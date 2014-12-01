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
        # from the caller (server)

        # receive cards from dealer/caller
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

        game_state = {'positions': {'p01': 'Library', 'p02': 'Hallway_01', 'p03': 'Study', 'p04': 'Hallway_06'}}
        move_response = self.player.take_turn(game_state)

        self.assertEqual(move_response['move'], 'Billiard')

    def test_cannot_move_out_from_current_position_all_moves_are_blocked(self):
        """
        Tests that the player (p04) can't move anywhere because all positions are blocked
        """

        self.player._location = 'Billiard'
        game_state = {'positions': {'p01': 'Hallway_06', 'p02': 'Hallway_04', 'p03': 'Hallway_07',
                                    self.player.player_id: 'Billiard', 'p05': 'Hallway_09'}}

        move_response = self.player.take_turn(game_state)

        self.assertEqual(move_response['move'], '')

    def test_can_move_to_diagonal_room(self):

        """
        Tests that the player will move to a diagonal room when all other paths are blocked
        """
        self.player.player_id = 'p03'
        self.player._location = 'Lounge'
        game_state = {'positions': {'p01': 'Hallway_02', 'p02': 'Hallway_05', 'p03': 'Lounge'}}

        move_response = self.player.take_turn(game_state)

        self.assertEquals(move_response['move'], 'Conservatory')

    def test_move_to_only_available_new_move(self):
        """
        Tests that the player will move to a room that player hasn't occupied yet.
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

        self.assertEqual(move_response['move'], 'Hallway_10')

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

    def test_move_attempt_failed_reported_by_caller_move_removed_from_prior_moves(self):

        # player current positions
        game_state = {'positions': {'p01': 'Lounge', 'p02': 'Billiard', 'p03': 'Hallway_01', 'p04': 'Library'}}

        move_response = self.player.take_turn(game_state)

        move_taken = move_response['move']

        # check that prior to an update from the caller, the move just taken is in the list of prior moves
        self.assertIn(move_taken, self.player._prior_moves)

        # caller states that the move couldn't be made. This is a rare and possibly impossible edge case
        # because the autonomous player will not attempt to move to a blocked location. However, in the
        # event that something in the caller caused the move to fail, the autonomous player needs to
        # react to the failure
        game_state = {'move_made': False}

        # tell this player the move wasn't successful
        ack = self.player.update(game_state)

        # verify acknowledgement that this player is done with the turn
        self.assertEqual(ack, {'turn_complete': True})

        # verify that the move was removed from prior moves. Again, while this is an unlikely situation,
        # if the caller does return False for move_made, then removing the move taken from prior moves
        # is important. The possible side-effect is that this player might have taken this move more than
        # once. If so, it will appear to this player that the move was never taken. This is not a
        # big issue, but worth noting this edge case.
        self.assertNotIn(move_taken, self.player._prior_moves)
