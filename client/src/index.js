import 'bootstrap/dist/css/bootstrap.min.css';
import React from "react";
import ReactDOM from 'react-dom';
import { Route, BrowserRouter as Router, Routes } from "react-router-dom";
import './styles/index.css';
// import jwtDecode from "jwt-decode";
import reportWebVitals from './reportWebVitals';

import Footer from './components/Footer';
import HomePage from './components/Home';
import LoginPage from './components/Login';
// import NavBar from './components/Navbar';
import SignupPage from './components/Signup';
import GetHierarchy from './components/Hierarchy';


export const baseUrl = "http://localhost:8000"
// export const baseUrl = process.env.REACT_APP_BASE_URL
// export const domain = process.env.REACT_APP_DOMAIN_URL
// export const qr_code_folder = process.env.REACT_APP_QR_CODE_FOLDER_PATH

// export const usernameRegex = /^[a-zA-Z0-9_]{3,25}$/;
export const emailRegex = /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i;
// export const customUrlRegex = /^[a-zA-Z0-9_]{5,20}$/;
// export const urlRegex = /^(https?:\/\/)/;


const App = () => {

  // let token = localStorage.getItem("REACT_TOKEN_AUTH_KEY")

  // if (token) {
  //   const decodedJWT = jwtDecode(token);
  //   const expirationTime = decodedJWT.exp * 1000
  //   console.log(expirationTime)
  //   if (expirationTime && expirationTime > Date.now()) {
  //     // Token is still valid
  //     console.log("Token is still valid.");
  //   } else {
  //     // Token has expired
  //     localStorage.removeItem('REACT_TOKEN_AUTH_KEY');
  //     console.log("Your login has expired");
  //     alert("Your login has expired.");
  //     window.location.href = "/login";
  //   };
  // };

  return (
    <Router>
      <div>
        {/* <NavBar /> */}
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/signup" element={<SignupPage />} />
          <Route path="/hierarchy" element={<GetHierarchy />} />
          <Route path="/" element={<HomePage />} />
        </Routes>
        <Footer />
      </div>
    </Router>
  )
}

ReactDOM.render(<App />, document.getElementById("root"));

// const root = createRoot(document.getElementById('root'));
// root.render(<App />);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
