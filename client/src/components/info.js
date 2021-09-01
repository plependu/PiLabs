import './info.css';
import './searchInput'
import React, {useEffect, useState} from 'react';
import axios from 'axios';
import { useParams, useHistory } from 'react-router-dom';

function Info() {
    var param = useParams();
    // const [term, setTerm] = useState(param.term);
    // var history = useHistory();

    // useEffect(() => {
    //     history.push(`/404`);
    //     console.log(term);
    // }, [term])

    return (
        <div className="div">
            <div className="div2">CUI: </div>
            <div className="div3">{param.CUI}</div>
        </div>
    );
}

export default Info;

