import { useEffect, useState } from "react";
import { baseUrl } from "..";

const GetHierarchy = () => {
    const [churchHierarchy, setChurchHierarchy] = useState([]);
    const [serverResponse, setServerResponse] = useState("");
    
    useEffect(() => {
        const token = localStorage.getItem("REACT_TOKEN_AUTH_KEY");
        
        if (!token) {
            console.log("Token not found");
            // Handle the case where token is missing
            return;
        }

        // Remove surrounding quotes from token if present
        const formattedToken = token.replace(/^"|"$/g, '');

        const headers = new Headers({
            "Content-Type": "application/json",
            "Authorization": `Bearer ${formattedToken}`
        });

        const requestOptions = {
            method: "GET",
            headers: headers
        };

        fetch(`${baseUrl}/hierarchy`, requestOptions)
            .then(response => {
                if (!response.ok ) {
                    return response.json().then(data => {
                        const errorDetail = data.detail;
                        setServerResponse(errorDetail);
                        alert(errorDetail);
                        throw new Error('Network response was not ok');
                    });
                }
                return response.json();
            })
            .then(data => {
                console.log(data.data);
                setChurchHierarchy(data.data); // Update state with received data
                alert(data.message);
            })
            .catch(error => console.error('Error fetching data:', error));
    }, []); // Empty dependency array, effect runs once on mount

    return (
        <div>
            {churchHierarchy.length === 0 && serverResponse}
            <h3>Church Hierarchy </h3>
            <ul>
                {churchHierarchy.map(level => (
                    level.Is_Active && (
                        <li key={level.Level_Code}>
                            {level.Church_Level}
                        </li>
                    )
                ))}
            </ul>
        </div>
    );
};

export default GetHierarchy;