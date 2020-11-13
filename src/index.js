// Se cargan los modulos necesarios.
const express = require('express');
const aedes = require('aedes')()
const path = require('path');
const PUERTO =3000;
const portMQTT = 1883
// Crea una Express app.
var mqtt = require('mqtt');
var client = mqtt.connect('mqtt://localhost:1883');
var TopicMQTT ="";

function MandarMensajeMQTT(mensaje){
  console.log('Topic actual:',TopicMQTT);
  if(TopicMQTT!=""){
      client.publish(TopicMQTT,mensaje);
      console.log('Mensaje enviado: ',mensaje);
  }
}
function MandarDireccionMQTT(mensaje){
    client.publish('direccion',mensaje);
    console.log('Direccion: ',mensaje);
  
}
function SuscribirMQTT(topic){
    client.subscribe(topic);
    console.log('Suscrito a: ',topic);
    TopicMQTT=topic;
}

function IniciarServer(){
  var app = express();

  // obtiene la ruta del directorio publico donde se encuentran los elementos estaticos (css, js).
  var publicPath = path.resolve(__dirname, 'public'); 

  // Para que los archivos estaticos queden disponibles.
  app.use(express.static(publicPath));

  app.get('/', function(req, res){
    res.sendFile(__dirname + '/public/index.html');
  });

  const serverMQTT = require('net').createServer(aedes.handle)
  const serverIO = require('http').createServer(app);
  const io = require('socket.io')(serverIO);

  serverIO.listen(PUERTO,()=>{
    console.log("El programa se esta ejecutando en el puerto: "+ PUERTO)
  });

  serverMQTT.listen(portMQTT, function () {
    console.log('El broker MQTT se esta ejecutando en el puerto: ', portMQTT)
  })
  
  io.on('connection', (socketIO)=> {
    console.log('Alguien se conecto con Sockets');
    socketIO.on('mensaje', (data)=>{
      MandarMensajeMQTT(data)
    });
    socketIO.on('topic', (data)=>{
      SuscribirMQTT(data);
    });
    socketIO.on('direccion', (data)=>{
      MandarDireccionMQTT(data);
    });
  });
  client.on('message',(topic,message)=>{
    message= message.toString();
    io.emit('respuesta', message);
  });
}

IniciarServer();