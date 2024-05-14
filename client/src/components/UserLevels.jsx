// import React, { useEffect, useState } from "react";
// import { baseUrl } from "..";
// import SelectLevel from "./SelectLevel";
import { Card } from "react-bootstrap";
import { Link } from "react-router-dom";


export const UserLevels = ({ level_code, churchlevel_code, church_level, onRelogin }) => {
    
    return(
        <div>
            <h1>Church Levels:</h1>
            <Link className="link" onClick={onRelogin}>
                    <Card.Body>
                        <Card.Title>{church_level}</Card.Title>
                        <Card.Link className='link'>{onRelogin}</Card.Link>
                        {/* <Card.Text className="m-2 text-muted">
                            <small className="justify-content">Date: {date_created}  ||  Clicks: {visits}</small>
                        </Card.Text> */}
                    </Card.Body>
            </Link>
            {/* <ul>
                {churchLevels.map(level => (
                    <li key={level.Level_Code}>{level.Church_Level}</li>
                ))}
            </ul> */}
        </div>
    )

}

// const UserLevels = () => {
//     const [churchLevels, setChurchLevels] = useState([]);
    
//     useEffect(() => {
//         const token = localStorage.getItem("REACT_TOKEN_AUTH_KEY").replace(/^"|"$/g, '');
        
//         if (!token) {
//             console.log("Token not found");
//             // Handle the case where token is missing
//             return;
//         }
        
//         const requestOptions = {
//             method: "GET",
//             headers: { "Authorization": `Bearer ${token}` }
//         };

//         fetch(`${baseUrl}/auth/user_levels/me`, requestOptions)
//             .then(response => {
//                 if (!response.ok) {
//                     throw new Error('Network response was not ok');
//                 }
//                 return response.json();
//             })
//             .then(data => {
//                 console.log(data);
//                 setChurchLevels(data); // Update state with received data
//             })
//             .catch(error => console.error('Error fetching data:', error));
//     }, []); // Empty dependency array, effect runs once on mount

//     return (
        // <div>
        //     <h1>Church Levels:</h1>
        //     <ul>
        //         {churchLevels.map(level => (
        //             <li key={level.Level_Code}>{level.Church_Level}</li>
        //         ))}
        //     </ul>
        // </div>
//     );
// };

// export default UserLevels;