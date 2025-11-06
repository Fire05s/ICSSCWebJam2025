/* This is the page 1 for our web app, contains Start/End form + search button */

import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import LocationForm from "../components/LocationForm";

export default function Home() {
    const [formData, setFormData] = useState({ start: "", end: "" });
    const navigate = useNavigate();

    const handleSubmit = (e) => {
        e.preventDefault();
        navigate("/result", { state: formData });
    };

    return (
        <div style={{ textAlign: "center", marginTop: "10vh" }}>
            <h1>Journey Map</h1>
            <p>Plan your route and explore landmarks & restaurants along the way.</p>
            <LocationForm formData={formData} setFormData={setFormData} onSubmit={handleSubmit} />
        </div>
    );
}
