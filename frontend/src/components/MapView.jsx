import React, { useState, useEffect, useCallback } from "react";
import { GoogleMap, Marker, useLoadScript } from "@react-google-maps/api";
import "./MapView.css";

const containerStyle = { width: "100%", height: "100%" };

export default function MapView({ start, end, setSelectedPOI }) {
    const { isLoaded } = useLoadScript({
        googleMapsApiKey: import.meta.env.VITE_GOOGLE_MAPS_API_KEY,
    });

    const [center, setCenter] = useState({ lat: 33.6441, lng: -117.8452 });
    const [userLocation, setUserLocation] = useState(null);

    const locateUser = useCallback(() => {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    const coords = {
                        lat: position.coords.latitude,
                        lng: position.coords.longitude,
                    };
                    setCenter(coords);
                    setUserLocation(coords);
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
        locateUser();
    }, [locateUser]);

    const POIs = [
        { id: 1, name: "Art Museum", type: "landmark", lat: 33.6441, lng: -117.8400 },
        { id: 2, name: "Sunset Café", type: "restaurant", lat: 33.6441, lng: -117.8252 },
    ];

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

                {POIs.map((poi) => (
                    <Marker
                        key={poi.id}
                        position={{ lat: poi.lat, lng: poi.lng }}
                        onClick={(e) => {
                            e.domEvent.stopPropagation();
                            setSelectedPOI(poi);
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
