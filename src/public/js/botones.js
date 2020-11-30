const   btnArriba = document.getElementById('btnArriba'),
        btnAbajo = document.getElementById('btnAbajo'),
        btnIzquierda = document.getElementById('btnIzquierda'),
        btnDerecha = document.getElementById('btnDerecha'),
        btnSuscribirse = document.getElementById('btnSuscribirse'),
        btnEnviar = document.getElementById('btnEnviar'),
        btnEstado = document.getElementById('btnEstado'),
        listaMensajes = document.getElementById('listaDeMensajes'),
        txtTopic= document.getElementById('txtTopic'),
        txtMensaje= document.getElementById('txtMensaje');

var mensaje="";
var topic ="";
var estado= true;

function EnviarMensaje(etiqueta,mensaje){
    socket.emit(etiqueta,mensaje);
}
const socket = io("http://localhost:3000/");
//const socket = io("https://119c817e659c.ngrok.io");

socket.on('respuesta', (data)=>{
    console.log("Mensaje MQTT: ",data);
    listaMensajes.innerHTML = "<option>"+data+"</option>" + listaMensajes.innerHTML;
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
btnEstado.addEventListener('click', () => {
    estado=!estado;
    if (estado){
        mensaje="Manual"
    }
    else{
        mensaje="Automatico"
    }    
    console.log(mensaje)
    btnEstado.innerHTML =mensaje
    EnviarMensaje('estado',mensaje)
    //listaMensajes.innerHTML += "<option>"+mensaje+"</option>";
});

