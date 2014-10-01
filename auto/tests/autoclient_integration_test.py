import socket
import json
import unittest

# socket mocking framework to turn this into a unit test...
# from mocket.mocket import Mocket, Mocketizer, MocketEntry


class AutoClientIntegrationTest(unittest.TestCase):
    def setUp(self):
        # connect socket to server
        server_address = ('localhost', 10000)
        print('connecting to {0} port {1}'.format(server_address[0], server_address[1]))
        try:
            self.socket = socket.create_connection(server_address)
        except ConnectionRefusedError:
            print('unable to connect to the socket server.')
            return

    def tearDown(self):
        print('closing client socket')
        self.socket.close()

    def send_receive(self, send_msg):
        print('sending {} to server'.format(send_msg))
        self.socket.sendall(bytes(json.dumps(send_msg), 'UTF-8'))
        # receive response
        received = 0
        expected = len(send_msg)
        while received < expected:
            received_msg = json.loads(self.socket.recv(1024).decode('UTF-8'))
            received += len(received_msg)
            print('received {0}', received_msg)
        return received_msg

    def test_should_return_json_formatted_ack_from_server(self):
        """
        Test that a simple json object literal acknowledging success is received from the server.
        """
        send_msg = {'msg_type':'json test'}
        received_msg = self.send_receive(send_msg)

        self.assertEqual({'return':'ok'}, received_msg, 'the message returned was not a json ack')

    def test_should_send_enter_game_and_return_ack_from_server(self):
        """
        Test that a game entry request should occur and return list of available players
        :return: one of these player: ["mustard", "scarlet", "white"]}'}
        """

        send_msg = {'msg_type':'enter_game'}
        received_msg = self.send_receive(send_msg)

        # player returned
        print(received_msg)

        self.assertTrue(received_msg == 'mustard' or 'scarlet' or 'white')

