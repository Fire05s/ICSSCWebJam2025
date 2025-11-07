import React, { useState, useEffect, useCallback, useRef } from "react";
import { GoogleMap, Marker, Polyline, useLoadScript } from "@react-google-maps/api";
import polyline from "@mapbox/polyline";
import "./MapView.css";

const containerStyle = { width: "100%", height: "100%" };
const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

// Initial Default Center (used as a fallback if geolocation fails)
const FALLBACK_CENTER = { lat: 33.6441, lng: -117.8452 }; // E.g., Irvine, CA

// Define dot color here
const color = {
    "Food & Drink": "#FF8C8C",
    "Lodging": "#4ECDC4",
    "Entertainment & Landmarks": "#FFD93D",
    "Shopping": "#6A4C93",
    // "Services": "#95A5A6",
    // "Transportation": "#3498DB",
    // "Cultural": "#E67E22",
    // "Health": "#FF1900"
};

// Helper: Validate LatLng
const isValidLatLng = (coord) =>
    coord &&
    typeof coord.lat === "number" &&
    typeof coord.lng === "number" &&
    isFinite(coord.lat) &&
    isFinite(coord.lng);

// Helper function to safely process coordinates
const processCoords = (coords) => {
    if (!coords) return null;
    if (Array.isArray(coords) && coords.length === 2) {
        return { lat: Number(coords[0]), lng: Number(coords[1]) };
    }
    else if (coords.lat && typeof coords.lat === 'string') {
        return { lat: Number(coords.lat), lng: Number(coords.lng) };
    }
    else if (isValidLatLng(coords)) {
        return coords;
    }
    return null;
};

