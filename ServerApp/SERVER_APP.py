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


def make_audio_sending_process(receiving_user):
    server_commands.send_FRR(receiving_user)
    logging.info(f'Servidor envía >> FRR a {receiving_user}')
    client_connection2, client_add2 = wait_connection()
    print('\n')
    new_print(f'Conexión establecida con {client_add2}', 1)
    logging.info(f'Servidor esta enviando un archivo a {receiving_user}...')
    server.send_file(client_connection)
    logging.info('¡Envió finalizado!')
    client_connection.close()


try:
    new_print('\n********* SERVIDOR MQTT **********', 1, 34)
    while True:
        client_connection, client_add = wait_connection()
        print('\n')
        new_print(f'Conexión establecida con {client_add}', 1)
        logging.info(f'Servidor esta recibiendo un archivo de {server_commands.sender}...')
        server.receive_file(client_connection)
        logging.info('¡Recepción finalizada!')
        client_connection.close()
        # Checking if the receiving user is one or more.
        if type(server_commands.receivers) == list:
            for receiver in server_commands.receivers:
                make_audio_sending_process(receiver)
        else:
            make_audio_sending_process(server_commands.receivers)

except KeyboardInterrupt:
    print('\n')
    logging.warning('\x1b[0;31m'+'CERRANDO EL SERVIDOR...'+'\x1b[;m')
    server_socket.close()
    logging.warning('\x1b[0;31m' + 'DESCONECTÁNDOSE DEL BROKER MQTT...' + '\x1b[;m')

finally:
    server.server.loop_stop()
    server.server.disconnect()
    logging.info('\x1b[0;31m'+'SE HA DESCONECTADO DEL BROKER. SALIENDO...'+'\x1b[;m')
