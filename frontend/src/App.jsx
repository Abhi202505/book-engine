import React, { useState } from 'react'
import FileUpload from './components/FileUpload'
import DocumentViewer from './components/DocumentViewer'
import './styles/App.css'

function App() {
  const [selectedBookId, setSelectedBookId] = useState(null)
  const [uploadedBooks, setUploadedBooks] = useState([])
  const [activeTab, setActiveTab] = useState('upload')

  const handleUploadSuccess = (bookId) => {
    setUploadedBooks([...uploadedBooks, bookId])
    setSelectedBookId(bookId)
    setActiveTab('viewer')
  }

  return (
    <div className="app-container">
      <header className="header">
        <h1>📄 PDF Document Intelligence</h1>
        <p>Upload, Parse, and Explore Your Documents</p>
      </header>

      <div className="tabs">
        <button
          className={`tab-button ${activeTab === 'upload' ? 'active' : ''}`}
          onClick={() => setActiveTab('upload')}
        >
          📤 Upload Document
        </button>
        <button
          className={`tab-button ${activeTab === 'viewer' ? 'active' : ''}`}
          onClick={() => setActiveTab('viewer')}
          disabled={uploadedBooks.length === 0}
        >
          📖 View Documents ({uploadedBooks.length})
        </button>
      </div>

      <main className="main-content">
        {activeTab === 'upload' && (
          <div className="content-section">
            <FileUpload onUploadSuccess={handleUploadSuccess} />
          </div>
        )}

        {activeTab === 'viewer' && uploadedBooks.length > 0 && (
          <div className="content-section">
            <div className="viewer-header">
              <h2>Document Library</h2>
              <select
                className="book-selector"
                value={selectedBookId || ''}
                onChange={(e) => setSelectedBookId(e.target.value)}
              >
                <option value="">Select a document...</option>
                {uploadedBooks.map((bookId) => (
                  <option key={bookId} value={bookId}>
                    {bookId}
                  </option>
                ))}
              </select>
            </div>
            {selectedBookId && <DocumentViewer bookId={selectedBookId} />}
          </div>
        )}
      </main>

      <footer className="footer">
        <p>Powered by Neo4j, Qdrant & Advanced PDF Parsing</p>
      </footer>
    </div>
  )
}

export default App
