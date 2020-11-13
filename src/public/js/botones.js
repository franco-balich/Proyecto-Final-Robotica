const   btnArriba = document.getElementById('btnArriba'),
        btnAbajo = document.getElementById('btnAbajo'),
        btnIzquierda = document.getElementById('btnIzquierda'),
        btnDerecha = document.getElementById('btnDerecha'),
        btnSuscribirse = document.getElementById('btnSuscribirse'),
        btnEnviar = document.getElementById('btnEnviar'),
        listaMensajes = document.getElementById('listaDeMensajes'),
        txtTopic= document.getElementById('txtTopic'),
        txtMensaje= document.getElementById('txtMensaje');

var mensaje="";
var topic ="";

function EnviarMensaje(etiqueta,mensaje){
    socket.emit(etiqueta,mensaje);
}
const socket = io("http://localhost:3000/");

socket.on('respuesta', (data)=>{
    console.log("Mensaje MQTT: ",data);
    listaMensajes.innerHTML += "<option>"+data+"</option>";
});

btnEnviar.addEventListener('click', () => {
    mensaje="Enviado";
    comando = txtMensaje.value;
    if(comando!=""){
        console.log(mensaje)
        EnviarMensaje('mensaje',comando)
    }
    else{
        alert("Por favor ingrese un mensaje");
    }
});

btnSuscribirse.addEventListener('click', () => {
    mensaje="Suscrito";
    comando = txtTopic.value;
    if(comando!=""){
        console.log(mensaje)
        EnviarMensaje('topic',comando)
    }
    else{
        alert("Por favor ingrese un topic");
    }
});
btnArriba.addEventListener('click', () => {
    mensaje="Arriba";
    console.log(mensaje)
    EnviarMensaje('direccion',mensaje)
    //listaMensajes.innerHTML += "<option>"+mensaje+"</option>";
});
btnAbajo.addEventListener('click', () => {
    mensaje="Abajo";
    console.log(mensaje)
    EnviarMensaje('direccion',mensaje)
   // listaMensajes.innerHTML += "<option>"+mensaje+"</option>";
});
btnIzquierda.addEventListener('click', () => {
    mensaje="Izquierda";
    console.log(mensaje)
    EnviarMensaje('direccion',mensaje)
   // listaMensajes.innerHTML += "<option>"+mensaje+"</option>";
});
btnDerecha.addEventListener('click', () => {
    mensaje="Derecha";
    console.log(mensaje)
    EnviarMensaje('direccion',mensaje)
    //listaMensajes.innerHTML += "<option>"+mensaje+"</option>";
});
