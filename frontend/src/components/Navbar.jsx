import React from "react";
import { Link } from "react-router-dom";

export default function Navbar() {
    return (
        <nav style={{
            backgroundColor: "#72a8ad",
            color: "white",
            padding: "3px 10px",
            display: "flex",
            justifyContent: "space-between"
        }}>
            <h2>Journey Map</h2>
            <div>
                <Link to="/" style={{ color: "white", textDecoration: "none", marginRight: "15px"}}>Home</Link>
            </div>
        </nav>
    );
}
