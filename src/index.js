// Se cargan los modulos necesarios.
const express = require('express');
const path = require('path');
const PUERTO =3000;
// Crea una Express app.
var app = express();

// obtiene la ruta del directorio publico donde se encuentran los elementos estaticos (css, js).
var publicPath = path.resolve(__dirname, 'public'); //path.join(__dirname, 'public'); también puede ser una opción

// Para que los archivos estaticos queden disponibles.
app.use(express.static(publicPath));

app.get('/', function(req, res){
  res.sendfile(__dirname + '/public/index.html');
  });
app.listen(PUERTO,()=>{
  console.log("El programa esta corriendo en el puerto: "+ PUERTO)
});