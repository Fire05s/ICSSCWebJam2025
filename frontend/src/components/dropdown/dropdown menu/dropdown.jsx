import React from "react";
import DropdownContent from "../dropdown content/dropdowncontent";
const Dropdown = ((buttonText,content)) => {
    return (<div><DropdownButton></DropdownButton>(buttonText)<DropdownContent>(content)</DropdownContent></div>  );
};

export default Dropdown;





const DropdownItem = ({children, onClick}) =>{
    return(
        <div className= "dropdown-item" onClick={onClick}>{children}
        </div>
    );
};

