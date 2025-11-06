import React from "react";

export default function DetailsModal({ poi, onClose }) {
    return (
        <div style={{
            position: "absolute",
            top: "50%",
            left: "50%",
            transform: "translate(-50%, -50%)",
            backgroundColor: "white",
            padding: "20px",
            boxShadow: "0px 4px 10px rgba(0,0,0,0.2)",
            zIndex: 1000,
            borderRadius: "8px",
            minWidth: "300px"
        }}>
            <h3>{poi.name}</h3>
            <img src={poi.image || "https://image"} alt={poi.name} style={{ width: "100%" }} />
            <p>Type: {poi.type}</p>
            <p>Weather: Sunny (mock)</p>
            <p>Detour time: 10 mins</p>
            <button onClick={onClose} style={{ marginTop: "10px" }}>Close</button>
        </div>
    );
}
