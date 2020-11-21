# Connection parameters for MQTT broker.
MQTT_HOST = '192.168.1.18'  # IP of my RPi4.
# MQTT_HOST = 'localhost'
MQTT_PORT = 1883

# Connections credentials for MQTT broker.
MQTT_USER = "rpi"
MQTT_PASS = "raspi4"

# Connection parameters for TCP.
SERVER_IP = '192.168.1.18'  # IP of my RPi4.
# SERVER_IP = 'localhost'
SERVER_PORT = 9819

# Configuration file names for the server.
USERS_FILENAME = 'users.txt'
ROOMS_FILENAME = 'rooms.txt'

# Commands
COMMAND_FRR = b'\x02'
COMMAND_FTR = b'\x03'
COMMAND_ALIVE = b'\x04'
COMMAND_ACK = b'\x05'
COMMAND_OK = b'\x06'
COMMAND_NO = b'\x07'

# Constants
GROUP = '19'
ALIVE_PERIOD = 2            # Period between sending commands ALIVE.
ALIVE_CONTINUOUS = 0.1      # Period between sending commands ALIVE if there is no answer.
BUFFER_SIZE = 64 * 1024     # 64KB.
qos = 2                     # Quality of Service to use.
