from Crypto.Cipher import AES
import os
import time

encryption = True

key = '1234567891234567'
mode = AES.MODE_CBC
IV = 'ProyectosGrupo19'
duration = 3


def prepare_file(file):
    while len(file) % 16 != 0:
        file = file + b' '
    return file


def do_encryption():
    if encryption:
        cipher = AES.new(key, mode, IV)
        audio_file = open('test.wav', 'rb')
        audio = audio_file.read()
        audio_file.close()
        audio_to_encrypt = prepare_file(audio)
        encrypted_audio = cipher.encrypt(audio_to_encrypt)

        new_audio_file = open('test_encrypted.wav', 'wb')
        new_audio_file.write(encrypted_audio)
        new_audio_file.close()
    else:
        audio_file = open('test.wav', 'rb')
        audio = audio_file.read()
        audio_file.close()

        new_audio_file = open('test_encrypted.wav', 'wb')
        new_audio_file.write(audio)
        new_audio_file.close()


def do_decryption():
    if encryption:
        cipher2 = AES.new(key, mode, IV)
        audio_file2 = open('test_encrypted.wav', 'rb')
        audio = audio_file2.read()
        audio_file2.close()
        decrypted_audio = cipher2.decrypt(audio)
        clean_audio = decrypted_audio.rstrip(b' ')

        new_audio_file = open('test2.wav', 'wb')
        new_audio_file.write(clean_audio)
        new_audio_file.close()
    else:
        audio_file2 = open('test_encrypted.wav', 'rb')
        audio = audio_file2.read()
        audio_file2.close()

        new_audio_file = open('test2.wav', 'wb')
        new_audio_file.write(audio)
        new_audio_file.close()


os.system(f'arecord -d {duration} -f U8 -r 8000 test.wav')
do_encryption()
os.system(f'aplay test.wav')
time.sleep(2)
os.system(f'aplay test_encrypted.wav')
time.sleep(2)
do_decryption()
os.system(f'aplay test2.wav')
