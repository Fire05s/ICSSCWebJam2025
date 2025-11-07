/* This is the page 1 for our web app, contains Start/End form + search button */

import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import LocationForm from "../components/LocationForm";

export default function Home() {
    const [formData, setFormData] = useState({ start: "", end: "" });
    const navigate = useNavigate();

    const handleSubmit = (e) => {
        e.preventDefault();
        // Validate start and end
        if (!formData.start.trim() || !formData.end.trim()) {
            alert("Please fill out both start and end locations.");
            return; // Stop navigation
        }
        navigate("/result", { state: formData });
    };

    return (
        <div style={{ textAlign: "center", minHeight: "100vh", position: "relative" }}>
            <div style={{ marginTop: "10vh" }}>
                <h1>Along the Way</h1>
                <p>Plan your route and explore restaurants along the way.</p>
                <LocationForm formData={formData} setFormData={setFormData} onSubmit={handleSubmit} />
            </div>
            <footer style={{
                fontSize: "0.8em",        
                color: "var(--credit-text-color)",     
                padding: "50px 0",
            }}>
                © 2025 ICSSC WebJam. All rights reserved.
            </footer>
        </div>
    );
}
