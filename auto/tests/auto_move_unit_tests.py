import unittest
import logging
import sys

from auto.automaton import Player


class AutoMoveUnitTests(unittest.TestCase):
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

        available_suspects = ['Peacock', 'Plum', 'Green', 'Mustard']

        # create a computer player and specify the total number of players in this game
        self.player = Player('p04', available_suspects, 4)
        # with four players, 2 players will get 4 cards and 2 players will get 5 cards

        # receive cards from dealer
        self.dealt_cards = ['Wrench', 'Green', 'Study', 'Hall']
        self.player.receive_cards(self.dealt_cards)

    def test_player_moves_to_an_allowed_spot(self):

        """
        Tests validity of next moves - adjacent locations and a room via a secret passageway for some rooms.
        """
        self.assertSetEqual(self.player._next_moves('Hallway_01'), {'Study', 'Hall'})
        self.assertSetEqual(self.player._next_moves('Billiard'),
                            {'Hallway_04', 'Hallway_06', 'Hallway_07', 'Hallway_09'})
        self.assertSetEqual(self.player._next_moves('Kitchen'), {'Hallway_10', 'Hallway_12', 'Study'})

    def test_should_not_include_library_as_valid_move_because_p01_there_so_should_move_p04_to_billiard(self):

        """
        Tests that this player (p04) will move to the Billiard Room because the p01 is blocking entry to the Library
        """

        self.player._location = 'Hallway_06'
        game_state = {'positions': {'p01': 'Library', 'p02': 'Hallway_01', 'p03': 'Study', 'p04': 'Hallway_06'}}
        move_response = self.player.take_turn(game_state)

        self.assertDictEqual(move_response, {'move': 'Billiard'})

    def test_cannot_move_out_from_current_position_all_moves_are_blocked(self):
        """
        Tests that the player (p04) can't move anywhere because all positions are blocked
        """

        self.player._location = 'Billiard'
        game_state = {'positions': {'p01': 'Hallway_06', 'p02': 'Hallway_04', 'p03': 'Hallway_07',
                                    self.player.player_id: 'Billiard', 'p05': 'Hallway_09'}}

        move_response = self.player.take_turn(game_state)

        self.assertDictEqual(move_response, {'move': ''})

    def test_can_move_to_diagonal_room(self):

        """
        Tests that the player will move to a diagonal room when all other paths are blocked
        """
        self.player.player_id = 'p03'
        self.player._location = 'Lounge'
        game_state = {'positions': {'p01': 'Hallway_02', 'p02': 'Hallway_05', 'p03': 'Lounge'}}

        move_response = self.player.take_turn(game_state)
        expected_response = {'move': 'Conservatory'}

        self.assertEquals(expected_response, self._subdictionary_from_dictionary(expected_response, move_response))

    def test_move_to_only_available_new_move(self):
        """
        Tests that the player can move into the room and make a suggestion.
        """

        # game_state sent by server showing where players are currently positioned.
        # this shows this player, p04, in the Kitchen. Therefore, valid next moves for p04 are
        # Hallway_12, Hallway_10 or Study
        game_state = {'positions': {'p01': 'Hallway_02', 'p02': 'Hallway_05', 'p03': 'Lounge', 'p04': 'Kitchen'}}

        # because no player is blocking these places, this player (p04) can move to Hallway_12, Hallway_10 or Study

        # add prior moves taken by this player
        self.player._prior_moves.add('Hallway_12')
        self.player._prior_moves.add('Study')

        move_response = self.player.take_turn(game_state)

        subset_test = {'move': 'Hallway_10'}

        self.assertEqual(subset_test, self._subdictionary_from_dictionary(subset_test, move_response))

    def test_move_to_prior_location_no_new_move_available(self):
        """
            Tests that the player will randomly move to a prior _location when there is no where else to move
            :return:
            """

        # player current positions
        game_state = {'positions': {'p01': 'Lounge', 'p02': 'Billiard', 'p03': 'Hallway_01', 'p04': 'Library'}}

        # add prior moves (all allowed moves from current position
        self.player._prior_moves.add('Hallway_03')
        self.player._prior_moves.add('Hallway_06')
        self.player._prior_moves.add('Hallway_08')

        move_response = self.player.take_turn(game_state)

        expected_response = {'Hallway_03', 'Hallway_06', 'Hallway_08'}

        self.assertIn(move_response['move'], expected_response)

    # region helper classes
    def _subdictionary_from_dictionary(self, subset_dictionary, dictionary):
        """
            Helper to replace deprecated assertDictContainsSubset

            :param subset_dictionary: the dictionary subset in which to test
            :param dictionary: the full dictionary that should contain the subset
            """
        return dict(
            [(k, dictionary[k]) for k in subset_dictionary.keys() if k in dictionary.keys()])