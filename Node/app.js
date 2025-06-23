const bodyParser = require('body-parser');
const express  = require('express');
const {db}  = require('./databases/db');
const routes = require('./routes/route');
require('dotenv').config();


const app = express();
app.use(bodyParser.json());
app.use('/',routes)


app.get('*' ,(req,res)=>{
    res.send("Currently Accessing the wrong API ")
})
db();
const PORT = process.env.PORT
app.listen(PORT, ()=>{
    
    console.log(`Server Running on port ${PORT}` )
})
