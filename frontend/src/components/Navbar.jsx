import React from "react";
import { Link } from "react-router-dom";

export default function Navbar() {
    return (
        <nav style={{
            backgroundColor: "var(--nvbar-bg-color)",
            color: "white",
            padding: "3px 10px",
            display: "flex",
            justifyContent: "space-between"
        }}>
            <h2>Along the Way</h2>
            <div>
                <Link to="/" style={{ color: "white", textDecoration: "none", marginRight: "15px"}}>Home</Link>
            </div>
        </nav>
    );
}
