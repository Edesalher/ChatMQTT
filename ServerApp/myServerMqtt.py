from serverData import *
import paho.mqtt.client as mqtt
import socket

# Creating a socket for the server using IPv4 and TCP.
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print(f'\x1b[1;36m'+f'\nIniciando servidor "{SERVER_IP}" en el puerto "{SERVER_PORT}"...'+'\x1b[;m')
server_socket.bind((SERVER_IP, SERVER_PORT))
server_socket.listen(1)
print(f'\x1b[1;36m'+f'¡Servidor iniciado!'+'\x1b[;m')


class MyServer:
    # Constructor method.
    def __init__(self, users_data, ids_list, rooms_list):
        self.server = mqtt.Client(clean_session=True)
        self.registered_users_data = users_data
        self.registered_ids = ids_list
        self.registered_rooms = rooms_list

    def send_text(self, destination_topic, msg):
        self.server.publish(destination_topic, msg, qos=qos, retain=False)

    def send_file(self, connection):
        """
        Description:
        Allows the server to send an audio file (a voice note) to a client using a TCP socket.
        The client connects to the server and at the end closes the socket.

        :param connection: The connection received from a TCP client.
        """
        audio = open(f'VoiceMsj_received/received.wav', 'rb')
        connection.sendfile(audio, 0)
        audio.close()

    def receive_file(self, client_connection):
        """
        Description:
        Allows the server to receive an audio file (a voice note) from a client using a TCP socket.
        The client connects to the server and at the end closes the socket.

        :param client_connection: The connection received from a TCP client.
        """
        # An audio file is created. It opens in binary and is received.
        audio = open(f'VoiceMsj_received/received.wav', 'wb')
        while True:
            reception = client_connection.recv(BUFFER_SIZE)
            if reception:
                audio.write(reception)
            else:
                break
        audio.close()


class MyServerCommands:
    # Constructor method.
    def __init__(self, server_object):
        self.server = server_object       # This is the server that has been created.
        self.sender = None
        self.receivers = None
        self.file_size = None
        self.flagAlive = False
        self.sender_ack = ''

    def set_destination_data(self, receivers, file_size):
        """
        Description:
        This function allows to set who is the sender, who are the recipients and the size of the file
        to send.

        :param sender: User sending the audio file.
        :param receivers: User or users who will receive the audio file.
        :param file_size: Size of the audio file.
        """
        self.receivers = receivers
        self.file_size = file_size

    def send_FRR(self, destination_user):
        """
        Description:
        Allows the server to send an FRR command to the client when a user requests to send a voice note.
        First, the structure of the FRR command is created and then it is sent to the corresponding topic.
        """
        command = COMMAND_FRR
        sent_by = self.sender.encode()
        file_size = self.file_size.encode()
        frr_command = command + b'$' + sent_by + b'$' + file_size

        self.server.send_text(f'comandos/{GROUP}/{destination_user}', frr_command)

    def answer_OK(self):
        """
        Description:
        Allows the server to respond an OK to the client when a condition has been met.
        First, the structure of the OK command is created and then it is sent to the corresponding topic.
        """
        command = COMMAND_OK
        reply_to = self.sender.encode()
        ok_command = command + b'$' + reply_to

        # self.server.publish(f'comandos/{GROUP}/{reply_to}', ok_command, qos=qos, retain=False)
        self.server.send_text(f'comandos/{GROUP}/{reply_to.decode()}', ok_command)

    def answer_NO(self, reason):
        """
        Description:
        Allows the server to respond NO to the client when a condition has not been met.
        First, the structure of the NO command is created and then it is sent to the corresponding topic.
        """
        command = COMMAND_NO
        reply_to = self.sender.encode()
        reason = reason.encode()
        no_command = command + b'$' + reply_to + b'$' + reason

        self.server.send_text(f'comandos/{GROUP}/{reply_to.decode()}', no_command)

    def answer_ACK(self):
        """
        Description:
        Allows the server to respond an ACK to the client when a condition has been met.
        First, the structure of the ACK command is created and then it is sent to the corresponding topic.
        """
        command = COMMAND_ACK
        while True:
            reply_to = self.sender_ack.encode()
            ack_command = command + b'$' + reply_to
            if self.flagAlive:
                self.server.send_text(f'comandos/{GROUP}/{reply_to.decode()}', ack_command)
                self.flagAlive = False
            else:
                pass


class UserControl:
    # Constructor method.
    def __init__(self, server_object):
        self.server = server_object  # This is the server that has been created.
        self.alives_received = []    # Temporary list for the received alives.
        self.active_clients = []     # This is the list of active clients.
        self.alive_periods = 0       # Stores the number of alive periods that have passed.

    def add_user(self, user):
        """
        Description:
        Determines if a user is already on the alives received list.
        If the user is in the list, it is not added. If the user is not in the list, it is added.

        :param user: User ID.
        """
        in_list = False
        for item in self.alives_received:
            if item == user:
                in_list = True
                break
        if in_list:
            pass
        else:
            self.alives_received.append(user)

    def refresh_active_clients(self):
        """
        Description:
        Allows the server to refresh the list of active clients using the temporary list of received alives.
        """
        self.active_clients = self.alives_received.copy()
        self.alives_received.clear()

    def check_client_status(self, user):
        """
        Description:
        Check if a user is active using the list of active clients.

        :param user: user ID.
        """
        active = False
        for active_user in self.active_clients:
            if user == active_user:
                active = True
                break
        return active

    def get_type_of_id(self, id_to_verify):
        id_type = 'user'
        for ID in self.server.registered_rooms:
            if ID == id_to_verify:
                id_type = 'room'
                break
        return id_type

    def check_validity_of_identifier(self, id_to_validate, id_type):
        it_is_valid = False
        # Depending on the type of ID, it is choose which list should be read.
        if id_type == 'user':
            for ID in self.server.registered_ids:
                if ID == id_to_validate:
                    it_is_valid = True
                    break
        else:
            for room in self.server.registered_rooms:
                if room == id_to_validate:
                    it_is_valid = True
                    break
        return it_is_valid

    def get_members_of_the_room(self, room_id):
        """
        Description:
        Each user is taken from the list and their data is read to verify if the ID of the indicated room is part of
        their data. This means that the user belongs to the indicated room.

        :param room_id: ID of the room of interest.
        :return: A list with the members that belong to the room.
        """
        members = []
        for user in range(len(self.server.registered_users_data)):
            for user_data in self.server.registered_users_data[user]:
                if user_data == room_id:
                    members.append(self.server.registered_users_data[user][0])
                    break
        return members
