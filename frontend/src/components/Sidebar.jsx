import React from "react";
import "./sidebar.css"
import {useState} from "react"
const POIs = [];

export default function Sidebar({ setSelectedPOI, onPreferencesUpdated }) {
    const CATEGORY_OPTIONS = [
        "Food & Drink",
        "Lodging",
        "Entertainment & Landmarks",
        "Shopping",
        // "Services",
        // "Transportation",
        // "Cultural",
        // "Health",
    ]

    const [selectedCategories, setSelectedCategories] = useState([])
    const [deepseekInput, setCustomInput] = useState("")
    const [searchRadius, setSearchRadius] = useState("")
    const [isUpdating, setIsUpdating] = useState(false)
    const [updateMessage, setUpdateMessage] = useState("")

    const toggleCategory = (cat) => {
        setSelectedCategories((prev) =>
            prev.includes(cat) ? prev.filter((c) => c !== cat) : [...prev, cat]
        )
    }

    const handleUpdate = async () => {
        setIsUpdating(true)
        setUpdateMessage("")
        try {
            // Resolve backend base URL: prefer Vite env VITE_BACKEND_URL, otherwise default to local Django dev server
            const BACKEND_BASE = (typeof import.meta !== 'undefined' && import.meta.env && import.meta.env.VITE_BACKEND_URL)
                || 'http://127.0.0.1:8000'
            const endpoint = `${BACKEND_BASE.replace(/\/$/, '')}/api/preferences/`
            console.debug('POST preferences to', endpoint)
                // Send categories, custom input, and radius as separate fields
                const payload = { categories: selectedCategories }
                if (deepseekInput.trim()) payload.custom_input = deepseekInput.trim()
                if (searchRadius) payload.radius = searchRadius
                const resp = await fetch(endpoint, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload),
                })

            // Try to read JSON if available, otherwise read text for debugging
            let bodyText = null
            let bodyJson = null
            const contentType = resp.headers.get('content-type') || ''
            if (contentType.includes('application/json')) {
                try {
                    bodyJson = await resp.json()
                } catch (e) {
                    // fall through to text
                    bodyText = await resp.text()
                }
            } else {
                bodyText = await resp.text()
            }

            if (resp.ok) {
                setUpdateMessage('Preferences updated')
                return true
            } else {
                // Prefer JSON error field, then text, then status
                const errMsg = (bodyJson && (bodyJson.error || JSON.stringify(bodyJson))) || bodyText || `HTTP ${resp.status}`
                setUpdateMessage(errMsg)
                console.debug('update preferences failed', resp.status, errMsg)
                return false
            }
        } catch (err) {
            // Network-level error (DNS, CORS, refused connection, etc.)
            console.debug('update preferences network error', err)
            setUpdateMessage(err.message || 'Network error')
            return false
        } finally {
            setIsUpdating(false)
        }
    }
    return (
        <div style={{
            width: "430px",
            borderRight: "1px solid #ccc",
            overflowY: "auto",
            padding: "10px",
            backgroundColor: "var(--sidebar-bg-color)"
        }}>
            <h2>Points of Interest</h2>

            <div style={{marginBottom: '10px'}}>
                <div style={{marginBottom: '6px', fontWeight: 600}}>Choose Categories:</div>
                <div style={{display: 'flex', flexDirection: 'column', gap: '6px'}}>
                    {CATEGORY_OPTIONS.map((cat) => (
                        <label key={cat} style={{display: 'flex', alignItems: 'center', gap: '8px'}}>
                            <input
                                type="checkbox"
                                checked={selectedCategories.includes(cat)}
                                onChange={() => toggleCategory(cat)}
                            />
                            {cat}
                        </label>
                    ))}
                </div>

                <div style={{marginTop: '10px', fontWeight: 600}}>Search Radius (meters):</div>
                <div style={{marginTop: '6px', marginBottom: '8px'}}>
                    <input
                        type="number"
                        value={searchRadius}
                        onChange={e => setSearchRadius(e.target.value)}
                        placeholder="Default: 5000"
                        min="100"
                        style={{width: '90%', padding: '6px', fontSize: '1em'}}
                    />
                </div>

                <div style={{marginTop: '10px',  fontWeight: 600}}>(Optional) Describe the places you'd like to visit on your journey:</div>
                <div style={{marginTop: '12px', marginBottom: '8px'}}>
                    <input
                        type="text"
                        value={deepseekInput}
                        onChange={e => setCustomInput(e.target.value)}
                        placeholder="Tell DeepSeek..."
                        style={{width: '90%', padding: '6px', fontSize: '1em'}}
                    />
                </div>
                <div style={{marginTop: '8px'}}>
                    <button onClick={async () => {
                        setSelectedPOI(null); // close POI panel
                        const ok = await handleUpdate();
                        // notify parent so MapView can re-fetch only on success
                        if (ok && onPreferencesUpdated) onPreferencesUpdated();
                    }} disabled={isUpdating || (selectedCategories.length === 0 && !deepseekInput.trim())} className="clicker" type="button">
                        {isUpdating ? 'Updating...' : 'Update'}
                    </button>
                    <span style={{marginLeft: '8px'}}>{updateMessage}</span>
                </div>
            </div>

            {POIs.map((poi) => (
                <div
                    key={poi.id}
                    style={{ display: "flex", alignItems: "center", marginBottom: "10px", cursor: "pointer" }}
                    onClick={() => setSelectedPOI(poi)}
                >
                    <img src={poi.image} alt={poi.name} style={{ width: "50px", height: "50px", marginRight: "10px" }} />
                    <div>
                        <strong>{poi.name}</strong>
                        <p style={{ margin: 0, fontSize: "12px", color: "var(--sidebar-text-color)" }}>{poi.type}</p>
                    </div>
                </div>
            ))}
        </div>
    );
}

