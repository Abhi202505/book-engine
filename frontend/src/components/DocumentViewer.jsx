import React, { useState, useEffect } from 'react'
import { getDocumentParagraphs, searchDocuments } from '../api/client'
import '../styles/DocumentViewer.css'

function DocumentViewer({ bookId }) {
  const [paragraphs, setParagraphs] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState(null)
  const [viewMode, setViewMode] = useState('all')

  useEffect(() => {
    fetchDocument()
  }, [bookId])

  const fetchDocument = async () => {
    setLoading(true)
    setError('')
    try {
      const data = await getDocumentParagraphs(bookId)
      setParagraphs(data.paragraphs || [])
      setViewMode('all')
      setSearchResults(null)
    } catch (err) {
      setError(`Failed to load document: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = async (e) => {
    e.preventDefault()
    if (!searchQuery.trim()) {
      setSearchResults(null)
      setViewMode('all')
      return
    }

    setLoading(true)
    try {
      const results = await searchDocuments(bookId, searchQuery)
      setSearchResults(results.results || [])
      setViewMode('search')
    } catch (err) {
      setError(`Search failed: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }

  const displayItems = viewMode === 'search' ? searchResults : paragraphs

  if (loading && !paragraphs.length) {
    return <div className="loading">⏳ Loading document...</div>
  }

  return (
    <div className="viewer-container">
      <div className="viewer-controls">
        <form onSubmit={handleSearch} className="search-form">
          <input
            type="text"
            placeholder="🔍 Search document..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="search-input"
          />
          <button type="submit" className="search-button">Search</button>
          {searchResults && (
            <button
              type="button"
              onClick={() => {
                setSearchResults(null)
                setSearchQuery('')
                setViewMode('all')
              }}
              className="clear-search"
            >
              Clear
            </button>
          )}
        </form>
      </div>

      <div className="viewer-stats">
        <span>📊 Total Paragraphs: {paragraphs.length}</span>
        {searchResults && (
          <span className="search-count">🔎 Search Results: {searchResults.length}</span>
        )}
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="paragraphs-grid">
        {(!displayItems || displayItems.length === 0) ? (
          <div className="no-results">
            {searchResults !== null ? '❌ No search results found' : '📭 No paragraphs available'}
          </div>
        ) : (
          displayItems.map((item, index) => (
            <div key={index} className="paragraph-card">
              <div className="card-header">
                <span className="card-index">#{index + 1}</span>
                {item.page_number && (
                  <span className="page-badge">Page {item.page_number}</span>
                )}
                {item.similarity_score && (
                  <span className="similarity-badge">
                    Relevance: {(item.similarity_score * 100).toFixed(1)}%
                  </span>
                )}
              </div>
              
              <div className="card-content">
                {item.text && (
                  <>
                    <p className="paragraph-text">{item.text}</p>
                  </>
                )}
              </div>

              {item.metadata && Object.keys(item.metadata).length > 0 && (
                <div className="card-metadata">
                  <details>
                    <summary>📝 Metadata</summary>
                    <pre>{JSON.stringify(item.metadata, null, 2)}</pre>
                  </details>
                </div>
              )}

              {item.images && item.images.length > 0 && (
                <div className="card-images">
                  <p className="images-label">📸 Linked Images: {item.images.length}</p>
                  <div className="images-list">
                    {item.images.map((img, imgIdx) => (
                      <span key={imgIdx} className="image-tag">{img}</span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))
        )}
      </div>

      {displayItems && displayItems.length > 0 && (
        <div className="viewer-footer">
          <p>Showing {displayItems.length} of {paragraphs.length} paragraphs</p>
        </div>
      )}
    </div>
  )
}

export default DocumentViewer
