import numpy as np
import time
#from os import system
from controller import Robot, DistanceSensor, Motor
from paho.mqtt import client as mqtt_client
import random

robot = Robot()
ENA = 5
ENB = 6
IN1 = 7
IN2 = 8
IN3 = 9
IN4 = 11
ESTADO = False
#******************************************************************
#   Network Configuration
#******************************************************************
InputNodes = 3      # incluye neurona de BIAS
HiddenNodes = 4     #incluye neurona de BIAS
OutputNodes = 4
i = 0
j = 0
Accum=0.0
Hidden=[0 for i in range(HiddenNodes)]
Output=[0 for i in range(OutputNodes)]

HiddenWeights=[]
OutputWeights = []

EstadoEntrenado=False
EstadoMQTT=False

global previousMillis 
previousMillis = 0              #para medir ciclos de tiempo
interval = 5 ##25                   #intervalos cada x milisegundos
grados_servo = 90               #posicion del servo que mueve el sensor ultrasonico
clockwise = True                #sentido de giro del servo
ANGULO_MIN = 30 
ANGULO_MAX = 150 
ditanciaMaxima = 50.0           #distancia de lejania desde la que empieza a actuar la NN
incrementos = 9                 #incrementos por ciclo de posicion del servo
accionEnCurso = 1               #cantidad de ciclos ejecutando una accion
multiplicador = 1000/interval   #multiplica la cant de ciclos para dar tiempo a que el coche pueda girar
SPEED = 100                     #velocidad del coche de las 4 ruedas a la vez.
tiempoDeEjecucion=0             #
arrayDistancias=[0,0,0]

TIME_STEP = 64
MAX_SPEED = 3

leftMotor = robot.getMotor('left wheel motor')
rightMotor = robot.getMotor('right wheel motor')
leftMotor.setPosition(float('inf'))
rightMotor.setPosition(float('inf'))

ps = []
psNames = ['ps0','ps1','ps6','ps7']

#ps7 y ps0 se tratan juntos como centro
#ps6 se trata como izquierda
#ps1 se trata como derecha

mqttMessage=""
mqttTopic=""

t_end = time.time()+1

broker="localhost"
port = 1883

# generate client ID with pub prefix randomly
client_id = f'python-mqtt-{random.randint(0, 100)}'

def resetSegundo():
    t_end = time.time()+1
    
def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Conectado al MQTT Broker!")
        else:
            print("Error al conectar al MQTT Broker %d\n", rc)
        robot.step(1)

    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def publish(client, topicSend, msg):
    result = client.publish(topicSend, msg)
    # result: [0, 1]
    status = result[0]
    if status == 0:
        print(f"Se envio ({msg}) al topic ({topicSend})")
    else:
        print(f"Error al enviar el mensaje al topic ({topicSend})")

def on_message(client, userdata, msg):
    global ESTADO
    print(f"Recibido ({msg.payload.decode()}) del topic ({msg.topic})")
    mqttMessage=msg.payload.decode()
    mqttTopic=msg.topic
    resetSegundo()
    if(mqttMessage =='Arriba' and mqttTopic =="direccion" and not ESTADO):
        avanzar()
    if(mqttMessage =='Abajo' and mqttTopic =="direccion" and not ESTADO):
        retroceder()
    if(mqttMessage =='Derecha' and mqttTopic =="direccion" and not ESTADO):
        derecha()
    if(mqttMessage =='Izquierda' and mqttTopic =="direccion" and not ESTADO):
        izquierda()
    if(mqttMessage =='test' and mqttTopic =="direccion" and not ESTADO):
        print("Prueba")
        robot.step(500)
    if(mqttMessage=='Manual' and mqttTopic=="estado"):
        ESTADO = False
        print("Estado: Manual")
        robot.step(1000)
    if(mqttMessage=='Automatico' and mqttTopic=="estado"):
        ESTADO = True
        print("Estado: Automatico")
        robot.step(1000)
        
