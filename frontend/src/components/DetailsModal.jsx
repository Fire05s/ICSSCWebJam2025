import React from "react";
import "./DetailsModal.css";

export default function DetailsModal({ poi, onClose }) {
    if (!poi) return null;

    const {
        name,
        photo_url,
        rating,
        user_ratings_total,
        weather,
    } = poi;

    // Map weather code → readable text
    const getWeatherDescription = (code) => {
        if (!code && code !== 0) return "Unknown";
        if (code === 0) return "Clear sky";
        if ([1].includes(code)) return "Mainly clear";
        if ([2].includes(code)) return "Partly cloudy";
        if ([3].includes(code)) return "Overcast";
        if ([45, 48].includes(code)) return "Foggy";
        if ([51, 53, 55].includes(code)) return "Drizzle";
        if ([61, 63, 65].includes(code)) return "Rain";
        if ([71, 73, 75].includes(code)) return "Snow";
        if ([80, 81, 82].includes(code)) return "Rain showers";
        if (code >= 95) return "Thunderstorms";
        return "Unknown";
    };

    return (
        <div className="details-modal">

            <h3>{name}</h3>

            {photo_url ? (
                <img src={photo_url} alt={name} className="poi-image" />
            ) : (
                <div className="poi-placeholder">No image available</div>
            )}

            {rating ? (
                <p>
                    <span className="material-symbols-outlined">star</span>
                    {rating.toFixed(1)}{" "}
                    {user_ratings_total && <span>({user_ratings_total} reviews)</span>}
                </p>
            ) : (
                <p>No rating available</p>
            )}

            {weather ? (
                <div className="weather-info">
                    <p><span className="material-symbols-outlined">cloud</span> {getWeatherDescription(weather.weather_code)}</p>
                    <p><span className="material-symbols-outlined">thermostat</span> {weather.temperature_c}°C</p>
                    <p><span className="material-symbols-outlined">air</span> {weather.wind_speed} m/s</p>
                    <p><span className="material-symbols-outlined">humidity_mid</span> {weather.humidity}%</p>
                </div>
            ) : (
                <p>Weather data not available</p>
            )}
        </div>
    );
}
