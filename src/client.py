'''
Copyright (C) 2026 Rimantas Rimkevičius

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see https://www.gnu.org/licenses/
'''

import socket
from common import FORMAT, BUFFER, PORT

game_status = 'MENIU'

def connect(server_ip):
    global client
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.settimeout(2) # 2 sekundes jungimuisi, kad neatsibostu laukti
        client.connect((server_ip, PORT))
        client.settimeout(None) # kai sekmingai prisijungia, grazinu timeout i iprasta reiksme, kuri leidzia klientui laukti kiek tik reikia sekanciu paketu is serverio po prisijungimo
        return 'success'
    except (socket.gaierror, TimeoutError, OSError):
        return 'fail'

def disconnect():
    client.close()

def is_connected(): # ping'inu serveri
    try:
        client.send(format_msg('ping'))
        return True
    except ConnectionError:
        return False

def format_msg(msg):
    message = f'{game_status}#{msg}'
    return str( message + ' ' * (BUFFER - len(message)) ).encode(FORMAT)
def send(msg):
    client.send(format_msg(msg))

def recv():
    return client.recv(BUFFER).decode(FORMAT).strip()
