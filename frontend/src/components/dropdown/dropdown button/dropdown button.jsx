import React from "react";
import "./DropdownButton.css"
import (FaChervonDown) from "react-icons/fa";
const DropdownButton =  ((children)) => {
    return (<div className="dropdown-btn">(children)<span className="toggle-icon"><FaChervonDown></FaChervonDown></span></div>  );
};

export default DropdownButton;
