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
            <img className="logo" src={logo} alt="HI"></img>
            <input className="search-bar-1 search-bar" type="text" id="word-search" placeholder=" " onChange={(e) => setSearchTerm(e.target.value)}/>
            <button className="search-button" onClick={search}> Search </button>
            <label from="word-search" className="search-label"> Search the UMLS...</label>
        </div>
        <div className="id-words">
            <div className="id CUI-id"> CUI </div>
            <div className="id source-id"> Source </div>
            <div className="id term-id"> Term </div>
        </div>
        <div className="CUI-background">
            <div className="CUI-content">
                {loading ? 
                <div>{CUIs}</div> : 
                <div className="spinner"> <ReactBootStrap.Spinner animation="border" variant="primary" /></div>}
            </div> 
        </div>
        <div className="nav-2">
            <input className="search-bar-2 search-bar" id="CUI-search" type="text" placeholder=" " onChange={(b) => setCUIsearch(b.target.value)}/>
            <button className="search-button-2 search-button" onClick={search2}> Search </button>
            <label from="CUI-search" className="search2-label"> Search with a CUI for more information... </label>
        </div>
        <div className="content-background">
            <div className="CUI-content">
                {loading2 ? (
                    <div> {defs} </div>
                    // <div> {AUIs} </div>
                ) : 
                <div className="spinner"> <ReactBootStrap.Spinner animation="border" variant="primary" /> </div>}
            </div> 
        </div>
    </div>
  );
}

export default App;