import React from "react";
// import UserLevels from "./UserLevels";
import SelectLevel from "./SelectLevel";
import GetHierarchy from "./Hierarchy";

const HomePage = () => {
    return (
        <div>
            <h1>Home Page</h1>
            <p>Welcome to ChurhMan app</p>
            <SelectLevel />
            {/* <GetHierarchy /> */}
        </div>
    )
};

export default HomePage