export default function MapView({ start, end, setSelectedPOI, preferencesVersion=0 }) {
    const { isLoaded } = useLoadScript({
        googleMapsApiKey: import.meta.env.VITE_GOOGLE_MAPS_API_KEY,
    });

    const mapRef = useRef(null);
    const hasFitBounds = useRef(false);

    // To store the user's fetched location
    const [defaultCenter, setDefaultCenter] = useState(FALLBACK_CENTER);
    const [route, setRoute] = useState([]);
    const [POIs, setPOIs] = useState([]);
    const [startCoords, setStartCoords] = useState(null);
    const [destCoords, setDestCoords] = useState(null);
    const [isLoading, setIsLoading] = useState(false); // Track map route loading

    const onMapLoad = useCallback((map) => {
        mapRef.current = map;
    }, []);

    // Fetch User Location on Mount
    useEffect(() => {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    setDefaultCenter({
                        lat: position.coords.latitude,
                        lng: position.coords.longitude,
                    });
                },
                // On error (user denies, timeout, etc.), fall back to FALLBACK_CENTER
                (error) => {
                    console.warn("Geolocation Error:", error.message);
                },
                { enableHighAccuracy: true, timeout: 5000, maximumAge: 0 }
            );
        }
    }, []); // Empty dependency array means this runs only once on mount

    // Fetch route and POIs
    useEffect(() => {
        if (!start || !end) return;

        hasFitBounds.current = false;

        setIsLoading(true); // Show loading overlay while fetching data

        // Prefer explicit env var VITE_BACKEND_URL in dev; fall back to localhost:8000 if not set
        const BACKEND_BASE = (typeof import.meta !== 'undefined' && import.meta.env && import.meta.env.VITE_BACKEND_URL)
            || 'http://127.0.0.1:8000';
        const endpoint = `${BACKEND_BASE.replace(/\/$/, '')}/?start=${encodeURIComponent(start)}&destination=${encodeURIComponent(end)}&format=json`;
        console.debug('Fetching route from', endpoint);

        const controller = new AbortController();
        // Increase timeout to 60s to allow the backend more time when many filters are selected
        const timeout = setTimeout(() => controller.abort(), 60000); // 60s timeout

        fetch(endpoint, { signal: controller.signal })
            .then((res) => {
                if (!res.ok) {
                    // Try to get any text for debugging
                    return res.text().then((t) => { throw new Error(`HTTP ${res.status}: ${t.slice(0,200)}`); });
                }
                const contentType = res.headers.get('content-type') || '';
                if (contentType.includes('application/json')) return res.json();
                return res.text().then((t) => { throw new Error(`Expected JSON but got: ${t.slice(0,200)}`); });
            })
            .then((data) => {
                console.debug('route response filters_used:', data.filters_used, 'applied_filters:', data.applied_filters, 'places_count:', Object.keys(data.places || {}).length)
                if (!data || !data.route_polyline) throw new Error('No route data');

                const decodedRoute = polyline.decode(data.route_polyline).map(([lat, lng]) => ({ lat, lng }));
                const placesArray = Object.values(data.places || {}).map(
                    ([lat, lng, name, color, rating, user_ratings_total, photo_url, weather]) => 
                        ({ lat, lng, name, color, rating, user_ratings_total, photo_url, weather}));
                const finalStart = processCoords(data.start_coords);
                const finalDest = processCoords(data.dest_coords);

                // Batch State Updates
                setRoute(decodedRoute);
                setPOIs(placesArray);
                setStartCoords(finalStart);
                setDestCoords(finalDest);
            })
            .catch((err) => {
                if (err.name === 'AbortError') console.error('Route fetch aborted (timeout)');
                else console.error('Route fetch error', err);
                // reset route/pois to avoid stale UI
                setRoute([]);
                setPOIs([]);
                setStartCoords(null);
                setDestCoords(null);
            })
            .finally(() => {
                clearTimeout(timeout);
                setIsLoading(false);
            }); // Hide loading overlay after done or error

        return () => {
            controller.abort();
            clearTimeout(timeout);
        };
    }, [start, end, preferencesVersion]);

    // Fit bounds only once when route data is ready
    useEffect(() => {
        if (mapRef.current && isValidLatLng(startCoords) && isValidLatLng(destCoords) && !hasFitBounds.current) {

            const bounds = new window.google.maps.LatLngBounds();
            bounds.extend(startCoords);
            bounds.extend(destCoords);

            POIs.forEach((poi) => {
                if (isValidLatLng(poi)) bounds.extend(poi);
            });

            mapRef.current.fitBounds(bounds);
            hasFitBounds.current = true;
        }
    }, [startCoords, destCoords, POIs]);

    // Helper to check if the center is the fallback 
    const isUserLocationLoaded = defaultCenter.lat !== FALLBACK_CENTER.lat || defaultCenter.lng !== FALLBACK_CENTER.lng;
    
    if (!isLoaded) return <div>Loading map...</div>;

    return (
        <div className="map-wrapper">
            {isLoading && (
                <div className="map-loading-overlay">
                    <div className="spinner"></div>
                    <p>Calculating route...</p>
                </div>
            )}
            <GoogleMap
                mapContainerClassName="map-container"
                mapContainerStyle={containerStyle}
                // Set initial center to the user's location state
                center={defaultCenter}
                zoom={13}
                onLoad={onMapLoad}
                onClick={() => setSelectedPOI(null)}
            >
                {/* Use defaultCenter for the position, and only render if not the fallback */}
                {isUserLocationLoaded && (
                    <Marker
                        position={defaultCenter} // Corrected variable
                        icon={{
                            path: window.google.maps.SymbolPath.CIRCLE,
                            scale: 8,
                            fillColor: "#4285F4", // Google Blue
                            fillOpacity: 1,
                            strokeWeight: 2,
                            strokeColor: "white",
                        }}
                    />
                )}

                {/* Route */}
                {route.length > 0 && (
                    <Polyline
                        path={route}
                        options={{ strokeColor: "#4285F4", strokeOpacity: 0.8, strokeWeight: 5 }}
                    />
                )}

                {/* POIs */}
                {POIs.map((poi, idx) => (
                    <Marker
                        key={idx}
                        position={{ lat: poi.lat, lng: poi.lng }}
                        onClick={(e) => { e.domEvent.stopPropagation(); setSelectedPOI(poi); }}
                        icon={{
                            path: window.google.maps.SymbolPath.CIRCLE,
                            scale: 8,
                            fillColor: poi.color?.background || "#4285F4",
                            fillOpacity: 1,
                            strokeWeight: 2,
                            strokeColor: poi.color?.border || "#000",
                        }}
                    />
                ))}
            </GoogleMap>
            
            {/* Add dot color box*/}
            <div className="dot-color">
                {Object.entries(color).map(([label, color]) => (
                    <div key={label} className="color-item">
                        <span className="color-dot" style={{ backgroundColor: color }}></span>
                        {label}
                    </div>
                ))}
            </div>
        </div>
    );
}