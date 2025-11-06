import React from "react";
import { GoogleMap, Marker, useLoadScript } from "@react-google-maps/api";

const containerStyle = { width: "100%", height: "100%" };

export default function MapView({ start, end, setSelectedPOI }) {
    const { isLoaded } = useLoadScript({
        googleMapsApiKey: import.meta.env.VITE_GOOGLE_MAPS_API_KEY,
    });

    const POIs = [
        { id: 1, name: "Art Museum", type: "landmark", lat: 37.7749, lng: -122.4194 },
        { id: 2, name: "Sunset Café", type: "restaurant", lat: 37.7849, lng: -122.4094 },
    ];

    if (!isLoaded) return <div>Loading map...</div>;

    return (
        <GoogleMap
            mapContainerStyle={containerStyle}
            center={{ lat: 37.7749, lng: -122.4194 }}
            zoom={13}
        >
            {POIs.map((poi) => (
                <Marker
                    key={poi.id}
                    position={{ lat: poi.lat, lng: poi.lng }}
                    onClick={() => setSelectedPOI(poi)}
                />
            ))}
        </GoogleMap>
    );
}
