import './searchInput.css';
import React, { useState } from "react";
import axios from 'axios';
import * as ReactBootStrap from 'react-bootstrap';
import logo from './PiLabsCrossLogo.png';

function App() {
    const [searchTerm, setSearchTerm] = useState("");
    const [CUIsearch, setCUIsearch] = useState("");
    const [CUIs, setCUIs] = useState("");
    const [defs, setDefs] = useState("");
    const [AUIs, setAUIs] = useState("");
    const [loading, setLoading] = useState(true);
    const [loading2, setLoading2] = useState(true);

    const search = () =>{
        setLoading(false);
        axios.post("http://localhost:5000/search", {    
            searchVal: searchTerm
        })
        setCUIs("");

        setTimeout(() => {
            fetch('/CUIs')
            .then(res => res.json())
            .then(data => setCUIs(data.CUI))
        }, 200);

        setTimeout(() => {
            setLoading(true);
        }, 0);
    };

    const search2 = () =>{
        setLoading2(false);
        axios.post("http://localhost:5000/CUIsearch", {    
            CUI: CUIsearch
        })//.then((response) => {
        //     console.log(response);
        // });
        setDefs("");
        setAUIs("");

        fetch('/definitions')

        fetch('/definitions')
        .then(res => res.json())
        .then(data => setDefs(data.def))

        fetch('/AUIs')

        fetch('/AUIs')
        .then(res => res.json())
        .then(data => setAUIs(data.AUI))

        setTimeout(() => {
            setLoading2(true);
        }, 3000);
    };

  return (
    <div className="UMLS">
        <div className="logo-nav">
            <img
            className="logo" 
            src={logo} 
            alt="HI"></img>
            <div className="nav">
                <input 
                className="searchBar" 
                type="text" 
                placeholder="Search the UMLS..." 
                onChange={(e) => setSearchTerm(e.target.value)}/>
                <button className="searchButton" 
                onClick={search}> Search </button>
            </div>
        </div>
        <div className="id-words">
            <div className="CUI-id">
                CUI
            </div>
            <div className="source-id">
                Source
            </div>
            <div className="term-id">
                Term
            </div>
        </div>
        <div className="CUI-background">
            <div className="CUI-content">
                {loading ? 
                <div>{CUIs}
                </div> : 
                <div className="spinner">
                    <ReactBootStrap.Spinner animation="border" variant="primary" />
                </div>}
            </div> 
        </div>
        <div className="nav-2">
            <input 
            className="searchBar-2" 
            type="text" 
            placeholder="Search with a CUI for more information..." 
            onChange={(b) => setCUIsearch(b.target.value)}/>
            <button className="searchButton-2" 
            onClick={search2}> Search </button>
        </div>
        <div className="content-background">
            <div className="CUI-content">
                {loading2 ? 
                <div>{defs} <div> {AUIs}
                </div>
                </div>  : 
                <div className="spinner">
                    <ReactBootStrap.Spinner animation="border" variant="primary" />
                </div>}
            </div> 
        </div>
    </div>
  );
}

export default App;