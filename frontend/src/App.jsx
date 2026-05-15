import { useState, useRef } from 'react'
import './App.css'

const CITIES = [
  { value: 'barcelona', label: 'Barcelona' },
  { value: 'lisbon', label: 'Lisbon' },
  { value: 'amsterdam', label: 'Amsterdam' },
]

function App() {
  const [file, setFile] = useState(null)
  const [city, setCity] = useState('barcelona')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [favorites, setFavorites] = useState(new Set())
  const fileInputRef = useRef(null)

  const cityLabel = CITIES.find(c => c.value === city)?.label || city

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0]
    if (selectedFile) {
      setFile(selectedFile)
      setResults([])
      setError(null)
    }
  }

  const handleDrop = (event) => {
    event.preventDefault()
    event.currentTarget.classList.remove('dragging')
    const droppedFile = event.dataTransfer.files[0]
    if (droppedFile && droppedFile.type.startsWith('image/')) {
      setFile(droppedFile)
      setResults([])
      setError(null)
    }
  }

  const handleDragOver = (event) => {
    event.preventDefault()
    event.currentTarget.classList.add('dragging')
  }

  const handleDragLeave = (event) => {
    event.currentTarget.classList.remove('dragging')
  }

  const triggerFileInput = () => fileInputRef.current?.click()

  const handleSearch = async () => {
    if (!file) return
    setLoading(true)
    setError(null)
    setResults([])

    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await fetch(
        `http://localhost:8000/search?city=${city}&top_k=10`,
        { method: 'POST', body: formData }
      )

      if (!response.ok) {
        throw new Error(`Server responded ${response.status}`)
      }

      const data = await response.json()
      setResults(data.results)
    } catch (err) {
      setError(err.message || 'Something went wrong. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const resetFile = (e) => {
    e.stopPropagation()
    setFile(null)
    setResults([])
    setError(null)
    if (fileInputRef.current) fileInputRef.current.value = ''
  }

  const openListing = (url) => {
    window.open(url, '_blank', 'noopener,noreferrer')
  }

  const toggleFavorite = (e, listingId) => {
    e.stopPropagation()
    setFavorites(prev => {
      const next = new Set(prev)
      if (next.has(listingId)) next.delete(listingId)
      else next.add(listingId)
      return next
    })
  }

  const handleCardKey = (e, url) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault()
      openListing(url)
    }
  }

  return (
    <div className="app">
      <nav className="navbar" aria-label="Main navigation">
        <div className="navbar-inner">
          <div className="brand">
            <svg className="brand-icon" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
              <path d="M12 2C9.24 2 7 4.24 7 7c0 1.66.83 3.12 2.09 4.01C7.84 12.17 7 13.99 7 16c0 2.76 2.24 5 5 5s5-2.24 5-5c0-2.01-.84-3.83-2.09-4.99C16.17 10.12 17 8.66 17 7c0-2.76-2.24-5-5-5z"/>
            </svg>
            <span>Vibe</span>
          </div>
        </div>
      </nav>

      <main className="main">
        <header className="header">
          <h1>Find your <span>vibe</span></h1>
          <p>Upload a photo to find Airbnb listings with a similar vibe.</p>
        </header>

        <section className="search-card" aria-label="Search controls">
          <div className="field">
            <label htmlFor="city-select">Destination</label>
            <select
              id="city-select"
              className="select"
              value={city}
              onChange={(e) => setCity(e.target.value)}
            >
              {CITIES.map(c => (
                <option key={c.value} value={c.value}>{c.label}</option>
              ))}
            </select>
          </div>

          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleFileChange}
            style={{ display: 'none' }}
            aria-label="Upload an image"
          />

          {!file ? (
            <div
              className="dropzone"
              onClick={triggerFileInput}
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => (e.key === 'Enter' || e.key === ' ') && triggerFileInput()}
            >
              <svg className="dropzone-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" aria-hidden="true">
                <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
              </svg>
              <div className="dropzone-text">
                <strong>Click to upload</strong> or drag and drop
              </div>
              <div className="dropzone-hint">PNG, JPG, or any image</div>
            </div>
          ) : (
            <div className="preview">
              <img src={URL.createObjectURL(file)} alt="Selected preview" className="preview-img" />
              <div className="preview-info">
                <div className="preview-filename" title={file.name}>{file.name}</div>
                <button className="link-btn" onClick={resetFile}>Choose a different image</button>
              </div>
              <button
                type="button"
                className="search-btn"
                onClick={handleSearch}
                disabled={loading}
              >
                {loading ? (
                  <>
                    <span className="spinner" aria-hidden="true"></span>
                    <span>Searching…</span>
                  </>
                ) : (
                  <span>Search {cityLabel}</span>
                )}
              </button>
            </div>
          )}
        </section>

        {error && (
          <div className="error" role="alert"
          >
            <strong>Error:</strong> {error}
          </div>
        )}

        {loading && (
          <section className="results" aria-live="polite" aria-busy="true">
            <div className="results-header">
              <h2>Searching {cityLabel}...</h2>
            </div>
            <div className="results-grid">
              {Array.from({ length: 10 }).map((_, i) => (
                <div key={i} className="listing-card skeleton">
                  <div className="skeleton-photo"></div>
                  <div className="listing-info">
                    <div className="skeleton-line skeleton-line-1"></div>
                    <div className="skeleton-line skeleton-line-2"></div>
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

        {!loading && results.length > 0 && (
          <section className="results" aria-live="polite">
            <div className="results-header">
              <h2>Top matches in {cityLabel}</h2>
              <span className="results-count">{results.length} listings</span>
            </div>
            <div className="results-grid">
              {results.map((listing) => {
                const isFav = favorites.has(listing.listing_id)
                return (
                  <article
                    key={listing.listing_id}
                    className="listing-card"
                    onClick={() => openListing(listing.url)}
                    onKeyDown={(e) => handleCardKey(e, listing.url)}
                    role="button"
                    tabIndex={0}
                  >
                    <div className="listing-photo-wrap">
                      <img
                        src={listing.photo_url}
                        alt={listing.name || 'Listing photo'}
                        className="listing-photo"
                        loading="lazy"
                      />
                      <button
                        className={`heart-btn ${isFav ? 'is-favorited' : ''}`}
                        onClick={(e) => toggleFavorite(e, listing.listing_id)}
                        aria-label={isFav ? 'Remove from favorites' : 'Add to favorites'}
                      >
                        <svg viewBox="0 0 32 32" aria-hidden="true">
                          <path d="M16 28.7l-1.5-1.4C7.1 20.8 2 16.3 2 10.8 2 6.4 5.4 3 9.8 3c2.5 0 4.9 1.2 6.2 3.1C17.3 4.2 19.7 3 22.2 3 26.6 3 30 6.4 30 10.8c0 5.5-5.1 10-12.5 16.5L16 28.7z"/>
                        </svg>
                      </button>
                      <span className="match-badge">{(listing.score * 100).toFixed(0)}% match</span>
                    </div>
                    <div className="listing-info">
                      <h3 className="listing-name">{listing.name || 'Unnamed listing'}</h3>
                      <div className="listing-meta">
                        <span>{listing.neighbourhood || '-'}</span>
                      </div>
                    </div>
                  </article>
                )
              })}
            </div>
          </section>
        )}

        {!file && !loading && results.length === 0 && !error && (
          <div className="empty">
            <h3>Ready to find your vibe?</h3>
            <p>Upload a photo above to start searching.</p>
          </div>
        )}
      </main>
    </div>
  )
}

export default App