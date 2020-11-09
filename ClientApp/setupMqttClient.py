from myUserMqtt import *
import threading

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
def on_connect(client, userdata, flags, rc):
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
        ID = byte_string[1]

        if command.encode() == COMMAND_OK:
            if ID == myID:
                user_commands.set_oknoIDcheck_flag(True)
                print('\n')
                logging.info('Enviando nota de voz...')
                user.send_recorded_audio()
                logging.info('Nota de voz enviada')
            else:
                user_commands.set_oknoIDcheck_flag(False)
        elif command.encode() == COMMAND_NO:
            if ID == myID:
                user_commands.set_oknoIDcheck_flag(True)
                print('\n')
                logging.error('\x1b[0;31m' + 'NO HA SIDO POSIBLE ENVIAR LA NOTA DE VOZ\n' + '\x1b[;m')
            else:
                user_commands.set_oknoIDcheck_flag(False)
        elif command.encode() == COMMAND_FRR:
            print('\n')
            logging.info(f'Has recibido una nota de voz de [{ID}]')
            logging.info('Recibiendo...')
            user.receive_audio()
            logging.info('Nota de voz recibida')
            logging.info('Reproduciendo nota de voz...')
            # A thread is created to play the received voice note in the "background".
            audio_thread = threading.Thread(name='Audio playback',
                                            target=user.play_received_audio,
                                            args=(),
                                            daemon=False)
            audio_thread.start()
        elif command.encode() == COMMAND_ACK:
            if ID == myID:
                user_commands.set_ackIDcheck_flag(True)
            else:
                user_commands.set_ackIDcheck_flag(False)


''' Handler functions are set for the MQTT user when there is a connection, 
    a message is received, and a message is posted.'''
user.get_client().on_connect = on_connect
user.get_client().on_publish = on_publish
user.get_client().on_message = on_message

# The username and password for the MQTT broker are set and then the connection is established.
user.get_client().username_pw_set(MQTT_USER, MQTT_PASS)
user.get_client().connect(host=MQTT_HOST, port=MQTT_PORT)  # We connect to the broker.

# The thread is started so that the client is attentive to the events of connection, publication and reception.
user.get_client().loop_start()

# The user subscribes to the corresponding topics.
user.get_client().subscribe([(f'comandos/{GROUP}/{myID}', qos), (f'usuarios/{GROUP}/{myID}', qos)])
for room in myRooms:
    user.get_client().subscribe((f'salas/{GROUP}/{room}', qos))

# A thread is created to send Alives to the server in the "background".
alive_thread = threading.Thread(name='Send Alive',
                                target=user_commands.send_ALIVE,
                                args=(),
                                daemon=True)
alive_thread.start()
