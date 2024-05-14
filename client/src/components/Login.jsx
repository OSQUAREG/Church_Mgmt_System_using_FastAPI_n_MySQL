import React, { useState } from "react";
import { Alert, Button, Container, Form, InputGroup } from "react-bootstrap";
import { useForm } from "react-hook-form";
import { Link, useNavigate } from "react-router-dom";
import { baseUrl } from "..";
import { login } from "../auth";


import { faEye, faEyeSlash, faSignIn } from '@fortawesome/free-solid-svg-icons';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';

const LoginPage = () => {

    const { register, handleSubmit, reset, formState: { errors } } = useForm();
    const [show, setShow] = useState(false);
    const [serverResponse, setServerResponse] = useState("");
    const navigate = useNavigate();

    const [showPassword, setShowPassword] = useState(false);
    const toggleShowPassword = () => {
        setShowPassword(!showPassword);
    };

    const loginUser = (data) => {
        console.log(data);

        const headers = new Headers({
            "Content-Type": "application/x-www-form-urlencoded",
        });

        const formData = new URLSearchParams();
        for (const key in data) {
            formData.append(key, data[key]);
        }
        
        const requestOptions = {
            method: "POST",
            headers: headers,
            body: formData.toString(), // JSON.stringify(data)
        }

        fetch(`${baseUrl}/auth/login`, requestOptions)
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
                setShow(true)
                alert(data.message)
                const reload = window.location.reload()
                reload()
            })
            .catch(error => console.log(error))
        reset();
    };
    return (
        <Container>
            <div className="form">
                {show ?
                    <>
                        <Alert variant="danger" onClose={() => setShow(false)} dismissible>
                            <p>{serverResponse}</p>
                        </Alert>
                        <h1 className="">Login</h1>
                    </>
                    :
                    <h1 className="">Login</h1>
                }
                <br />
                <Form>
                    <Form.Group className="mb-3" controlId="formBasicUsercode">
                        <Form.Label className="form-label" >Usercode</Form.Label>
                        <Form.Control type="text" placeholder="Enter Your Member Code"
                            {...register("username", { required: true })}
                        />
                        {errors.username && <small style={{ color: "red" }}>Usercode is required</small>}
                    </Form.Group>
                    <br />

                    <Form.Group className="mb-3" controlId="formBasicPassword">
                        <Form.Label className="form-label" >Password</Form.Label>
                        <InputGroup>
                            <Form.Control type={showPassword ? "text" : "password"} placeholder="Your password"
                                {...register("password", { required: true })}
                            />
                            <Button variant="secondary btn-sm" type="button" onClick={toggleShowPassword}
                            >{showPassword ? <FontAwesomeIcon icon={faEyeSlash} />: <FontAwesomeIcon icon={faEye} />}</Button>
                        </InputGroup>
                        {errors.password && <small style={{ color: "red" }}>Password is required</small>}
                    </Form.Group>
                    <br />

                    <Form.Group className="mb-3">
                        <Button as="sub" variant="success" onClick={handleSubmit(loginUser)} ><FontAwesomeIcon icon={faSignIn} />{" "}Login</Button>
                    </Form.Group>
                    <br />

                    <Form.Group className="mb-3">
                        <p>Don't have an account? <Link to="/signup">Sign Up</Link>.</p>
                    </Form.Group>
                </Form>
            </div>
        </Container>
    )
};

export default LoginPage;