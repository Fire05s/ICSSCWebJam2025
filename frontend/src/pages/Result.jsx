/* This is the Page 2 after user clicked in Home page, contains Map + POI + sidebar */

import React, { useState } from "react";
import { useLocation } from "react-router-dom";
import MapView from "../components/MapView";
import Sidebar from "../components/Sidebar";
import DetailsModal from "../components/DetailsModal";
import "./Result.css";

export default function Result() {
    const { state } = useLocation(); // contains start/end data
    const [selectedPOI, setSelectedPOI] = useState(null);

    return (
        <div style={{ display: "flex", height: "100vh", position: "relative" }}>
            <Sidebar setSelectedPOI={setSelectedPOI} />
            <MapView start={state?.start} end={state?.end} setSelectedPOI={setSelectedPOI} />
            {selectedPOI && (
                <DetailsModal poi={selectedPOI} onClose={() => setSelectedPOI(null)} />
            )}
        </div>
    );
}