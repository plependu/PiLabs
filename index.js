const express = require("express");
const {UMLSJS} = require("umlsjs");
const app = express();
const fs = require('fs');
const cors = require("cors");
const run = require("./search.js");
require('dotenv').config();
app.use(cors());
app.use(express.json());

var input = [];
var CUI = [];

async function STGrabber(){
    const api_key = process.env.APIKEY;
    const token = new UMLSJS.UMLSToken(api_key);
    let ST = await token.getSt();

    return ST;
}

async function CUIGrabber(val){
    var ST = await STGrabber();
    const search = new UMLSJS.UMLSSearch(ST);
    search.init(val);
    await search.query();
    const result = search.getResults();

    return result;
}

async function DefGrabber(){
    var ST = await STGrabber();
    const search = new UMLSJS.CUISearch(ST);
    search.init(CUI[0]);
    await search.getDefinitions()
    const result = search.definitions;

    return result;
}

async function AUIGrabber(){
    var ST = await STGrabber();
    const search = new UMLSJS.CUISearch(ST);
    search.init(CUI[0]);
    await search.getAtoms()
    const result = search.atoms;

    return result;
}

app.post('/search', async(req,res)=>{
    var searchVal = req.body.searchVal;
    input = [];
    input.push(searchVal);
    console.log(searchVal);
    // var searchVal = req.body.searchVal;
    // fs.writeFile('userSearch.txt', searchVal, (err) => {
    //     if (err) throw err;
    // });
    // fs.writeFile('CUI.txt', "", (err) => {
    //     if (err) throw err;
    // });
    // fs.writeFile('AUI.txt', "", (err) => {
    //     if (err) throw err;
    // });
    // fs.writeFile('definition.txt', "", (err) => {
    //     if (err) throw err;
    // });
    // run.TGTGrabber();
    //res.send(searchVal);
}); 

app.get("/", (req, res)=> {          
    res.send(input);              
});

app.get("/api/CUIs", (req, res)=> {
    // setTimeout(async function () { //text file delay call
    //     val = fs.readFileSync('CUI.txt', 'utf8');
    //     res.json({CUI: val});
    // }, 4000 );

    setTimeout(async function () { //text file delay call
        var tmpCUI = await CUIGrabber(input[0]);
        var val = tmpCUI[0].ui;
        CUI = [];
        CUI.push(val);
        console.log("CUI", val);
        res.json({CUI: val});
    }, 200 );
});

app.get("/api/definitions", (req, res)=> {
    // setTimeout(async function () { //text file delay call
    //     val = fs.readFileSync('definition.txt', 'utf8');
    //     res.json({def: val});
    // }, 4000 );
    setTimeout(async function () { //text file delay call
        var tmpDef = await DefGrabber();
        var val = tmpDef[0].value;
        console.log("Def", val);
        res.json({def: val});
    }, 1000 );
});

app.get("/api/AUIs", (req, res)=> {
    // setTimeout(async function () { //text file delay call
    //     val = fs.readFileSync('AUI.txt', 'utf8');
    //     res.json({AUI: val});
    // }, 4000 );
    setTimeout(async function () { //text file delay call
        var tmpAUI = await AUIGrabber();
        var val = tmpAUI[0].ui;
        console.log("AUI", val);
        res.json({AUI: val});
    }, 1000 );
});

// app.get("/def", (req, res)=> {
//     res.send(fs.readFileSync('definition.txt', 'utf8'))
// });


// app.use('/definitions', definitions);

app.listen(5000);