def subscribe(client: mqtt_client):
    client.subscribe('test')
    client.subscribe('mensaje')
    client.subscribe('direccion')
    client.subscribe('estado')
    client.on_message = on_message
    EstadoMQTT=True

# Creamos la clase 
class NeuralNetwork:

    def __init__(self, layers, activation='tanh'):
        if activation == 'sigmoid':
            self.activation = sigmoid
            self.activation_prime = sigmoid_derivada
        elif activation == 'tanh':
            self.activation = tanh
            self.activation_prime = tanh_derivada

        # inicializo los pesos
        self.weights = []
        self.deltas = []
        # capas = [2,3,4]
        # rando de pesos varia entre (-1,1)
        # asigno valores aleatorios a capa de entrada y capa oculta
        for i in range(1, len(layers) - 1):
            r = 2* np.random.random((layers[i-1] + 1, layers[i] + 1)) -1
            self.weights.append(r)
        # asigno aleatorios a capa de salida
        r = 2* np.random.random( (layers[i] + 1, layers[i+1])) - 1
        self.weights.append(r)

    def fit(self, X, y, learning_rate=0.2, epochs=100000):
        # Agrego columna de unos a las entradas X
        # Con esto agregamos la unidad de Bias a la capa de entrada
        ones = np.atleast_2d(np.ones(X.shape[0]))
        X = np.concatenate((ones.T, X), axis=1)
        
        for k in range(epochs):
            i = np.random.randint(X.shape[0])
            a = [X[i]]

            for l in range(len(self.weights)):
                    dot_value = np.dot(a[l], self.weights[l])
                    activation = self.activation(dot_value)
                    a.append(activation)
            # Calculo la diferencia en la capa de salida y el valor obtenido
            error = y[i] - a[-1]
            deltas = [error * self.activation_prime(a[-1])]
            
            # Empezamos en el segundo layer hasta el ultimo
            # (Una capa anterior a la de salida)
            for l in range(len(a) - 2, 0, -1): 
                deltas.append(deltas[-1].dot(self.weights[l].T)*self.activation_prime(a[l]))
            self.deltas.append(deltas)

            # invertir
            # [level3(output)->level2(hidden)]  => [level2(hidden)->level3(output)]
            deltas.reverse()

            # backpropagation
            # 1. Multiplcar los delta de salida con las activaciones de entrada 
            #    para obtener el gradiente del peso.
            # 2. actualizo el peso restandole un porcentaje del gradiente
            for i in range(len(self.weights)):
                layer = np.atleast_2d(a[i])
                delta = np.atleast_2d(deltas[i])
                self.weights[i] += learning_rate * layer.T.dot(delta)

            if k % 10000 == 0: 
                print('epochs:', k)
            #print("---Red neuronal entrenada---")

    def predict(self, x): 
        ones = np.atleast_2d(np.ones(x.shape[0]))
        a = np.concatenate((np.ones(1).T, np.array(x)), axis=0)
        for l in range(0, len(self.weights)):
            a = self.activation(np.dot(a, self.weights[l]))
        return a

    def print_weights(self):
        print("LISTADO PESOS DE CONEXIONES")
        for i in range(len(self.weights)):
            print(self.weights[i])

    def get_weights(self):
        return self.weights
    
    def get_deltas(self):
        return self.deltas

# Al crear la red, podremos elegir entre usar la funcion sigmoid o tanh
def sigmoid(x):
    return 1.0/(1.0 + np.exp(-x))

def sigmoid_derivada(x):
    return sigmoid(x)*(1.0-sigmoid(x))

def tanh(x):
    return np.tanh(x)

def tanh_derivada(x):
    return 1.0 - x**2


# Red Coche para Evitar obstáculos
nn = NeuralNetwork([2,3,4],activation ='tanh')
X = np.array([[-1, 0],   # sin obstaculos
              [-1, 1],   # sin obstaculos
              [-1, -1],  # sin obstaculos
              [0, -1],   # obstaculo detectado a derecha
              [0,1],     # obstaculo a izq
              [0,0],     # obstaculo centro
              [1,1],     # demasiado cerca a derecha
              [1,-1],    # demasiado cerca a izq
              [1,0]      # demasiado cerca centro
             ])
