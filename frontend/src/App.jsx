import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Home from "./pages/Home.jsx";
import Result from "./pages/Result.jsx";
import Navbar from "./components/Navbar.jsx";

/**
 * Controls navigation with react-router
 */
export default function App() {
    return (
        <Router>
            <Navbar />
            <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/result" element={<Result />} />
            </Routes>
        </Router>
    );
}