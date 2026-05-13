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

from common import FORMAT, BUFFER

def format_msg(msg):
    return str( msg + ' ' * (BUFFER - len(msg)) ).encode(FORMAT)

queue = []

def start_sending():
    global queue
    while 1:
        if len(queue) > 0:
            sockets, msg = queue[0]
            
            for socket in sockets:
                try:
                    socket.send(format_msg(msg))
                except ConnectionError:
                    pass

            queue.pop(0)