# las salidas 'y' se corresponden con encender (o no) los motores
y = np.array([[1,0,0,1], # avanzar
              [1,0,0,1], # avanzar
              [1,0,0,1], # avanzar
              [0,1,0,1], # giro derecha
              [1,0,1,0], # giro izquierda (cambie izq y derecha)
              [1,0,0,1], # avanzar
              [0,1,1,0], # retroceder
              [0,1,1,0], # retroceder
              [0,1,0,1]  # giro derecha
             ])
nn.fit(X, y, learning_rate=0.03,epochs=40001)

def valNN(x):
    return (int)(abs(round(x)))

index=0
for e in X:
    prediccion = nn.predict(e)
    print("X:",e,"esperado:",y[index],"obtenido:", valNN(prediccion[0]),valNN(prediccion[1]),valNN(prediccion[2]),valNN(prediccion[3]))
    #print("X:",e,"y:",y[index],"Network:",prediccion)
    index=index+1

deltas = nn.get_deltas()
valores=[]
index=0

for arreglo in deltas:
    valores.append(arreglo[1][0] + arreglo[1][1])
    index=index+1

def parar():
    leftMotor.setVelocity(0 * MAX_SPEED)
    rightMotor.setVelocity(0 * MAX_SPEED)
       
def avanzar():
    leftMotor.setPosition(float('inf'))
    rightMotor.setPosition(float('inf'))
    leftMotor.setVelocity(0.5 * MAX_SPEED)
    rightMotor.setVelocity(0.5 * MAX_SPEED)
    robot.step(1000)
    parar()
               
def derecha():  
    leftMotor.setPosition(575)
    rightMotor.setPosition(-575)
    leftMotor.setVelocity(0.5 * MAX_SPEED)
    rightMotor.setVelocity(0.5 * MAX_SPEED)
    robot.step(660)
    parar()
    
def izquierda():
    leftMotor.setPosition(-575)
    rightMotor.setPosition(575)
    leftMotor.setVelocity(0.5 * MAX_SPEED)
    rightMotor.setVelocity(0.5 * MAX_SPEED)
    robot.step(660)
    parar()
      
def retroceder():
    leftMotor.setPosition(-10000)
    rightMotor.setPosition(-10000)
    leftMotor.setVelocity(0.5 * MAX_SPEED)
    rightMotor.setVelocity(0.5 * MAX_SPEED)
    robot.step(1000)
    parar()
    
