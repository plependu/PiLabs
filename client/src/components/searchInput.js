import './searchInput.css';
import React, { useEffect, useState } from "react";
import axios from 'axios';
import * as ReactBootStrap from 'react-bootstrap';
import logo from './logo.jpg';

function App() {
    const [searchTerm, setSearchTerm] = useState("");
    const [CUIs, setCUIs] = useState("");
    const [defs, setDefs] = useState("");
    const [AUIs, setAUIs] = useState("");
    const [loading, setLoading] = useState(true);

    const search = () =>{
        setLoading(false);
        axios.post("http://localhost:5000/search", {
            searchVal: searchTerm
        }).then((response) => {
            console.log(response);
        });
        setCUIs("");
        setDefs("");
        setAUIs("");

        fetch('/api/CUIs')
        .then(res => res.json())
        .then(data => setCUIs(data.CUI))

        fetch('/api/definitions')
        .then(res => res.json())
        .then(data => setDefs(data.def))

        fetch('/api/AUIs')
        .then(res => res.json())
        .then(data => setAUIs(data.AUI))

        setTimeout(() => {
            setLoading(true);
        }, 3500);
    };

    // useEffect(() => {
    //     setLoading(false);
    //     setTimeout(() => {
    //         setLoading(true);
    //     }, 3000);
    // }, []);

  return (
    <div className="UMLS">
        <div className="UMLS Search">
            <h1><img src={logo} alt="HI"></img></h1>
            <input class="searchBar" type="text" placeholder="Search..." onChange={(e)=> {setSearchTerm(e.target.value)}}/>
            <button class="searchButton" onClick={search}> Search </button>
            {loading ? <p classname="info">CUI: {CUIs}<p>AUI: {AUIs}<p>Definition: {defs}</p></p></p> : <main><ReactBootStrap.Spinner animation="border" variant="primary" /></main>}
        </div>
    </div>
  );
}

export default App;