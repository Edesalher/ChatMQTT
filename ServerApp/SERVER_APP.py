from setupMqttServer import *


def new_print(text, style=0, color=37):
    print(f'\x1b[{style};{color}m' + text + '\x1b[;m')


def new_input(text, style=0, color=37):
    return input(f'\x1b[{style};{color}m' + text + '\x1b[;m')


def wait_connection():
    new_print('\nEsperando conexión...', 1, 33)
    # The server receive the connection of the client and at the end closes the socket.
    connection, client_address = server_socket.accept()
    return connection, client_address


try:
    new_print('\n********* SERVIDOR MQTT **********', 1, 34)
    while True:
        client_connection, client_add = wait_connection()
        print('\n')
        new_print(f'Conexión establecida con {client_add}', 1)
        logging.info('Servidor esta recibiendo un archivo...')
        server.receive_file(client_connection)
        logging.info('¡Recepción finalizada!')
        client_connection.close()
        server_commands.send_FRR()
        logging.info('Servidor envía >> FRR')

        client_connection, client_add = wait_connection()
        print('\n')
        new_print(f'Conexión establecida con {client_add}', 1)
        logging.info('Servidor esta enviando un archivo...')
        server.send_file(client_connection)
        logging.info('¡Envió finalizado!')
        client_connection.close()

except KeyboardInterrupt:
    print('\n')
    logging.warning('\x1b[0;31m'+'CERRANDO EL SERVIDOR...'+'\x1b[;m')
    server_socket.close()
    logging.warning('\x1b[0;31m' + 'DESCONECTÁNDOSE DEL BROKER MQTT...' + '\x1b[;m')

finally:
    server.get_server().loop_stop()
    server.get_server().disconnect()
    logging.info('\x1b[0;31m'+'SE HA DESCONECTADO DEL BROKER. SALIENDO...'+'\x1b[;m')
