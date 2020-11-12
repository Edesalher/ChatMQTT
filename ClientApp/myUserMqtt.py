from clientData import *
from datetime import datetime, date
import paho.mqtt.client as mqtt
import os
import socket
import time
import logging
import encryptionControl as ec

# Do you want to use encryption?
encryption = True


class MyUser:
    # Constructor method.
    def __init__(self, ID):
        self.client = mqtt.Client(clean_session=True)
        self.userID = ID
        self.recorded_audio = None
        self.audio_received = None

    def send_text(self, destination_topic, msg):
        self.client.publish(destination_topic, msg, qos=qos, retain=False)

    def record_audio(self, duration):
        """
        Description:
        Allows you to record an audio (the voice note) and save the name of the recording.
        The duration must be indicate in seconds.

        :param duration: Duration, in seconds, of the voice note to be recorded.
        :return recorded_audio: The file name of the recorded voice note.
        """
        # current_time = datetime.now()                       # Get the current time.
        # time_date = int(datetime.timestamp(current_time))   # Convert time to UNIX format.
        current_date = date.today()  # Get the current date.
        # self.recorded_audio = f'{time_date}.wav'
        self.recorded_audio = f'AUD-{current_date}.wav'

        os.system(f'arecord -d {duration} -f U8 -r 8000 {self.recorded_audio}')
        os.system(f'mv {self.recorded_audio} VoiceMsj_sent')
        return self.recorded_audio

    def send_recorded_audio(self):
        """
        Description:
        Allows you to send an audio file (the voice note) to the server using a TCP socket.
        The user connects to the server and at the end closes the socket.
        """
        # Creating a socket for the client using IPv4 and TCP.
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client_socket.connect((SERVER_IP, SERVER_PORT))
            audio = open(f'VoiceMsj_sent/{self.recorded_audio}', 'rb')
            client_socket.sendfile(audio, 0)
            audio.close()
        except ConnectionRefusedError:
            print('ERROR! the connection to the server failed.')
        finally:
            client_socket.close()

    def receive_audio(self):
        """
        Description:
        Allows you to receive an audio file (a voice note) from the server using a TCP socket.
        The user connects to the server and at the end closes the socket.
        """
        # current_time = datetime.now()                       # Get the current time.
        # time_date = int(datetime.timestamp(current_time))   # Convert time to UNIX format.
        current_date = date.today()  # Get the current date.
        # self.audio_received = f'{time_date}.wav'
        self.audio_received = f'AUD-{current_date}.wav'
        # Creating a socket for the client using IPv4 and TCP.
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client_socket.connect((SERVER_IP, SERVER_PORT))
            # An audio file is created. It opens in binary and is received.
            audio = open(f'VoiceMsj_received/{self.audio_received}', 'wb')
            while True:
                reception = client_socket.recv(BUFFER_SIZE)  # Reception of the audio file.
                if reception:
                    audio.write(reception)
                else:
                    break
            audio.close()
            if encryption:
                # Only if the received voice note is encrypted will it be able to be decrypted.
                try:
                    ec.decrypt_audio(self.audio_received)
                except ValueError:
                    pass
        except ConnectionRefusedError:
            print('ERROR! the connection to the server failed.')
        finally:
            client_socket.close()

    def play_received_audio(self):
        os.system(f'aplay VoiceMsj_received/{self.audio_received}')


class MyUserCommands:
    # Constructor method.
    def __init__(self, user_object):
        self.user = user_object       # This is the user that has been created.
        self.OKNOID_check = False
        self.ACK_ID_check = True
        self.exit_app = False         # This flag indicates whether the application should be closed or not.

    def send_FTR(self, destination, file):
        """
        Description:
        Allows you to send an FTR command to the server when the user requests to send a voice note.
        First, the structure of the FTR command is created and then it is sent to the corresponding topic.

        :param destination: ID of the room or user to whom the voice note will be sent.
        :param file: File to be sent.
        """
        command = COMMAND_FTR
        send_to = destination.encode()
        file_size = str(os.stat(f'VoiceMsj_sent/{file}').st_size).encode()
        ftr_command = command + b'$' + send_to + b'$' + file_size

        # self.user.publish(f'comandos/{GROUP}/{self.user.userID}', ftr_command, qos=qos, retain=False)
        self.user.send_text(f'comandos/{GROUP}/{self.user.userID}', ftr_command)

    def send_ALIVE(self):
        """
        Description:
        Allows you to send an ALIVE command to the server to indicate that your user is active or online.
        First, the structure of the ALIVE command is created and then it is sent to the corresponding topic.
        """
        command = COMMAND_ALIVE
        myID = self.user.userID.encode()
        alive_command = command + b'$' + myID
        periods = 0

        initial_time = 0
        while not self.exit_app:
            """
            Only in case the server has responded to us with the acknowledge command, the alive command will be sent 
            every 2 seconds.
            
            Every 3 periods, the client tests if the server responds with the ACK command within 2 seconds after
            the AKC_ID_CHECK flag is lowered. In case the server has not responded with the ACK command, the ACK 
            command will be sent every 0.1 seconds.
            """
            if self.ACK_ID_check:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       
                self.user.send_text(f'comandos/{GROUP}', alive_command)
                periods += 1
                if periods == 3:
                    # Check the server response.
                    self.ACK_ID_check = False
                    periods = 0
                time.sleep(ALIVE_PERIOD)  # 2 seconds
                initial_time = time.time()
            else:
                self.user.send_text(f'comandos/{GROUP}', alive_command)
                time.sleep(ALIVE_CONTINUOUS)  # 0.1 seconds
                """
                If the time is up and the server did not respond, the exit flag is set to True to indicate that 
                the application should close.
                """
                if time.time() > initial_time + 5:
                    if not self.ACK_ID_check:
                        self.exit_app = True
                        print('\n')
                        logging.critical('\x1b[0;31m' + 'SERVIDOR NO RESPONDE.' + '\x1b[;m')
                        break
