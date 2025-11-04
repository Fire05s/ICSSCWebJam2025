/* This is the Page 2 after user clicked in Home page, contains Map + POI + sidebar */

import React from "react";
import { useLocation } from "react-router-dom";
import MapView from "../components/MapView";
import Sidebar from "../components/Sidebar";
import DetailsModal from "../components/DetailsModal";

export default function Results() {
    const { state } = useLocation(); // contains start/end data
    return (
        <div className="results-page">
            <Sidebar />
            <MapView start={state?.start} end={state?.end} />
            <DetailsModal />
        </div>
    );
}