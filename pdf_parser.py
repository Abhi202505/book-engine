import pdfplumber
import uuid
import base64
import numpy as np
import logging
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from sklearn.cluster import KMeans
from PIL import Image
import io

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Pydantic Data Models (Strict Output Schema) ---

class ContentBlock(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str  # "paragraph", "heading", "image", "table", "equation"
    text: Optional[str] = None
    base64: Optional[str] = None
    caption: Optional[str] = None
    linked_to: Optional[str] = None
    embedding_ready: bool = False
    bbox: Optional[List[float]] = None # [x0, y0, x1, y1] kept for internal graph linking

class Section(BaseModel):
    title: str
    content: List[ContentBlock]

class PageDef(BaseModel):
    page_number: int
    sections: List[Section]

class DocumentOutput(BaseModel):
    book_id: str
    pages: List[PageDef]

# --- Core Parser ---

class PDFLayoutParser:
    def __init__(self, pdf_path: str, book_id: str):
        self.pdf_path = pdf_path
        self.book_id = book_id
        self.doc = pdfplumber.open(pdf_path)
        self.output = DocumentOutput(book_id=self.book_id, pages=[])
        
    def _is_header_footer(self, bbox: tuple, page_height: float) -> bool:
        """Filter out running heads and page numbers."""
        y0, x0, y1, x1 = bbox  # pdfplumber uses (x0, y0, x1, y1) format
        return y1 < (page_height * 0.08) or y0 > (page_height * 0.92)

    def _get_median_font_size(self, blocks: List[dict]) -> float:
        sizes = [b.get("size", 11) for b in blocks]
        return np.median(sizes) if sizes else 11.0

    def _cluster_columns(self, blocks: List[dict]) -> List[List[dict]]:
        """Cluster blocks into columns based on their X-centers."""
        if not blocks: return []
        if len(blocks) == 1: return [blocks]

        x_centers = np.array([[(b["bbox"][0] + b["bbox"][2]) / 2] for b in blocks])
        
        # Determine if 1 or 2 columns based on variance of X centers
        variance = np.var(x_centers)
        n_clusters = 2 if variance > 5000 else 1

        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10).fit(x_centers)
        
        # Sort clusters left to right
        cluster_centers = kmeans.cluster_centers_.flatten()
        sorted_labels = np.argsort(cluster_centers)
        
        columns = [[] for _ in range(n_clusters)]
        for i, label in enumerate(kmeans.labels_):
            sorted_idx = int(np.where(sorted_labels == label)[0][0])
            columns[sorted_idx].append(blocks[i])
            
        for col in columns:
            col.sort(key=lambda x: x["bbox"][1])
            
        return columns

    def _reconstruct_reading_order(self, blocks: List[dict], page_width: float) -> List[dict]:
        """Spatial Banding Algorithm for complex/mixed layouts."""
        ordered_blocks = []
        current_band = []
        
        # FIXED: Sort all blocks purely by Y coordinate initially (index 1)
        blocks.sort(key=lambda b: b["bbox"])
        
        for block in blocks:
            x0, y0, x1, y1 = block["bbox"]
            block_width = x1 - x0
            is_spanning = block_width > (page_width * 0.65)
            
            if is_spanning:
                # Flush current multi-column band
                if current_band:
                    columns = self._cluster_columns(current_band)
                    for col in columns:
                        ordered_blocks.extend(col)
                    current_band = []
                # Add spanning block
                ordered_blocks.append(block)
            else:
                current_band.append(block)
                
        # Flush remaining
        if current_band:
            columns = self._cluster_columns(current_band)
            for col in columns:
                ordered_blocks.extend(col)
                
        return ordered_blocks

    def _extract_image_base64(self, page, bbox: tuple) -> str:
        """Extracts region of page as base64 image (simplified for pdfplumber)."""
        # For now, return empty string - image extraction would need more complex implementation
        return ""

    def parse(self) -> str:
        """Main execution pipeline."""
        for page_num, page in enumerate(self.doc.pages):
            # Extract text and layout information using pdfplumber
            page_width = page.width
            page_height = page.height

            # Get text with bounding boxes
            words = page.extract_words()

            # Convert words to block-like structure
            raw_blocks = []
            current_block = None
            current_y = None
            line_tolerance = 5  # pixels

            for word in words:
                word_bbox = (word['x0'], word['top'], word['x1'], word['bottom'])

                if current_block is None or abs(word['top'] - current_y) > line_tolerance:
                    if current_block:
                        raw_blocks.append(current_block)
                    current_block = {
                        'bbox': word_bbox,
                        'text': word['text'],
                        'size': word.get('size', 11),
                        'type': 0  # text
                    }
                    current_y = word['top']
                else:
                    # Extend current block
                    current_block['text'] += ' ' + word['text']
                    current_block['bbox'] = (
                        min(current_block['bbox'][0], word_bbox[0]),
                        min(current_block['bbox'][1], word_bbox[1]),
                        max(current_block['bbox'][2], word_bbox[2]),
                        max(current_block['bbox'][3], word_bbox[3])
                    )

            if current_block:
                raw_blocks.append(current_block)

            # 1. Clean & Filter Blocks
            valid_blocks = []
            for b in raw_blocks:
                if self._is_header_footer(b["bbox"], page_height):
                    continue
                valid_blocks.append(b)

            if not valid_blocks:
                continue

            median_size = self._get_median_font_size(valid_blocks)

            # 2. Layout Reconstruction
            ordered_blocks = self._reconstruct_reading_order(valid_blocks, page_width)

            # 3. Semantic Classification & Output Generation
            current_section_title = "Introduction" if page_num == 0 else "Continued"
            current_content = []
            sections = []
            images_awaiting_link = []
            last_paragraph_id = None

            for b in ordered_blocks:
                text = b.get("text", "").strip()
                if not text:
                    continue

                # Simple heading detection based on size
                font_size = b.get("size", 11)
                is_heading = font_size > median_size * 1.2

                if is_heading:
                    # Save previous section
                    if current_content:
                        sections.append({
                            "title": current_section_title,
                            "content": current_content
                        })

                    current_section_title = text[:50]  # Limit title length
                    current_content = []
                else:
                    # Regular paragraph
                    para_block = ContentBlock(
                        type="paragraph",
                        text=text,
                        bbox=b["bbox"]
                    )
                    current_content.append(para_block)
                    last_paragraph_id = para_block.id

            # Save final section
            if current_content:
                sections.append({
                    "title": current_section_title,
                    "content": current_content
                })

            # Create page definition
            page_def = PageDef(
                page_number=page_num + 1,
                sections=sections
            )
            self.output.pages.append(page_def)

        self.doc.close()
        return self.output.model_dump_json()