import React from "react";
import { Link } from "react-router-dom";

export default function Navbar() {
    return (
        <nav style={{
            backgroundColor: "#222",
            color: "white",
            padding: "10px 20px",
            display: "flex",
            justifyContent: "space-between"
        }}>
            <h3>Journey Map</h3>
            <div>
                <Link to="/" style={{ color: "white", textDecoration: "none", marginRight: "15px" }}>Home</Link>
                <Link to="/result" style={{ color: "white", textDecoration: "none" }}>Result</Link>
            </div>
        </nav>
    );
}
