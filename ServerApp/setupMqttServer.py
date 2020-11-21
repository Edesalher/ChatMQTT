from myServerMqtt import *
import logging
import threading

# Initial configuration for logging.
logging.basicConfig(level=logging.INFO,
                    format='[%(levelname)s] %(message)s')

# The users.txt file is read to obtain the data and ID of the users.
users_file = open(USERS_FILENAME, 'r')
registered_users_data = []
registered_IDs = []
for user in users_file:
    user = user.split(',')
    user[-1] = user[-1].rstrip('\n')
    registered_users_data.append(user)
    registered_IDs.append(user[0])
users_file.close()

# The rooms.txt file is read to obtain the rooms to which the users belongs.
rooms_file = open(ROOMS_FILENAME, 'r')
rooms = rooms_file.read()
registered_rooms = rooms.split('\n')
registered_rooms.pop()
rooms_file.close()

# Creating a server for the MQTT broker.
server = MyServer(registered_users_data, registered_IDs, registered_rooms)

# Creating the commands for the server.
server_commands = MyServerCommands(server)

# A user controller is created for the server to handle the list of active users, validations and others.
control = UserControl(server)


# Function that is executed when a connection to the broker MQTT occurs.
def on_connect(client, userdata, rc):
    logging.debug('CONECTADO AL BROKER')


# Function that is executed when a publication occurs.
def on_publish(client, userdata, mid):
    logging.debug('¡Respuesta satisfactoria!')


# Function that is executed when a message reception occurs.
def on_message(client, userdata, msg):
    topic_by_parts = msg.topic.split('/')
    # The received byte string is split to read if it is a FTR or ALIVE command.
    byte_string = msg.payload.decode().split('$')
    command = byte_string[0].encode()

    if command == COMMAND_ALIVE:
        sender = byte_string[1]
        # Checking the validity of the user ID.
        if control.check_validity_of_identifier(sender, 'user'):
            server_commands.sender_ack = sender
            server_commands.flagAlive = True
            control.add_user(sender)
        # Every 2 alive periods, the server updates the list of active users.
        if control.alive_periods == 2:
            control.alive_periods = 0
            control.refresh_active_clients()
        else:
            control.alive_periods += 1
        logging.debug(f'ACTIVOS >>>>>> {control.active_clients}')

    elif command == COMMAND_FTR:
        print('\n')
        logging.info(f'Servidor ha recibido un comando en el topic [{msg.topic}]')
        logging.info(f'Comando << {command}')
        sender = topic_by_parts[2]
        destination_id = byte_string[1]
        # Getting if the destination is a user or room.
        id_type = control.get_type_of_id(destination_id)
        # Checking the validity of the ID.
        if control.check_validity_of_identifier(destination_id, id_type):
            file_size = byte_string[2]
            if id_type == 'room':
                ''' If the destination is a room, first, the users belonging to the room are obtained and then it is 
                    verified which members of the room are online.'''
                members = control.get_members_of_the_room(destination_id)
                online_members = []
                # Checking which member is online.
                for mem in members:
                    if control.check_client_status(mem):
                        online_members.append(mem)
                # Checking if at least one member is online.
                if len(online_members) > 0:
                    server_commands.set_destination_data(sender, members, file_size)
                    server_commands.answer_OK()
                    logging.info('Servidor responde >> OK')
                else:
                    server_commands.answer_NO('LOS DESTINATARIOS NO ESTÁN EN LÍNEA.')
                    logging.info('Servidor responde >> NO --> Ningún miembro de la sala está en línea.')
            else:
                if control.check_client_status(destination_id):
                    server_commands.set_destination_data(sender, destination_id, file_size)
                    server_commands.answer_OK()
                    logging.info('Servidor responde >> OK')
                else:
                    server_commands.answer_NO('EL DESTINATARIO NO ESTÁ EN LÍNEA.')
                    logging.info('Servidor responde >> NO --> El usuario destino no está en línea.')
        else:
            server_commands.answer_NO('EL ID INGRESADO FUÉ INVÁLIDO.')
            logging.info('Servidor responde >> NO --> ID del destino no es válido.')


''' Handler functions are set for the MQTT server when there is a connection, 
    a message is received, and a message is posted.'''
server.server.on_connect = on_connect
server.server.on_publish = on_publish
server.server.on_message = on_message

# The username and password for the MQTT broker are set and then the connection is established.
server.server.username_pw_set(MQTT_USER, MQTT_PASS)
server.server.connect(host=MQTT_HOST, port=MQTT_PORT)

# The thread is started so that the server is attentive to connection, publication and reception events.
server.server.loop_start()

# The server subscribes to the corresponding topics.
server.server.subscribe((f'comandos/{GROUP}/#', qos))
for ID in registered_IDs:
    server.server.subscribe((f'comandos/{GROUP}/{ID}', qos))

# A thread is created to receive Alives from the clients in the "background".
alive_thread = threading.Thread(name='Receive Alive',
                                target=server_commands.answer_ACK,
                                args=(),
                                daemon=True)
alive_thread.start()
