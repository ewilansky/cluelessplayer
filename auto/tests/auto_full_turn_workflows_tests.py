import unittest
import logging
import sys

from auto.automaton import Player


class AutoFullTurnWorkflowsUnitTests(unittest.TestCase):
    """
    Testing the automaton player's taken turn move actions
    """

    def setUp(self):
        """
        unittest class setup

        :var available players list for most tests in this class
        :var an instantiated player object
        """
        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

        # available_suspects = ['Peacock', 'Plum', 'Green', 'Mustard']
        #
        # # create a computer player and specify the total number of players in this game
        # self.player = Player('p04', available_suspects, 4)
        # # with four players, 2 players will get 4 cards and 2 players will get 5 cards
        #
        # # receive cards from dealer
        # self.dealt_cards = ['Wrench', 'Green', 'Study', 'Hall']
        # self.player.receive_cards(self.dealt_cards)

    def test_move_suggest(self):
        pass

    def test_move_accuse(self):
        pass

    def test_move_suggest_accuse(self):
        pass

    def test_accuse(self):
        pass

    def move(self):
        # mark everything as known except a location that this player must move
        # to in multiple turns before making a suggestion
        pass