#USA LA RED NEURONAL YA ENTRENADA
def conducir():
    if ESTADO:
        TestInput = np.array([0, 0,0])
        entrada1=0
        entrada2=0
        
        #******************************************************************
        #  OBTENER DISTANCIA DEL SENSOR
        #******************************************************************
    
        # Entrada1
        # 1 => -1 - No hay obstaculos
        # 2 => 0  - Cerca
        # 3 => 1  - Choque
        # 
        # Entrada2
        # 1 => -1 - Sensor derecha
        # 2 =>  0 - Sensor frontal
        # 3 =>  1 - Sensor izquierda
    
        #arrayDistancias[sensor-1]=distanciaDetectada-2
        if 0 in arrayDistancias:
            entrada1=0
            entrada2=arrayDistancias.index(-1)-1
        elif 1 in arrayDistancias:
            entrada1=1
            entrada2=arrayDistancias.index(-1)-1
        else:
            entrada1=-1
            entrada2=0
        accionEnCurso = int(((entrada1 +1) * multiplicador)+1)  # si esta muy cerca del obstaculo, necestia mas tiempo de reaccion
        print("Distancia: "+ str(entrada1)+" - Sensor: " + str(entrada2))
        #******************************************************************
        #  LLAMAMOS A LA RED FEEDFORWARD CON LAS ENTRADAS
        #******************************************************************
    
        TestInput[0] = 1.0 #BIAS UNIT
        TestInput[1] = entrada1
        TestInput[2] = entrada2 / 100.0
        InputToOutput(TestInput[0], TestInput[1], TestInput[2])  #INPUT to ANN to obtain OUTPUT
    
        out1 = round(abs(Output[0]))
        out2 = round(abs(Output[1]))
        out3 = round(abs(Output[2]))
        out4 = round(abs(Output[3]))
    
        #******************************************************************
        #  IMPULSAR MOTORES CON LA SALIDA DE LA RED
        #******************************************************************
    
        print("Actualizar estado motores")
        if out1==1 and out2==0 and out3==0 and out4==1:
            print("Adelante")
            avanzar()
        elif out1==0 and out2==1 and out3==0 and out4==1:
            print("Derecha")
            derecha()
        elif out1==1 and out2==0 and out3==1 and out4==0:
            print("Izquierda")
            izquierda()
        elif out1==0 and out2==1 and out3==1 and out4==0:
            print("Atras")
            retroceder()
        print("S1: " + str(arrayDistancias[0])+" - S2: " + str(arrayDistancias[1])+" S3: " + str(arrayDistancias[2]))
    
        print('///////////////////////////////////////////////////')
 
def InputToOutput(In1, In2, In3):
    TestInput = np.array([0, 0,0])
    TestInput[0] = In1
    TestInput[1] = In2
    TestInput[2] = In3

    #******************************************************************
    #  Calcular las activaciones en las capas ocultas
    #******************************************************************
 
    for i in range(HiddenNodes):
        Accum =0 #HiddenWeights[InputNodes][i] ;
        for j in range(InputNodes):
            Accum += TestInput[j] * HiddenWeights[j][i]
            #Hidden[i] = 1.0 / (1.0 + exp(-Accum)) ;  #Sigmoid
        Hidden[i] = np.tanh(Accum)  #tanh
 
  #******************************************************************
  #  Calcular activacion y error en la capa de Salida
  #******************************************************************
 
    for i in range(OutputNodes):
        Accum = 0 #OutputWeights[HiddenNodes][i];
        for j in range(HiddenNodes):
            Accum += Hidden[j] * OutputWeights[j][i]
        Output[i] = np.tanh(Accum)  #tanh

def setearVelocidad():
    leftMotor.setVelocity(0.2 * MAX_SPEED)
    rightMotor.setVelocity(0.2 * MAX_SPEED)
    
for i in range(4):
    ps.append(robot.getDistanceSensor(psNames[i]))
    ps[i].enable(TIME_STEP)

parar()
while robot.step(TIME_STEP) != -1:       
    if not EstadoEntrenado:
        pesos = nn.get_weights();
        HiddenWeights=pesos[0]
        OutputWeights=pesos[1]
        print("---Red neuronal vinculada al robot---")
        EstadoEntrenado=True
        client = connect_mqtt()
        subscribe(client)
        client.loop_start()
    #setearVelocidad()
    psValues = []
    arrayDistancias=[-1,-1,-1]
    
    for i in range(4):
        psValues.append(ps[i].getValue())
    #Evaluacion ps1 DERECHA
    if(psValues[1]>=80.0):
        arrayDistancias[0]=1
    elif(psValues[1]<80 and psValues[1]>=76.5):
        arrayDistancias[0]=0
    else:
        #Evaluacion ps6 IZQUIERDA
        if(psValues[2]>80.0):
            arrayDistancias[2]=1
        elif(psValues[2]<80 and psValues[2]>=76.5):
            arrayDistancias[2]=0
        else:
            #Evaluacion ps7 y ps0 CENTRO
            if(psValues[0]>=80.0 or psValues[3]>=80.0):
                arrayDistancias[1]=1
            elif(psValues[0]>76.5 or psValues[3]>76.5):
                arrayDistancias[1]=0
    conducir()
