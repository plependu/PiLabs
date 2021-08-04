import './searchInput.css';
import React, { useState } from "react";
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
        })//.then((response) => {
        //     console.log(response);
        // });
        setCUIs("");
        setDefs("");
        setAUIs("");

        fetch('/api/CUIs')

        fetch('/api/CUIs')
        .then(res => res.json())
        .then(data => setCUIs(data.CUI))


        fetch('/api/definitions')
        .then(res => res.json())
        .then(data => setDefs(data.def))

        // fetch('/api/AUIs')
        // .then(res => res.json())
        // .then(data => setAUIs(data.AUI))

        setTimeout(() => {
            setLoading(true);
        }, 3000);
    };

    // useEffect(() => {
    //     setLoading(false);
    //     setTimeout(() => {
    //         setLoading(true);
    //     }, 3000);
    // }, []);

  return (
    <div className="UMLS">
        <h1><img src={logo} alt="HI"></img></h1>
        <input className="searchBar" type="text" placeholder="Search..." onChange={(e) => setSearchTerm(e.target.value)}/>
        <button className="searchButton" onClick={search}> Search </button>
        {loading ? <div className="info">CUI: {CUIs}<div> Definition: {defs}</div></div> : <main><ReactBootStrap.Spinner animation="border" variant="primary" /></main>}
        {/* {loading ? <div className="info">CUI: {CUIs} <div> AUI: {AUIs} <div> Definition: {defs}</div></div></div> : <main><ReactBootStrap.Spinner animation="border" variant="primary" /></main>} */}
    </div>
  );
}

export default App;