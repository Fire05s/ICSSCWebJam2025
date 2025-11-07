import React from "react";

const DropdownItem = ({children, onClick}) =>{
    return(
        <div className= "dropdown-item" onClick={onClick}>{children}
        </div>
    );
};

