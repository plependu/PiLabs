import './searchInput.css';
import Info from './info.js';
import React, { useState, useEffect } from "react";
import axios from 'axios';
import * as ReactBootStrap from 'react-bootstrap';
import logo from './PiLabsCrossLogo.png';
import mg from './mg.png';
import { useHistory, useParams, Link, useRouteMatch, Switch, Route } from 'react-router-dom';

function SearchInput() {
    const [searchTerm, setSearchTerm] = useState("");
    const [CUIs, setCUIs] = useState([]);
    const [loading, setLoading] = useState(true);
    const param = useParams();
    const history = useHistory();
    const { path, url } = useRouteMatch();

    useEffect(() => {
        paramInput();
    }, [param.term]);

    const paramInput = async () => {
        if(param.term == null || searchTerm !== ""){
        }
        else{
            // history.push(`/search=${param.term}`);
            // console.log("HEELO");
            document.getElementById('word-search').value = param.term;
            setSearchTerm(param.term);

            setLoading(false);

            await axios.post('http://localhost:5000/search', {    
                searchVal: param.term
            });

            const data = await fetch('/CUIs');
            const CUI = await data.json();
            setCUIs(CUI.result);
            setLoading(true);
        }
    };

    const search = async () => {
        if(searchTerm !== ""){
            history.push(`/search=${searchTerm}`);

            setLoading(false);

            await axios.post('http://localhost:5000/search', {    
                searchVal: searchTerm
            })

            const data = await fetch('/CUIs');
            const CUI = await data.json();
            setCUIs(CUI.result);

            setLoading(true);
        }
    };

    const keyEvent = (e) => {
        if(e.key === "Enter"){
            search();
        }
    };

    return (
        <div className="UMLS">
            <div className="logo-nav" id="navbar">
                <img className="logo" src={logo} alt="logo"></img>
                <input 
                    className="search-bar-1 search-bar" 
                    type="text" 
                    id="word-search"
                    placeholder="Search the UMLS..." 
                    onKeyPress={keyEvent} 
                    onChange={(e) => setSearchTerm(e.target.value)}
                />
                <button className="search-button" onClick={search}>
                    <img className="mg" src={mg} alt="mg"></img> 
                </button>
                {/* <label from="word-search" className="search-label"> Search the UMLS...</label> */}
            </div>
            <div className="id-words">
                <div className="id CUI-id"> CUI </div>
                <div className="id source-id"> Source </div>
                <div className="id term-id"> Term </div>
            </div>
            <Switch>
                <Route path={`${path}/:CUI`} component={Info}/>
            </Switch>
            <div className="CUI-background">
                <div className="CUI-content">
                    {loading ? 
                    <div>{CUIs.map(CUIs => (
                        <div key={CUIs.CUI}><Link to={`${url}/${CUIs.CUI}`}> {CUIs.CUI} </Link></div>
                    ))}</div> : 
                    <div className="spinner"> <ReactBootStrap.Spinner animation="border" variant="primary" /></div>}
                </div>
            </div>
    </div>
    );
}

export default SearchInput;