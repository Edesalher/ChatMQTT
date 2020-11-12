from Crypto.Cipher import AES
import hashlib

# Password for encrypt and decrypt.
password = "proyectos_g19".encode()
# A hashing function is used to make the password a random string of characters that is always 32 bytes long.
key = hashlib.sha3_256(password).digest()

mode = AES.MODE_CBC
IV = 'ProyectosGrupo19'


def prepare_message(text):
    """
    Description:
    This function adds characters (blanks) to make the message be a multiple of 16 so that it can be encrypted
    by the encrypt() function of AES. These blanks must be removed when decrypting.

    :param text: The text or character string to be encrypted.
    :return: The new text.
    """
    while len(text) % 16 != 0:
        text = text + " "
    return text


def prepare_file(file):
    """
    Description:
    This function adds characters (blanks) in binary to make the audio be a multiple of 16 bytes so that it can be
    encrypted by the encrypt() function of AES. These blanks must be removed when decrypting.

    :param file: The audio file (voice note) to be encrypted.
    :return: The new audio file.
    """
    while len(file) % 16 != 0:
        file = file + b' '
    return file


def encrypt_message(text):
    # Creating the cipher with AES.
    cipher = AES.new(key, mode, IV)
    message = prepare_message(text)
    encrypted_message = cipher.encrypt(message)
    return encrypted_message


def decrypt_message(text):
    # Creating de cipher with AES.
    cipher = AES.new(key, mode, IV)
    # The message is decrypted and the blanks are removed.
    decrypted_message = cipher.decrypt(text).rstrip()
    return decrypted_message


def encrypt_audio(audio_file):
    # Creating the cipher with AES.
    cipher = AES.new(key, mode, IV)
    audio = open(f'VoiceMsj_sent/{audio_file}', 'rb')
    data = audio.read()
    audio.close()
    data_to_encrypt = prepare_file(data)
    encrypted_data = cipher.encrypt(data_to_encrypt)
    # The audio file is overwritten with the encrypted data.
    encrypted_audio = open(f'VoiceMsj_sent/{audio_file}', 'wb')
    encrypted_audio.write(encrypted_data)
    encrypted_audio.close()


def decrypt_audio(audio_file):
    # Creating the cipher with AES.
    cipher = AES.new(key, mode, IV)
    audio2 = open(f'VoiceMsj_received/{audio_file}', 'rb')
    data2 = audio2.read()
    audio2.close()
    decrypted_data = cipher.decrypt(data2)
    clean_data = decrypted_data.rstrip(b' ')
    # The audio file is overwritten with the decrypted and clean data.
    decrypted_audio = open(f'VoiceMsj_received/{audio_file}', 'wb')
    decrypted_audio.write(clean_data)
    decrypted_audio.close()
