import unittest
import itertools
import logging
import sys

from auto.automaton import Player


class AutoCoreUnitTests(unittest.TestCase):
    """
    Testing the automaton player's core functions associated with instantiation
    """

    def setUp(self):
        """
        unittest class setup

        :var available players list for most tests in this class
        :var an instantiated player object
        """
        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

        available_suspects = ['Peacock', 'Plum', 'Green', 'Mustard']

        # create a computer player and specify the total number of players in this game
        self.player = Player('p04', available_suspects, 4)
        # with four players, 2 players will get 4 cards and 2 players will get 5 cards

        # receive cards from dealer
        self.dealt_cards = ['Wrench', 'Green', 'Study', 'Hall']
        self.player.receive_cards(self.dealt_cards)

    def test_player_instantiated(self):
        """
        Test that a player object was returned.
        """
        self.assertTrue(self.player)
        self.assertTrue(self.player._selected_suspect == 'Peacock' or 'Plum' or 'Green' or 'Mustard')

    def test_selected_player_in_correct_starting_position(self):
        """
        Since no moves have been made, test that the instantiated player should be in the correct starting position.
        """
        starting_position = self.player._get_starting_location(self.player._selected_suspect)

        if self.player._selected_suspect == 'Peacock':
            self.assertTrue(starting_position == 'Hallway_07')
        elif self.player._selected_suspect == 'Plum':
            self.assertTrue(starting_position == 'Hallway_08')
        elif self.player._selected_suspect == 'Green':
            self.assertTrue(starting_position == 'Hallway_06')
        else:
            self.assertTrue(starting_position == 'Hallway_03')

    def test_that_valid_set_of_dealt_cards_in_this_players_subtable_in_pad(self):
        """
        Tests that the number of cards dealt are between 3 and y
        """
        # the number of cards will vary based on the number of players
        # 21 cards (3 hidden), 18 available. # of players 3 to 6
        # deal min 3, max 6 cards

        # check that this player's table has been marked properly
        # with the cards dealt
        tbl = self.player._pad.get_player_table(self.player.player_id)

        for card in self.dealt_cards:
            self.assertEqual(tbl['c1'][card], 1, '1 isn\'t in cell01 ({0})'.format(card))

        logging.debug('p04 table:\n%s', tbl['c1'])


    def test_should_throw_exception_for_invalid_number_of_cards_dealt(self):
        """
        Tests that an exception is thrown if the number of cards dealt are not between 3 and 6.
        """
        dealt_cards = ['Wrench', 'White', 'Study', 'Plum', 'Mustard', 'Knife', 'Scarlet']

        self.assertRaises(IndexError, self.player.receive_cards, dealt_cards)

    def test_should_state_invalid_number_of_cards_dealt(self):
        """
        Tests that if too many cards are dealt, the Player object returns a too many cards message.
        """
        # see https://docs.python.org/dev/library/unittest.html#unittest.TestCase.assertRaises
        # for another working sample, see
        # http://stackoverflow.com/questions/8215653/using-a-context-manager-with-python-assertraises
        dealt_cards = ['Wrench', 'White', 'Study', 'Plum', 'Mustard', 'Knife', 'Scarlet']

        with self.assertRaises(IndexError) as ie:
            self.player.receive_cards(dealt_cards)

        self.assertEqual(ie.exception.args, ('the number of cards dealt, must be between 3 and 6', ))

    def test_should_state_cards_are_invalid(self):
        """
        Tests that an error occurs if the cards received do not belong to the data structure of cards.
        """
        # will have enumerations of valid cards to work with
        # this will test that the cards dealt are in that enumeration
        dealt_cards = ['Wrench', 'White', 'Blue']

        self.assertRaises(ValueError, self.player.receive_cards, dealt_cards)

        with self.assertRaises(ValueError) as ve:
            self.player.receive_cards(dealt_cards)

        self.assertEqual(ve.exception.args, ('the card Blue is not valid', ))

    def test_where_player_is_on_board(self):

        """
        Test that the player's current _location is correctly returned.
        """
        location = self.player._get_location

        location_categories = [self.player._get_rooms, self._get_lobbies]
        all_locations = list(itertools.chain(*location_categories))

        self.assertIn(location, all_locations)

    # region: helper functions
    @property
    def _get_lobbies(self):

        """
        Get the lobbies that are valid for this game.

        :return: valid lobbies
        :rtype: list<str>
        """
        return {'Hallway_01', 'Hallway_02', 'Hallway_03', 'Hallway_04', 'Hallway_05', 'Hallway_06', 'Hallway_07',
                'Hallway_08', 'Hallway_09', 'Hallway_10', 'Hallway_11', 'Hallway_12'}
