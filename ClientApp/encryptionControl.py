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
    :return: The result of the encryption.
    """
    while len(text) % 16 != 0:
        text = text + " "
    return text


# def prepare_file(file): #SERN Este metodo añade bytes al archivo para que se encripte en pedezos de 16bytes
#     while len(file)% 16 != 0:
#         file = file + b'0'
#     return file


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


# def CryptoAudio(archivo):  # SERN Para encriptar archivos
#     cipher = AES.new(key, mode, IV)
#
#     # Nombrar con el nombre de audio grabado en cliente/ o llamar la variable que contenga el archivo.
#     with open(archivo, 'rb') as f:
#        Audio = f.read()
#
#     AudioMod = prepare_file(Audio)
#     AudioEncriptado = cipher.encrypt(AudioMod)
#
#     with open('AudioEncriptado.txt', 'wb') as e:
#        e.write(AudioEncriptado)         # SERN El archivo a enviar ahora sería AudioEncriptado.
#
#
# def DesC_Audio(archivo):    # SERN Para desencriptar archivos
#     cipher = AES.new(key, mode, IV)
#     with open(archivo, 'rb') as fs:
#         AudioEncriptado = fs.read()
#
#     AudioDesencriptado = cipher.decrypt(AudioEncriptado)
#
#     with open('AudioDesencriptado.mp3', 'wb') as es:   # Se le coloca el nombre según como pídio el ingeniero
#         es.write(AudioDesencriptado.rstrip(b'0'))
