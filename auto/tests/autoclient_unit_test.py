import unittest
import itertools
from auto.automaton import Player

class AutoClientUnitTest(unittest.TestCase):
    def setUp(self):
        available_players = ['Peacock', 'Plum', 'Green', 'Mustard']
        self.player = Player(available_players)

    def tearDown(self):
        pass

    def test_player_instantiated(self):
        # test that a player object was returned
        self.assertTrue(self.player)
        self.assertTrue(self.player.selected_player == 'Peacock' or 'Plum' or 'Green', 'Mustard')

    def test_selected_player_in_correct_starting_position(self):
        # no moves have been made so the instantiated player should be in the correct starting position
        starting_position = self.player.get_starting_location(self.player.selected_player)

        if self.player == 'Peacock':
            self.assertTrue(starting_position == 'Hallway_07')
        elif self.player == 'Plum':
            self.assertTrue(starting_position == 'Hallway_08')
        elif self.player == 'Green':
            self.assertTrue(starting_position == 'Hallway_06')
        else:
            self.assertTrue(starting_position == 'Hallway_03')

    def test_should_store_a_valid_set_of_cards(self):
        # the number of cards will vary based on the number of players
        # 21 cards (3 hidden), 18 available. # of players 3 to 6
        # deal min 3, max 6 cards

        dealt_cards = ['Wrench', 'White', 'Study']
        self.cards = self.player.receive_cards(dealt_cards)

        self.assertTrue(3 <= len(self.cards) <= 6)

    def test_should_throw_exception_for_invalid_number_of_cards_dealt(self):
        dealt_cards = ['Wrench', 'White', 'Study', 'Plum', 'Mustard', 'Knife', 'Scarlet']

        self.assertRaises(IndexError, self.player.receive_cards, dealt_cards)

    def test_should_state_invalid_number_of_cards_dealt(self):
        # see https://docs.python.org/dev/library/unittest.html#unittest.TestCase.assertRaises
        # for another working sample, see
        # http://stackoverflow.com/questions/8215653/using-a-context-manager-with-python-assertraises
        dealt_cards = ['Wrench', 'White', 'Study', 'Plum', 'Mustard', 'Knife', 'Scarlet']

        with self.assertRaises(IndexError) as ie:
            self.player.receive_cards(dealt_cards)

        self.assertEqual(ie.exception.args, ('the number of cards dealt, must be between 3 and 6', ))

    def test_should_state_cards_are_invalid(self):
        # will have enumerations of valid cards to work with
        # this will test that the cards dealt are in that enumeration
        dealt_cards = ['Wrench', 'White', 'Blue']

        self.assertRaises(ValueError, self.player.receive_cards, dealt_cards)

        with self.assertRaises(ValueError) as ve:
            self.player.receive_cards(dealt_cards)

        self.assertEqual(ve.exception.args, ('the card Blue is not valid', ))

    def test_where_is_player_on_board(self):
        # this is a test to drive the creation of the get_location function
        # changes this so location isn't passed in. Game state (all player positions
        # will be sent at the start of each turn. So get_location might simply use
        # game state to determine current location and allowed moves
        location = self.player.get_location()

        location_categories = [self.player.get_rooms, self.player.get_lobbies]
        all_locations = list(itertools.chain(*location_categories ))

        self.assertIn(location, all_locations)

    def test_player_moves_to_an_allowed_spot(self):
        # when asked to move, move to an allowed location
        location = self.player.get_location()

    def test_should_move_from_hallway_01_to_study_and_store_visit(self):
        # this will call the move command, which can kick-off a number of possible
        # actions - move into a room, move out of a room, move between rooms. Suggest/accuse, etc...

        current_location = self.player.get_location('Hallway_01')
        move_success = self.move(current_location)
        self.assertEqual(self.player.get_location(), 'Study')


        # given my location
        # move into a room, out of a room to an adjacent lobby or between rooms on the diagonal
        # optionally make a suggestion or accusation

    def test_can_move_out_of_room(self):
        pass

    def test_cannot_move_out_of_room(self):
        pass

    def test_can_move_to_diagonal_room(self):
        pass

    def test_move_to_specific_room(self):
        pass

    def test_whether_player_makes_a_valid_move(self):
        pass

    def test_move_and_suggest(self):
        pass

    def test_move_and_accuse(self):
        pass