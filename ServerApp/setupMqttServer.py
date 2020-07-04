from myServerMqtt import *
import logging

# Initial configuration for logging.
logging.basicConfig(level=logging.INFO,
                    format='[%(levelname)s] %(message)s')

# The usuarios.txt file is read to obtain the data and ID of the users.
users_file = open(USERS_FILENAME, 'r')
registered_users = []
registered_IDs = []
for user in users_file:
    user = user.split(',')
    registered_users.append(user)
    registered_IDs.append(user[0])
users_file.close()

# The salas.txt file is read to obtain the rooms to which the user belongs.
rooms_file = open(ROOMS_FILENAME, 'r')
myRooms = rooms_file.read()
myRooms = myRooms.split('\n')
myRooms.pop()
rooms_file.close()

# Creating a server for the MQTT broker.
server = MyServer()

# Creating the commands for the server.
server_commands = MyServerCommands(server)


# Function that is executed when a connection to the broker MQTT occurs.
def on_connect(client, userdata, rc):
    logging.debug('CONECTADO AL BROKER')


# Function that is executed when a publication occurs.
def on_publish(client, userdata, mid):
    logging.info('¡Respuesta satisfactoria!')


# Function that is executed when a message reception occurs.
def on_message(client, userdata, msg):
    print('\n')
    logging.info(f'Servidor ha recibido un comando en el topic [{msg.topic}]')
    topic_by_parts = msg.topic.split('/')
    # The received byte string is split to read if it is a FTR or ALIVE.
    byte_string = msg.payload.decode().split('$')
    command = byte_string[0]
    logging.info(f'Comando << {command.encode()}')

    if command.encode() == COMMAND_FTR:
        sender = topic_by_parts[2]
        destination_ID = byte_string[1]
        file_size = byte_string[2]
        server_commands.set_destination(sender, destination_ID, file_size)

        server_commands.answer_OK()
        logging.info('Servidor responde >> OK')


''' Handler functions are set for the MQTT server when there is a connection, 
    a message is received, and a message is posted.'''
server.get_server().on_connect = on_connect
server.get_server().on_publish = on_publish
server.get_server().on_message = on_message

# The username and password for the MQTT broker are set and then the connection is established.
server.get_server().username_pw_set(MQTT_USER, MQTT_PASS)
server.get_server().connect(host=MQTT_HOST, port=MQTT_PORT)

# The thread is started so that the server is attentive to connection, publication and reception events.
server.get_server().loop_start()

# The server subscribes to the corresponding topics.
server.get_server().subscribe((f'comandos/{GROUP}/#', qos))
for ID in registered_IDs:
    server.get_server().subscribe((f'comandos/{GROUP}/{ID}', qos))
