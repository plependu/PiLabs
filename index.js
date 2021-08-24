//authors Summer 2021 Team - Tyler Pastor, Mayur Ryali, Apar Mistry, Gwen Kiler

const express = require("express");
const app = express();
const cors = require("cors");
const mysql = require("mysql");
require('dotenv').config();
app.use(cors());
app.use(express.json());

var term_input = [];
var CUI_input = [];
var index;
var val = "";

const db = mysql.createConnection({
    host: "localhost",
    user: "root",
    password: "PiLabs21!",
    database: "umls",
    port: "3306"
});

db.connect((err) => {
    if(err) console.log(err);
    else console.log("MySQL connected");
});

app.post('/search', cors(), async (req,res) => {  
    term_input[0] = req.body.searchVal;
    console.log("input", term_input);
    res.sendStatus(200);
}); 

app.post('/CUIsearch', cors(), async (req,res) => {  
    CUI_input[0] = req.body.CUI;
    console.log("input", CUI_input);
    res.sendStatus(200);
}); 

app.get("/CUIs", async (req, res) => {
    if(term_input[0] == ""){
        result = [];
        result[0] = {
            CUI: "ERROR"
        }
        res.json({result});
    }
    else{
        var sql = 'SELECT DISTINCT CUI ' +
                  'FROM mrconso ' +
                  'WHERE STR LIKE \'' + term_input[0] + '\' ' +
                  'ORDER BY CUI;';

        db.query(sql, (err, result) => {
            if(err){
                console.log("CUI error");
                res.json({CUI: "ERROR"});
            }
            else{
                console.log('No Error');
                res.json({result});
            }
        });
    } 
});

app.get("/sources", async (req, res) => {

    res.json({CUI: val});  
});

app.get("/names", async (req, res) => {

    res.json({CUI: val});  
});

app.get("/definitions", async (req, res) => {
    if(CUI_input[0] == ""){
        res.json({def: "ERROR"});
    }
    else{
        var sql = 'SELECT DISTINCT CUI, DEF ' +
                'FROM mrdef ' +
                'WHERE CUI = \'' + CUI_input[0] + '\' ';

        db.query(sql, (err, result) => {
            if(err){
                console.log("Def error");
                res.json({def: "ERROR"});
            }
            else{
                index = 0;
                val = "";

                while(result[index] != null){
                    val += result[index].CUI + " ";
                    val += result[index].DEF + ", ";
                    console.log({index});

                    index++;
                }

                val = val.substring(0, val.length - 2);

                if(val == ""){
                    val = "No Definitions Exist";
                }

                console.log('No Error');
                res.json({def: val});
            }
        });
    }
});

app.get("/AUIs", async (req, res) => {
    
    res.json({AUI: val});
});

app.listen(5000);