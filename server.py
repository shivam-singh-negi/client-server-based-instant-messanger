import socket
import select

HEAD_LEN = 10

IP = "127.0.0.1"
PORT = 1234

# Creating a socket
ser_socket = socket.socket(socket.AF_INET,
                          socket.SOCK_STREAM)  # socket.AF_INET - IPv4 addresing , socket.SOCK_STREAM - TCP
ser_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,
                     1)  # SO_ - socket option ,SOL_-socket option level, Sets REUSEADDR (To using the address again)to 1 on socket
ser_socket.bind((IP, PORT))  # Bind, tells the system that it's going to use given IP and port
ser_socket.listen()  # listening to new connections
sock_list = [ser_socket]  # List of sockets for select.select()
requesting_clients = {}  # List of connected clients - {socket:[user header, data]} format
print("Welcome to instant client server based messanger")
print("starting the server .......")
print(f' Waiting for any  connection request at : IP:PORT: {IP}:{PORT}...')


def receive_message(user_socket):
   try:

       # message length, it's size is defined and constant
       mes_head = user_socket.recv(HEAD_LEN)
       # If we received no data, client gracefully closed a connection
       if not len(mes_head):
           return False
       # Convert header to int value
       mes_len = int(mes_head.decode('utf-8').strip())
       return {'header': mes_head, 'data': user_socket.recv(mes_len)}  # Return  message header and message data
   except:
       # if the connection is lost of the client closes the script
       return False


while True:

   # Returns lists:
   know_sockets, _, problem_sockets = select.select(sock_list, [],
                                                  sock_list)  # it will be return 3 list, one containt the recieved data, sockets through which data can be send and the sockets having errors
   for test_socket in know_sockets:  # iterating thorugh the recieved sockets

       if test_socket == ser_socket:  # if ture then accept the connection

           # The other returned object is ip/port set
           client_socket, client_address = ser_socket.accept()  # here we get the IP/port adddress of the accepted connection

           user = receive_message(client_socket)  # receiving the data from the given port "client_socket"

           if user is False:  # If False refers that the  client  is disconnected before he sent his name
               continue

           sock_list.append(client_socket)  # adding the accepet socket to the buffer

           requesting_clients[
               client_socket] = user  # here mapping the "user name" and "user header" to the accepted socket in the dictionary

           print('Approving the incoming connection from {}:{}, username: {}'.format(*client_address,
                                                                                     user['data'].decode(
                                                                                         'utf-8')))  # printing results of data recieved

       else:  # if the test_socket is not same as server_socket it means the socket is sending a message not receiveing one
           message = receive_message(test_socket)  # Receive message

           # If False, client disconnected, cleanup
           if message is False:
               print('Closed connection from: {}'.format(requesting_clients[test_socket]['data'].decode('utf-8')))
               sock_list.remove(test_socket)  # Removing the socket entry from list
               del requesting_clients[test_socket]  # Removing the socket entry from client dictionary
               continue
           user = requesting_clients[
               test_socket]  # extracting the user details from the client dictionary using test_socket(key )

           print(f'Received message from {user["data"].decode("utf-8")}: {message["data"].decode("utf-8")}')

           for client_socket in requesting_clients:  # now we need to broadcast the message from 1 client to all the other excluding the sender
               if client_socket != test_socket:
                   client_socket.send(user['header'] + user['data'] + message['header'] + message[
                       'data'])  # broadcasting in the given format
   for test_socket in problem_sockets:  # for handling exceptions
       # Remove from list for socket.socket()
       sock_list.remove(test_socket)
       # Remove from our list of users
       del requesting_clients[test_socket]
