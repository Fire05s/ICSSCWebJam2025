import React from "react";
import "sidebar.css"
const POIs = [
    { id: 1, name: "Art Museum", type: "landmark", image: "https://image" },
    { id: 2, name: "Sunset Café", type: "restaurant", image: "https://image" },
];

export default function Sidebar({ setSelectedPOI }) {
    return (
        <div style={{
            width: "430px",
            borderRight: "1px solid #ccc",
            overflowY: "auto",
            padding: "10px",
            backgroundColor: "#f8f8f8"
        }}>
            <h2>Points of Interest</h2>
            <div>
             <button type="button">Resturants</button>
            <button type="button">Landmarks</button>
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
                        <p style={{ margin: 0, fontSize: "12px", color: "#666" }}>{poi.type}</p>

                    </div>
                </div>
            ))}
        </div>
    );
}

