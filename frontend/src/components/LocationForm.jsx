import React from "react";

/* This is a reusable form component for start & end locations*/ 
export default function LocationForm({ formData, setFormData, onSubmit }) {
    return (
        <form onSubmit={onSubmit} style={{ marginTop: "50px" }}>
            <input
                type="text"
                placeholder="Start location"
                value={formData.start}
                onChange={(e) => setFormData({ ...formData, start: e.target.value })}
                style={{ padding: "15px", margin: "10px" }}
            />
            <input
                type="text"
                placeholder="End location"
                value={formData.end}
                onChange={(e) => setFormData({ ...formData, end: e.target.value })}
                style={{ padding: "15px", margin: "10px" }}
            />
            <button type="submit" style={{ padding: "15px 40px", margin: "10px" }}>
                Search
            </button>
        </form>
    );
}
