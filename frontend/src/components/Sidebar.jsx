import React from "react";
import "./sidebar.css"
import {useState} from "react"
const POIs = [
    { id: 1, name: "Art Museum", type: "landmark", image: "https://image" },
    { id: 2, name: "Sunset Café", type: "restaurant", image: "https://image" },
];

export default function Sidebar({ setSelectedPOI }) {
    const [
        POIType,setPOIType
    ]=useState("Resturants")
    return (
        <div style={{
            width: "430px",
            borderRight: "1px solid #ccc",
            overflowY: "auto",
            padding: "10px",
            backgroundColor: "var(--sidebar-bg-color)"
        }}>
            <h2>Points of Interest</h2>
 
            <div>
             <button onClick={()=>setPOIType("Resturants")}type="button"className="clicker">Resturants</button>
            <button onClick={()=>setPOIType("Landmarks")}type="button"className=" clicker">Landmarks</button>
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
<<<<<<< HEAD
                        <p style={{ margin: 0, fontSize: "12px", color: "#666" }}>{poi.type}</p>

=======
                        <p style={{ margin: 0, fontSize: "12px", color: "var(--sidebar-text-color)" }}>{poi.type}</p>
>>>>>>> 52f80eb417d09f1a7d33fb7755faf2ff5cc6bf64
                    </div>
                </div>
            ))}
        </div>
    );
}

