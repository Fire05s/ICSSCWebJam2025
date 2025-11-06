import React, { useState, useEffect, useCallback, useRef } from "react";
import { GoogleMap, Marker, useLoadScript } from "@react-google-maps/api";
import "./MapView.css";

const containerStyle = { width: "100%", height: "100%" };

export default function MapView({ start, end, setSelectedPOI }) {
    const { isLoaded } = useLoadScript({
        googleMapsApiKey: import.meta.env.VITE_GOOGLE_MAPS_API_KEY,
    });

    const [center, setCenter] = useState({ lat: 33.6441, lng: -117.8452 });
    const [userLocation, setUserLocation] = useState(null);
    const [POIs, setPOIs] = useState([]);
    const mapRef = useRef(null); // Ref for the Google Map instance

    const onMapLoad = useCallback((map) => {
        mapRef.current = map;
    }, []);

    // Locate user
    const locateUser = useCallback(() => {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    const userCoords = {
                        lat: position.coords.latitude,
                        lng: position.coords.longitude,
                    };
                    setCenter(userCoords);
                    setUserLocation(userCoords);
                    // Smooth pan to user's location
                    if (mapRef.current) {
                        mapRef.current.panTo(userCoords);
                        mapRef.current.setZoom(14);
                    }
                },
                (error) => {
                    console.error("Error getting location:", error);
                    alert("Unable to fetch your location. Please allow access.");
                }
            );
        } else {
            alert("Geolocation not supported by your browser.");
        }
    }, []);

    useEffect(() => {
        // Auto-locate once on mount
        locateUser();
    }, [locateUser]);

    useEffect(() => {
        // Fetch route + places from backend
        if (start && end) {
            fetch(`http://127.0.0.1:8000/?start=${encodeURIComponent(start)}&destination=${encodeURIComponent(end)}&format=json`)
                .then((res) => res.json())
                .then((data) => {
                    if (data.route_polyline) {
                        setCenter(data.center);
                        const placesArray = Object.values(data.places).map(([lat, lng, name, color]) => ({
                            lat, lng, name, color
                        }));
                        setPOIs(placesArray);
                    } else {
                        console.error(data.error);
                    }
                })
                .catch(console.error);
        }
    }, [start, end]);

    if (!isLoaded) return <div>Loading map...</div>;

    return (
        <div className="map-wrapper">
            <GoogleMap
                mapContainerStyle={containerStyle}
                center={center}
                zoom={13}
                onClick={() => setSelectedPOI(null)}
            >
                {userLocation && (
                    <Marker
                        position={userLocation}
                        icon={{
                            path: window.google.maps.SymbolPath.CIRCLE,
                            scale: 8,
                            fillColor: "#4285F4",
                            fillOpacity: 1,
                            strokeWeight: 2,
                            strokeColor: "white",
                        }}
                    />
                )}

                {POIs.map((poi, index) => (
                    <Marker
                        key={index}
                        position={{ lat: poi.lat, lng: poi.lng }}
                        onClick={(e) => {
                            e.domEvent.stopPropagation();
                            setSelectedPOI(poi);
                        }}
                        icon={{
                            path: google.maps.SymbolPath.CIRCLE,
                            scale: 8,
                            fillColor: poi.color?.background || "#4285F4",
                            fillOpacity: 1,
                            strokeWeight: 2,
                            strokeColor: poi.color?.border || "#000",
                        }}
                    />
                ))}
            </GoogleMap>

            <button className="locate-btn" onClick={locateUser} title="Center map on my location">
                📍
            </button>
        </div>
    );
}
