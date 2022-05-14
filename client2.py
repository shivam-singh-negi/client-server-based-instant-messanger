import socket
import select
import errno

HEADER_LENGTH = 10
IP = "127.0.0.1"
PORT = 1234
print("welcome to the instant client server based messanger")
print("You are connected to the server ")
print("you are online ...start sending the messages")
my_username = input("Username: ")
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP, PORT))

# Set connection to non-blocking state, so .recv() call won;t block, just return some exception we'll handle
client_socket.setblocking(False)
username = my_username.encode('utf-8')
username_header = f"{len(username):<{HEADER_LENGTH}}".encode('utf-8')
client_socket.send(username_header + username)

while True:

   message = input(f'{my_username} > ')

   if message:
       message = message.encode('utf-8')
       message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
       client_socket.send(message_header + message)

   try:
       while True:

           # Receive our "header" containing username length, it's size is defined and constant
           username_header = client_socket.recv(HEADER_LENGTH)

           # If we received no data, server gracefully closed a connection, for example using socket.close() or socket.shutdown(socket.SHUT_RDWR)
           if not len(username_header):
               print('Connection closed by the server')
               sys.exit()

           # Convert header to int value
           username_length = int(username_header.decode('utf-8').strip())

           # Receive and decode username
           username = client_socket.recv(username_length).decode('utf-8')

           # Now do the same for message (as we received username, we received whole message, there's no need to check if it has any length)
           message_header = client_socket.recv(HEADER_LENGTH)
           message_length = int(message_header.decode('utf-8').strip())
           message = client_socket.recv(message_length).decode('utf-8')

           # Print message
           print(f'{username} > {message}')

   except IOError as e:

       if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
           print('Reading error: {}'.format(str(e)))
           sys.exit()

       # We just did not receive anything
       continue

   except Exception as e:
       # Any other exception - something happened, exit
       print('Reading error: '.format(str(e)))
       sys.exit()

