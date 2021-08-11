const express = require("express");
const {UMLSJS} = require("umlsjs");
const app = express();
const cors = require("cors");
const run = require("./search.js");
require('dotenv').config();
app.use(cors());
app.use(express.json());

var input = [];
var input2 =[];
var num = 0;
const api_key = process.env.APIKEY;

async function STGrabber(){ 
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

async function DefGrabber(val){
    var ST = await STGrabber();
    const search = new UMLSJS.CUISearch(ST);
    search.init(val);
    var result;
    try{
        await search.getDefinitions();
        result = search.definitions;
    }
    catch(error){
        console.log("ERROR");
        result = "ERROR";
    }

    return result;
}

async function AUIGrabber(val){
    var ST = await STGrabber();
    const search = new UMLSJS.CUISearch(ST);
    search.init(val);
    await search.getAtoms();
    const result = search.atoms;

    return result;
}

app.post('/search', cors(), async (req,res)=>{  
    input[0] = req.body.searchVal;
    console.log("input", input);
    res.sendStatus(200);
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

app.post('/CUIsearch', cors(), async (req,res)=>{  
    input2[0] = req.body.CUI;
    console.log("input", input2);
    res.sendStatus(200);
}); 

app.get("/", (req, res)=> {          
    res.send(input);              
});

app.get("/api/CUIs", async (req, res) =>  {
    // setTimeout(async function () { //text file delay call
    //     val = fs.readFileSync('CUI.txt', 'utf8');
    //     res.json({CUI: val});
    // }, 4000 );
    var tmpCUI = await CUIGrabber(input[0]);
    num = 0;
    var dis = tmpCUI;//[0].ui;
    var val = "";
    console.log("val", val);
    //console.log("CUI", dis);

    while(dis[num] != null){
        // val.push(dis[num].ui) + " ";
        // val.push(dis[num].rootSource) + " ";
        // val.push(dis[num].name) + " ";
        if(dis[0].ui == "NONE"){
            val = "NO SEARCH RESULTS";
            break;
        }
        val += (dis[num].ui) + " ";
        val += (dis[num].rootSource) + " ";
        val += (dis[num].name) + " ";
        num++;
    }

    res.json({CUI: val});  
});

app.get("/api/sources", async (req, res) =>  {
    // setTimeout(async function () { //text file delay call
    //     val = fs.readFileSync('CUI.txt', 'utf8');
    //     res.json({CUI: val});
    // }, 4000 );
    var tmpCUI = await CUIGrabber(input[0]);
    num = 0;
    var dis = tmpCUI;//[0].ui;
    var val = "";
    console.log("val", val);
    //console.log("CUI", dis);

    while(dis[num] != null){
        // val.push(dis[num].ui) + " ";
        // val.push(dis[num].rootSource) + " ";
        // val.push(dis[num].name) + " ";
        if(dis[0].ui == "NONE"){
            val = "NO SEARCH RESULTS";
            break;
        }
        val += (dis[num].rootSource) + " ";
        num++;
    }

    res.json({CUI: val});  
});

app.get("/api/names", async (req, res) =>  {
    // setTimeout(async function () { //text file delay call
    //     val = fs.readFileSync('CUI.txt', 'utf8');
    //     res.json({CUI: val});
    // }, 4000 );
    var tmpCUI = await CUIGrabber(input[0]);
    num = 0;
    var dis = tmpCUI;//[0].ui;
    var val = "";
    console.log("val", val);
    //console.log("CUI", dis);

    while(dis[num] != null){
        // val.push(dis[num].ui) + " ";
        // val.push(dis[num].rootSource) + " ";
        // val.push(dis[num].name) + " ";
        if(dis[0].ui == "NONE"){
            val = "NO SEARCH RESULTS";
            break;
        }
        val += (dis[num].name) + " ";
        num++;
    }

    res.json({CUI: val});  
});

app.get("/api/definitions", async (req, res)=> {
    // setTimeout(async function () { //text file delay call
    //     val = fs.readFileSync('definition.txt', 'utf8');
    //     res.json({def: val});
    // }, 4000 );
    // var tmpCUI = await CUIGrabber(input[0]);
    // var val = tmpCUI[0].ui;
    var tmpDef = await DefGrabber(input2[0]);
    console.log("def", tmpDef);
    if(tmpDef == "ERROR"){
        val = tmpDef;
    }
    else{
        val = tmpDef[0].value;
    }
    res.json({def: val});
});

app.get("/api/AUIs", async (req, res)=> {
    // setTimeout(async function () { //text file delay call
    //     val = fs.readFileSync('AUI.txt', 'utf8');
    //     res.json({AUI: val});
    // }, 4000 );
    // var tmpCUI = await CUIGrabber(input[0]);
    // var val = tmpCUI[0].ui;
    var tmpAUI = await AUIGrabber(input2[0]);
    val = tmpAUI[0].ui; 
    console.log("AUI", val);
    res.json({AUI: val});
});

app.listen(5000);