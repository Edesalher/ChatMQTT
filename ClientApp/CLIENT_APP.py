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


def check_exit_app_flag():
    if user_commands.exit_app:
        sys.exit()


def menu_options():
    first_menu()
    while True:
        valid_options = ('1', '2', '3')
        option = new_input('\n\tOpción > ', 1, 36)
        check_exit_app_flag()
        if option in valid_options:
            break
        else:
            logging.warning('\x1b[0;31m' + 'Ups! esa opción no es válida.' + '\x1b[;m')

    if option == SEND_TEXT:
        second_menu()
        while True:
            valid_options2 = ('a', 'b')
            destination = new_input('\n\tOpción > ', 1, 36)
            check_exit_app_flag()
            if destination in valid_options2:
                break
            else:
                logging.warning('\x1b[0;31m' + 'Ups! esa opción no es válida.' + '\x1b[;m')
        if destination == TO_ROOM:
            destination_room = new_input('\tSala > ', 1, 36)
            topic = f'salas/{GROUP}/{destination_room}'
        else:
            destination_user = new_input('\tUser ID > ', 1, 36)
            topic = f'usuarios/{GROUP}/{destination_user}'

        check_exit_app_flag()
        text = new_input('\tEscriba su mensajes >> ', 1, 36)
        check_exit_app_flag()
        message = f'{text}|{myID}'
        if encryption:
            encrypted_message = ec.encrypt_message(message)
            user.send_text(topic, encrypted_message)
        else:
            user.send_text(topic, message)

    elif option == SEND_VOICE_NOTE:
        second_menu()
        while True:
            valid_options2 = ('a', 'b')
            destination = new_input('\n\tOpción > ', 1, 36)
            check_exit_app_flag()
            if destination in valid_options2:
                break
            else:
                logging.warning('\x1b[0;31m' + 'Ups! esa opción no es válida.' + '\x1b[;m')
        if destination == TO_ROOM:
            destination = new_input('\tSala > ', 1, 36)
        else:
            destination = new_input('\tUser ID > ', 1, 36)
        check_exit_app_flag()
        while True:
            try:
                duration = int(new_input('\tIngrese la duración de la nota de voz en seg. > ', 1, 36))
                check_exit_app_flag()
                if duration > 30:
                    logging.error('\x1b[0;31m' + 'La duración no debe ser mayor a 30 seg.' + '\x1b[;m')
                else:
                    break
            except ValueError:
                logging.warning('\x1b[0;31m' + 'Ups! debes ingresar un número.' + '\x1b[;m')
        print('\n')
        logging.info('Grabando...')
        voice_note = user.record_audio(duration)
        if encryption:
            ec.encrypt_audio(voice_note)
        logging.info('Listo')
        user_commands.send_FTR(destination, voice_note)

    elif option == EXIT:
        print('\n')
        logging.info('\x1b[0;31m'+'CERRANDO LA APLICACIÓN...'+'\x1b[;m')
        sys.exit()


try:
    new_print('\n********* MENSAJERÍA MQTT **********', 1, 34)
    while not user_commands.exit_app:
        menu_options()

except KeyboardInterrupt:
    print('\n')
    logging.warning('\x1b[0;31m'+'DESCONECTÁNDOSE DEL BROKER MQTT...'+'\x1b[;m')

finally:
    user.client.loop_stop()
    user.client.disconnect()
    logging.info('\x1b[0;31m'+'SE HA DESCONECTADO DEL BROKER. SALIENDO...'+'\x1b[;m')
