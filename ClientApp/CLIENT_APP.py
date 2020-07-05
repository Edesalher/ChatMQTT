from setupMqttClient import *
import sys


def new_print(text, style=0, color=37):
    print(f'\x1b[{style};{color}m' + text + '\x1b[;m')


def new_input(text, style=0, color=37):
    return input(f'\x1b[{style};{color}m' + text + '\x1b[;m')


def first_menu():
    new_print('\n¿QUÉ DESEA REALIZAR?', 1, 33)
    new_print('\t1 - Enviar texto', 1, 33)
    new_print('\t2 - Enviar nota de voz', 1, 33)
    new_print('\t3 - Salir de la aplicación', 1, 33)


def second_menu():
    new_print('\n\t¿A QUIÉN ENVIARÁ?', 1, 33)
    new_print('\t\ta - A usuario', 1, 33)
    new_print('\t\tb - A sala', 1, 33)


def menu_options():
    first_menu()
    option = new_input('\n\tOpción > ', 1, 36)

    if option == SEND_TEXT:
        second_menu()
        destination = new_input('\n\tOpción > ', 1, 36)

        if destination == TO_USER:
            destination_user = new_input('\tUser ID > ', 1, 36)
            topic = f'usuarios/{GROUP}/{destination_user}'
            text = new_input('\tEscriba su mensajes >> ', 1, 36)
            message = f'{text}|{myID}'
            user.send_text(topic, message)
        elif destination == TO_ROOM:
            destination_room = new_input('\tSala > ', 1, 36)
            topic = f'salas/{GROUP}/{destination_room}'
            text = new_input('\tEscriba su mensajes >> ', 1, 36)
            message = f'{text}|{myID}'
            user.send_text(topic, message)

    elif option == SEND_VOICE_NOTE:
        second_menu()
        destination = new_input('\n\tOpción > ', 1, 36)

        if destination == TO_USER:
            destination_user = new_input('\tUser ID > ', 1, 36)
            while True:
                duration = new_input('\tIngrese la duración de la nota de voz en seg. > ', 1, 36)
                if int(duration) > 30:
                    print('\n')
                    logging.error('\x1b[0;31m'+'La duración no debe ser mayor a 30 seg.\n'+'\x1b[;m')
                else:
                    break
            print('\n')
            logging.info('Grabando...')
            voice_note = user.record_audio(duration)
            logging.info('Listo')
            user_commands.send_FTR(destination_user, voice_note)
        elif destination == TO_ROOM:
            destination_room = new_input('\tSala > ', 1, 36)
            while True:
                duration = new_input('\tIngrese la duración de la nota de voz en seg. > ', 1, 36)
                if int(duration) > 30:
                    print('\n')
                    logging.error('\x1b[0;31m' + 'La duración no debe ser mayor a 30 seg.\n' + '\x1b[;m')
                else:
                    break
            print('\n')
            logging.info('Grabando...')
            voice_note = user.record_audio(duration)
            logging.info('Listo')
            user_commands.send_FTR(destination_room, voice_note)

    elif option == EXIT:
        print('\n')
        logging.info('\x1b[0;31m'+'CERRANDO APLICACIÓN...'+'\x1b[;m')
        sys.exit()


try:
    new_print('\n********* MENSAJERÍA MQTT **********', 1, 34)
    while True:
        menu_options()

except KeyboardInterrupt:
    print('\n')
    logging.warning('\x1b[0;31m'+'DESCONECTÁNDOSE DEL BROKER MQTT...'+'\x1b[;m')

finally:
    user.get_client().loop_stop()
    user.get_client().disconnect()
    logging.info('\x1b[0;31m'+'SE HA DESCONECTADO DEL BROKER. SALIENDO...'+'\x1b[;m')
