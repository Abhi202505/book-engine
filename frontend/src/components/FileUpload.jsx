import React, { useState } from 'react'
import { uploadPDF, getTaskStatus } from '../api/client'
import '../styles/FileUpload.css'

function FileUpload({ onUploadSuccess }) {
  const [file, setFile] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [processing, setProcessing] = useState(false)
  const [taskId, setTaskId] = useState(null)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [progress, setProgress] = useState(0)

  const handleFileChange = (e) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile && selectedFile.type === 'application/pdf') {
      setFile(selectedFile)
      setError('')
    } else {
      setError('Please select a valid PDF file')
      setFile(null)
    }
  }

  const pollTaskStatus = (id, bookId) => {
    const pollInterval = setInterval(async () => {
      try {
        const status = await getTaskStatus(id)
        
        if (status.status === 'PENDING') {
          setProgress(25)
        } else if (status.status === 'PROGRESS') {
          setProgress(75)
        } else if (status.status === 'SUCCESS') {
          setProgress(100)
          setMessage(`✅ Document processed successfully! (ID: ${bookId})`)
          setProcessing(false)
          clearInterval(pollInterval)
          setTimeout(() => {
            onUploadSuccess(bookId)
          }, 1000)
        } else if (status.status === 'FAILURE') {
          setError(`Processing failed: ${status.result || 'Unknown error'}`)
          setProcessing(false)
          clearInterval(pollInterval)
        }
      } catch (err) {
        console.log('Assuming still processing...')
        setProgress(50)
      }
    }, 2000)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!file) {
      setError('Please select a file')
      return
    }

    setUploading(true)
    setError('')
    setMessage('')
    setProgress(10)

    try {
      const response = await uploadPDF(file)
      const { book_id, task_id } = response
      
      setMessage(`Uploading ${file.name}...`)
      setProgress(20)
      setTaskId(task_id)
      setFile(null)
      setUploading(false)
      setProcessing(true)

      // StartPolling for task status
      pollTaskStatus(task_id, book_id)
    } catch (err) {
      setError(err.message)
      setUploading(false)
    }
  }

  return (
    <div className="upload-container">
      <div className="upload-box">
        <h2>Upload PDF Document</h2>
        <p className="subtitle">Your document will be parsed, embedded, and stored for analysis</p>

        <form onSubmit={handleSubmit}>
          <div className="file-input-wrapper">
            <input
              type="file"
              accept=".pdf"
              onChange={handleFileChange}
              disabled={uploading || processing}
              id="pdf-input"
            />
            <label htmlFor="pdf-input" className="file-label">
              {file ? `✓ ${file.name}` : '📁 Click to select PDF'}
            </label>
          </div>

          <button
            type="submit"
            disabled={!file || uploading || processing}
            className="upload-button"
          >
            {uploading ? '⏳ Uploading...' : processing ? '🔄 Processing...' : '🚀 Upload & Process'}
          </button>
        </form>

        {progress > 0 && (
          <div className="progress-container">
            <div className="progress-bar">
              <div className="progress-fill" style={{ width: `${progress}%` }}></div>
            </div>
            <p className="progress-text">{progress}% Complete</p>
          </div>
        )}

        {message && <div className="message success">{message}</div>}
        {error && <div className="message error">{error}</div>}

        <div className="info-box">
          <h3>📋 Processing Information</h3>
          <ul>
            <li>Extracts text, layout, and images from PDF</li>
            <li>Generates embeddings for semantic search</li>
            <li>Stores in Neo4j graph database</li>
            <li>Indexes vectors in Qdrant</li>
          </ul>
        </div>
      </div>
    </div>
  )
}

export default FileUpload
