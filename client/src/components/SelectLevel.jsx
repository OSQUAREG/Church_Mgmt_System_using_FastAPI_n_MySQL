import React, { useEffect, useState } from "react";
import { Button, Modal } from "react-bootstrap";
// import { useForm } from "react-hook-form";
import { useNavigate } from "react-router-dom";
import { baseUrl } from "..";
import { login } from "../auth";
import { useForm } from "react-hook-form";

const SelectLevel = () => {
    // const { church_level } = useParams();
    const [churchLevels, setChurchLevels] = useState([]);
    const [userAccess, setUserAccess] = useState([]);

    const { reset } = useForm();
    const [show, setShow] = useState(false);
    const [serverResponse, setServerResponse] = useState("");
    const navigate = useNavigate();

    useEffect(() => {
        let token = localStorage.getItem("REACT_TOKEN_AUTH_KEY");
    
        if (!token) {
            console.log("Token not found");
            // Handle the case where token is missing
            return;
        }

        // Remove surrounding quotes from token if present
        token = token.replace(/^"|"$/g, '');
        
        const requestOptions = {
            method: "GET",
            headers: { "Authorization": `Bearer ${token}` }
        };

        fetch(`${baseUrl}/auth/user_levels/me`, requestOptions)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                console.log(data);
                setChurchLevels(data); // Update state with received data
                setShow(true);
            })
            .catch(error => console.error('Error fetching data:', error));
    }, []); 

    const closeModal = () => { setShow(false) };

    const selectChurchLevel = (churchlevel_code) => {
        console.log(churchlevel_code)

        let token = localStorage.getItem("REACT_TOKEN_AUTH_KEY");
    
        if (!token) {
            console.log("Token not found");
            // Handle the case where token is missing
            return;
        }

        // Remove surrounding quotes from token if present
        token = token.replace(/^"|"$/g, '');

        const headers = new Headers({
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        });

        const requestOptions = {
            method: "POST",
            headers: headers,
            body: JSON.stringify(churchlevel_code)
        }

        fetch(`${baseUrl}/auth/select_level/${churchlevel_code}`, requestOptions)
            .then(response => {
                console.log(response.status)
                if (response.status === 201) {
                    navigate("/")
                }
                return response.json()
            })
            .then(data => {
                console.log(data)
                setServerResponse(data.message)
                console.log(serverResponse)

                // localStorage.setItem("REACT_TOKEN_AUTH_KEY1", data.access_token)

                login(data.access_token)
                setUserAccess(data.user_access)
                console.log(userAccess)
                alert(data.message)
                // const reload = window.location.reload()
                // reload()
                navigate("/")
                setShow(false)

            })
            .catch(error => console.log(error))
        reset();
    };

    return (
            <Modal
                show={show}
                size="sm"
                onHide={closeModal}
                aria-labelledby="contained-modal-title-vcenter"
                centered
            >
                <Modal.Header closeButton>
                    <Modal.Title id="contained-modal-title-vcenter">
                    Please select a church level to continue:
                    </Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    <div>
                        <ul>
                            {churchLevels.map(level => (
                                <li key={level.Level_Code}>
                                    <Button onClick={() => selectChurchLevel(level.ChurchLevel_Code)}>
                                        {level.Church_Level}
                                    </Button></li>
                            ))}
                        </ul>
                    </div>
                </Modal.Body>
                <Modal.Footer>
                    <button onClick={closeModal}>Close</button>
                </Modal.Footer>
            </Modal>
    )
};

export default SelectLevel
