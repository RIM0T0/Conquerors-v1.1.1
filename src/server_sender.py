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
