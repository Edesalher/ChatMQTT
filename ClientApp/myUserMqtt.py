from brokerData import *
from datetime import datetime
import paho.mqtt.client as mqtt
import os
import socket
import time

# Creating a socket for the client using IPv4 and TCP.
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


class MyUser:
    # Constructor method.
    def __init__(self, ID):
        self.client = mqtt.Client(clean_session=True)
        self.userID = ID
        self.recorded_audio = None
        self.audio_received = None

    # Allows you to get the object that represents the user.
    def get_client(self):
        return self.client

    def send_text(self, destination_topic, msg):
        self.client.publish(destination_topic, msg, qos=qos, retain=False)

    # Allows you to record an audio (the voice note) and save the name of the recording file.
    def record_audio(self, duration):
        current_time = datetime.now()                       # Get the current time.
        time_date = int(datetime.timestamp(current_time))   # Convert time to UNIX format.
        self.recorded_audio = f'{time_date}.wav'

        os.system(f'arecord -d {duration} -f U8 -r 8000 {self.recorded_audio}')
        os.system(f'mv {self.recorded_audio} VoiceMsj_sent')
        return self.recorded_audio

    '''Allows you to send an audio file (the voice note) to the server using a TCP socket.
        The user connects to the server and at the end closes the socket.'''
    def send_recorded_audio(self):
        audio = open(f'VoiceMsj_sent/{self.recorded_audio}', 'rb')
        client_socket.connect((SERVER_IP, SERVER_PORT))
        client_socket.sendfile(audio, 0)
        client_socket.close()
        audio.close()

    # Allows you to receive an audio file (a voice note) from the server using a TCP socket.
    def receive_audio(self):
        current_time = datetime.now()                       # Get the current time.
        time_date = int(datetime.timestamp(current_time))   # Convert time to UNIX format.
        self.audio_received = f'{time_date}.wav'

        '''An audio file is created. It opens in binary and is received. 
            The user connects to the server and at the end closes the socket.'''
        audio = open(f'VoiceMsj_received/{self.audio_received}', 'wb')
        client_socket.connect((SERVER_IP, SERVER_PORT))
        while True:
            reception = client_socket.recv(BUFFER_SIZE)
            if reception:
                audio.write(reception)
            else:
                break
        client_socket.close()
        audio.close()

    def play_received_audio(self):
        os.system(f'aplay VoiceMsj_received/{self.audio_received}')


class MyUserCommands:
    # Constructor method.
    def __init__(self, user_object):
        self.user = user_object       # This is the user that has been created.

    '''Allows you to send an FTR command to the server when the user requests to send a voice note. 
    First, the structure of the FTR command is created and then it is sent to the corresponding topic.'''
    def send_FTR(self, destination, file):
        command = COMMAND_FTR
        send_to = destination.encode()
        file_size = str(os.stat(f'VoiceMsj_sent/{file}').st_size).encode()
        ftr_command = command + b'$' + send_to + b'$' + file_size

        # self.user.publish(f'comandos/{GROUP}/{self.user.userID}', ftr_command, qos=qos, retain=False)
        self.user.send_text(f'comandos/{GROUP}/{self.user.userID}', ftr_command)