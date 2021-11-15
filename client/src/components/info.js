import './info.css';
import './searchInput'
import React, { useEffect } from 'react';
import axios from 'axios';
import { useParams, useHistory } from 'react-router-dom';

function Info() {
    var param = useParams();
    // const [term, setTerm] = useState(param.term);
    var history = useHistory();

    useEffect(() => {
        check();
    }, [param.CUI])

    const check = async () => {
        await axios.post('http://localhost:5000/search', {    
            searchVal: param.term
        });

        const data = await fetch('/CUIs');
        const CUI = await data.json();

        var index = 0;
        var change = 'false';

        while(CUI.result[index] != null){
            if(param.CUI === CUI.result[index].CUI){
                change = 'true';
                break;
            }
            console.log(index);
            index++;
        }

        if(change === 'false'){
            history.push(`/search=${param.term}`);
        }
    };

    return (
        <div className="div">
            <div className="div2">CUI: </div>
            <div className="div3">{param.CUI}</div>
        </div>
    );
}

export default Info;

