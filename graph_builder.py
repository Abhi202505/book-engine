from neo4j import GraphDatabase
import json
import logging

class Neo4jIngestor:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def ingest_document(self, json_data: str):
        doc = json.loads(json_data)
        book_id = doc["book_id"]
        
        with self.driver.session() as session:
            # Create Book Node
            session.run("MERGE (b:Book {id: $book_id})", book_id=book_id)
            
            for page in doc["pages"]:
                for sec_idx, section in enumerate(page["sections"]):
                    sec_id = f"{book_id}_p{page['page_number']}_s{sec_idx}"
                    
                    # Create Section Node
                    session.run("""
                        MATCH (b:Book {id: $book_id})
                        MERGE (s:Section {id: $sec_id, title: $title})
                        MERGE (b)-[:CONTAINS]->(s)
                    """, book_id=book_id, sec_id=sec_id, title=section["title"])
                    
                    prev_block_id = None
                    for block in section["content"]:
                        block_id = block["id"]
                        
                        if block["type"] in ["paragraph", "equation"]:
                            session.run("""
                                MATCH (s:Section {id: $sec_id})
                                MERGE (p:Paragraph {id: $block_id, book_id: $book_id, text: $text, type: $type, page_number: $page_number})
                                MERGE (s)-[:CONTAINS]->(p)
                            """, sec_id=sec_id, block_id=block_id, book_id=book_id, text=block["text"], type=block["type"], page_number=page["page_number"])
                            
                            # Maintain sequential reading order in Graph
                            if prev_block_id:
                                session.run("""
                                    MATCH (prev:Paragraph {id: $prev_id})
                                    MATCH (curr:Paragraph {id: $curr_id})
                                    MERGE (prev)-[:NEXT]->(curr)
                                """, prev_id=prev_block_id, curr_id=block_id)
                            prev_block_id = block_id
                            
                        elif block["type"] == "image":
                            session.run("""
                                MERGE (i:Image {id: $block_id, caption: $caption, book_id: $book_id})
                            """, block_id=block_id, caption=block["caption"] or "", book_id=book_id)
                            
                            # Link image to paragraph
                            if block["linked_to"]:
                                session.run("""
                                    MATCH (p:Paragraph {id: $linked_id})
                                    MATCH (i:Image {id: $img_id})
                                    MERGE (p)-[:HAS_IMAGE]->(i)
                                """, linked_id=block["linked_to"], img_id=block_id)
        logging.info(f"Successfully ingested {book_id} into Neo4j")

    def query_paragraphs(self, book_id: str):
        """Query all paragraphs for a given book"""
        with self.driver.session() as session:
            query = """
            MATCH (p:Paragraph {book_id: $book_id})
            RETURN p.id as id, p.text as text, p.page_number as page_number, p.type as type
            ORDER BY p.page_number, p.id
            """
            results = session.run(query, book_id=book_id)
            return [dict(record) for record in results]