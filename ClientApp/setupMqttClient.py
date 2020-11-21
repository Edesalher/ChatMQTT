from myUserMqtt import *
import threading
import encryptionControl as ec

# Initial configuration for logging.
logging.basicConfig(level=logging.INFO,
                    format='\t[%(levelname)s] %(message)s')

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

    if root_topic == 'usuarios' or root_topic == 'salas':
        message = msg.payload
        sender_of_the_message = '-----'
        # If the UnicodeDecodeError exception occurs, it means that the received message is encrypted because
        # it cannot be decoded.
        try:
            received_data = message.decode().split('|')
            message = received_data[0]
            sender_of_the_message = received_data[1]
        except UnicodeDecodeError:
            if encryption:
                decrypted_data = ec.decrypt_message(message)
                received_data = decrypted_data.decode().split('|')
                message = received_data[0]
                sender_of_the_message = received_data[1]
            else:
                pass
        finally:
            print('\n')
            if root_topic == 'usuarios':
                logging.info(f'Has recibido un texto de [{sender_of_the_message}]')
            else:
                logging.info(f'Has recibido un texto de [{sender_of_the_message}] en la sala [{topic_by_parts[2]}]')
            logging.info(f'>> {message}')

    elif root_topic == 'comandos':
        # The received byte string is split to read if the command is a FRR, OK, NO or ACK.
        byte_string = msg.payload.decode().split('$')
        command = byte_string[0]
        ID = byte_string[1]

        if command.encode() == COMMAND_OK or command.encode() == COMMAND_NO:
            if ID == myID:
                user_commands.OKNOID_check = True
                print('\n')
                if command.encode() == COMMAND_OK:
                    logging.info('Enviando nota de voz...')
                    user.send_recorded_audio()
                    logging.info('Nota de voz enviada')
                else:
                    reason = byte_string[2]
                    logging.error('\x1b[0;31m' + f'NO HA SIDO POSIBLE ENVIAR LA NOTA DE VOZ. {reason}\n' + '\x1b[;m')
            else:
                user_commands.OKNOID_check = False

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
                user_commands.ACK_ID_check = True
            else:
                user_commands.ACK_ID_check = False


''' Handler functions are set for the MQTT user when there is a connection, 
    a message is received, and a message is posted.'''
user.client.on_connect = on_connect
user.client.on_publish = on_publish
user.client.on_message = on_message

# The username and password for the MQTT broker are set and then the connection is established.
user.client.username_pw_set(MQTT_USER, MQTT_PASS)
user.client.connect(host=MQTT_HOST, port=MQTT_PORT)  # We connect to the broker.

# The thread is started so that the client is attentive to the events of connection, publication and reception.
user.client.loop_start()

# The user subscribes to the corresponding topics.
user.client.subscribe([(f'comandos/{GROUP}/{myID}', qos), (f'usuarios/{GROUP}/{myID}', qos)])
for room in myRooms:
    user.client.subscribe((f'salas/{GROUP}/{room}', qos))

# A thread is created to send Alives to the server in the "background".
alive_thread = threading.Thread(name='Send Alive',
                                target=user_commands.send_ALIVE,
                                args=(),
                                daemon=True)
alive_thread.start()
