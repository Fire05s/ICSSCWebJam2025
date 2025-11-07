/* This is the Page 2 after user clicked in Home page, contains Map + POI + sidebar */

import React, { useState } from "react";
import { useLocation, Navigate } from "react-router-dom";
import MapView from "../components/MapView";
import Sidebar from "../components/Sidebar";
import DetailsModal from "../components/DetailsModal";
import "./Result.css";

export default function Result() {
    const { state } = useLocation(); // contains start/end data
    const [selectedPOI, setSelectedPOI] = useState(null);
    const [preferencesVersion, setPreferencesVersion] = useState(0);

    if (!state) {
        return (
            <div>
                <p>Redirecting to Home...</p>
                <Navigate to="/" replace />
            </div>
        );
    }
    return (
        <div className="result-container">
            <Sidebar setSelectedPOI={setSelectedPOI} onPreferencesUpdated={() => setPreferencesVersion((v) => v + 1)} />
            <MapView start={state?.start} end={state?.end} setSelectedPOI={setSelectedPOI} preferencesVersion={preferencesVersion} />
            {selectedPOI && (
                <DetailsModal poi={selectedPOI}  />
            )}
        </div>
    );
}