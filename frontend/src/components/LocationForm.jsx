import React from "react";

export default function LocationForm({ formData, setFormData, onSubmit }) {
    return (
        <form onSubmit={onSubmit} style={{ marginTop: "20px" }}>
            <input
                type="text"
                placeholder="Start location"
                value={formData.start}
                onChange={(e) => setFormData({ ...formData, start: e.target.value })}
                style={{ padding: "10px", margin: "5px" }}
            />
            <input
                type="text"
                placeholder="End location"
                value={formData.end}
                onChange={(e) => setFormData({ ...formData, end: e.target.value })}
                style={{ padding: "10px", margin: "5px" }}
            />
            <button type="submit" style={{ padding: "10px 20px", margin: "5px" }}>
                Search
            </button>
        </form>
    );
}
