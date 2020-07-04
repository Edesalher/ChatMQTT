from myUserMqtt import *
import logging

# Initial configuration for logging.
logging.basicConfig(level=logging.INFO,
                    format='[%(levelname)s] %(message)s')

# The usuario.txt file is read to obtain the user ID.
user_file = open(USER_FILENAME, 'r')
myID = user_file.read().rstrip('\n')
user_file.close()

# The salas.txt file is read to obtain the rooms to which the user belongs.
rooms_file = open(ROOMS_FILENAME, 'r')
myRooms = rooms_file.read()
myRooms = myRooms.split('\n')
myRooms.pop()
rooms_file.close()

# Creating a user for the client.
user = MyUser(myID)

# Creating the commands for the user.
user_commands = MyUserCommands(user)


# Function that is executed when a connection to the broker MQTT occurs.
def on_connect(client, userdata, rc):
    logging.debug('CONECTADO AL BROKER')


# Function that is executed when a publication occurs.
def on_publish(client, userdata, mid):
    logging.debug('Publicación satisfactoria')


# Function that is executed when a message reception occurs.
def on_message(client, userdata, msg):
    topic_by_parts = msg.topic.split('/')
    root_topic = topic_by_parts[0]

    if root_topic == 'usuarios':
        message = msg.payload.decode().split('|')
        print('\n')
        logging.info(f'> Has recibido un texto de [{message[1]}]')
        logging.info(f'>> {message[0]}')

    elif root_topic == 'salas':
        message = msg.payload.decode().split('|')
        print('\n')
        logging.info(f'Has recibido un texto de [{message[1]}] en la sala [{topic_by_parts[2]}]')
        logging.info(f'>> {message[0]}')

    elif root_topic == 'comandos':
        # The received byte string is split to read if it is a FRR, OK, NO or ACK.
        byte_string = msg.payload.decode().split('$')
        command = byte_string[0]

        if command.encode() == COMMAND_OK:
            print('\n')
            logging.info('Enviando nota de voz...')
            user.send_recorded_audio()
            logging.info('Nota de voz enviada')
        elif command.encode() == COMMAND_NO:
            print('\n')
            logging.error('NO HA SIDO POSIBLE ENVIAR LA NOTA DE VOZ')
        elif command.encode() == COMMAND_FRR:
            print('\n')
            logging.info('Recibiendo nota de voz...')
            user.receive_audio()
            logging.info('Nota de voz recibida')
            # Ejecución del hilo para play_received_audio


''' Handler functions are set for the MQTT user when there is a connection, 
    a message is received, and a message is posted.'''
user.get_client().on_connect = on_connect
user.get_client().on_publish = on_publish
user.get_client().on_message = on_message

# The username and password for the MQTT broker are set and then the connection is established.
user.get_client().username_pw_set(MQTT_USER, MQTT_PASS)
user.get_client().connect(host=MQTT_HOST, port=MQTT_PORT)

# The thread is started so that the client is attentive to connection, publication and reception events.
user.get_client().loop_start()

# The user subscribes to the corresponding topics.
user.get_client().subscribe([(f'comandos/{GROUP}/{myID}', qos), (f'usuarios/{GROUP}/{myID}', qos)])
for room in myRooms:
    user.get_client().subscribe((f'salas/{GROUP}/{room}', qos))
