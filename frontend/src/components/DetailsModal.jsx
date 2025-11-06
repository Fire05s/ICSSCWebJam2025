import React from "react";
import "./DetailsModal.css";

export default function DetailsModal({ poi, onClose }) {
    return (
        <div className="details-modal">
            <h3>{poi.name}</h3>
            <img src={poi.image || "https://image"} alt={poi.name} />
            <p>Type: {poi.type}</p>
            <p>Weather: Sunny (mock)</p>
            <p>Detour time: 10 mins</p>
        </div>
    );
}
