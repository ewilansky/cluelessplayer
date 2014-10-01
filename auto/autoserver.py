import socket
import json
import automaton


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def start():
    # socket create
    # sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # port bind
    server_address = ('localhost', 10000)
    print('starting server on {0} port {1}'.format(server_address[0], server_address[1]))
    sock.bind(server_address)

    # place the socket in server mode to listen for incoming connections
    sock.listen(1)

    # wait for incoming connections
    while True:
        print('waiting for connection')
        # accept returns a new client socket connection on this server and the client address making the connection
        connection, client_address = sock.accept()

        try:
            # receive json data in 1024 chunks
            data = json.loads(connection.recv(1024).decode('UTF-8').strip())

            print('connection from {}'.format(client_address))
            if data:
                # if the message type is enter_game, instantiate automaton class
                # and send the class the list of available players
                if data['msg_type'] == 'enter_game':
                    available_players = ['mustard', 'white', 'scarlet']
                    # class returns an available player to use
                    auto_player_01 = automaton.Player(available_players);
                    # get the string length to determine the length of the message

                    print('sending selected player {}'.format(auto_player_01.selected_player))
                    connection.sendall(bytes(json.dumps({'return': '{}'.format(auto_player_01.selected_player)}), 'UTF-8'))

                else:
                    print('sending json ack back to client')
                    connection.sendall(bytes(json.dumps({'return':'ok'}), 'UTF-8'))
            else:
                print('no more data from {}', client_address)
                break
        except Exception as e:
            print('exception thrown while receiving data {}'.format(e))
        finally:
            # remove the connection
            connection.close()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', action='store', help='start server (-start)', default='tart')
    print('ctrl + z to shutdown')

    args = parser.parse_args()

    if args.s == "tart":
         start()
    else:
        print('invalid or no argument provided')
