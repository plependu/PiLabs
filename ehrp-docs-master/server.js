// References
// 1. https://codeburst.io/build-a-weather-website-in-30-minutes-with-node-js-express-openweather-a317f904897b

// Requirements and packages
const express = require('express')
const app = express()

// Allow access to the public folder
app.use(express.static('public'));
app.set('view engine', 'ejs')

// Landing pages START

/*
Template for adding a new page
[text] are parameters. Omit the []

app.get('/[Directory for the link. They do not have to be the same as the file name]', function (req, res) {
    res.render('[.ejs file without the .ejs]') // Use this when changing the template to see if it works
})

*/

app.get('/', function (req, res) {
    //res.render('template') // Use this when changing the template to see if it works
    res.render('home') // Otherwise keep it as the home
})

app.get('/introduction', function (req, res) {
    res.render('introduction')
})

app.get('/authentication', function (req, res) {
    res.render('authentication')
})

app.get('/resources/ehrp', function (req, res) {
    res.render('res_ehrp')
})

app.get('/resources/texts', function (req, res) {
    res.render('res_texts')
})

app.get('/examples', function (req, res) {
    res.render('examples')
})

// Tagger documentation routes
app.get('/tagger', function (req, res) {
    res.render('tagger/userDocumentation')
})

app.get('/tagger/userDocumentation', function (req, res) {
    res.render('tagger/userDocumentation')
})

app.get('/tagger/contributorDocumentation/introduction', function (req, res) {
    res.render('tagger/contributorIntroduction')
})

app.get('/tagger/contributorDocumentation/ConceptParser', function (req, res) {
    res.render('tagger/ConceptParser')
})

app.get('/tagger/contributorDocumentation/DictionaryParser', function (req, res) {
    res.render('tagger/DictionaryParser')
})

app.get('/tagger/contributorDocumentation/ehrpUtils', function (req, res) {
    res.render('tagger/ehrpUtils')
})

app.get('/tagger/contributorDocumentation/endpointResources', function (req, res) {
    res.render('tagger/endpointResources')
})

app.get('/tagger/contributorDocumentation/filePaths', function (req, res) {
    res.render('tagger/filePaths')
})

app.get('/tagger/contributorDocumentation/startAPI', function (req, res) {
    res.render('tagger/startAPI')
})

app.get('/tagger/contributorDocumentation/WordSenseDisambiguation', function (req, res) {
    res.render('tagger/WordSenseDisambiguation')
})
// End tagger documentation routes

// Landing pages END

// Error catches START
app.use('*',function(req, res){
    res.send('Error 404: Not Found!')
})
// Error catches END

// Print on terminal when you start the server
app.listen(3030, function () {
    console.log('Documentation listening on port 3030!');
    console.log('Visit http://localhost:3030/ to view the documentation.');
})
