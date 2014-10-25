import unittest
import itertools
from auto.automaton import Player, Pad


class AutoClientUnitTest(unittest.TestCase):
    """
    The automaton Player unit test class
    """

    def setUp(self):
        """
        unittest class setup

        :var available players list for most tests in this class
        :var an instantiated player object
        """

        available_players = ['Peacock', 'Plum', 'Green', 'Mustard']
        self.player = Player(available_players)
        # create a pad for 4 players
        self.pad = Pad(4)

    def test_player_instantiated(self):
        """
        Test that a player object was returned.

        """
        self.assertTrue(self.player)
        self.assertTrue(self.player.selected_player == 'Peacock' or 'Plum' or 'Green', 'Mustard')

    def test_selected_player_in_correct_starting_position(self):
        """
        Since no moves have been made, test that the instantiated player should be in the correct starting position.

        """

        starting_position = self.player.get_starting_location(self.player.selected_player)

        if self.player.selected_player == 'Peacock':
            self.assertTrue(starting_position == 'Hallway_07')
        elif self.player.selected_player == 'Plum':
            self.assertTrue(starting_position == 'Hallway_08')
        elif self.player.selected_player == 'Green':
            self.assertTrue(starting_position == 'Hallway_06')
        else:
            self.assertTrue(starting_position == 'Hallway_03')

    def test_should_store_a_valid_set_of_cards(self):
        """
        Tests that the number of cards dealt are between 3 and y

        """

        # the number of cards will vary based on the number of players
        # 21 cards (3 hidden), 18 available. # of players 3 to 6
        # deal min 3, max 6 cards

        dealt_cards = ['Wrench', 'White', 'Study']
        self.cards = self.player.receive_cards(dealt_cards)

        self.assertTrue(3 <= len(self.cards) <= 6)

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
        Test that the players current location is correctly returned.

        """
        location = self.player.get_location

        location_categories = [self.player._get_rooms, self.player._get_lobbies]
        all_locations = list(itertools.chain(*location_categories))

        self.assertIn(location, all_locations)

    def test_player_moves_to_an_allowed_spot(self):

        """
        Tests validity of next moves - adjacent locations and a room via a secret passageway for some rooms.

        """
        self.assertSetEqual(self.player._next_moves('Hallway_01'), {'Study', 'Hall'})
        self.assertSetEqual(self.player._next_moves('Billiard'),
                            {'Hallway_04', 'Hallway_06', 'Hallway_07', 'Hallway_09'})
        self.assertSetEqual(self.player._next_moves('Kitchen'), {'Hallway_10', 'Hallway_12', 'Study'})

    def test_should_not_include_library_as_valid_move_because_mustard_there_so_should_move_white_to_billiard(self):

        """
        Tests that the player will move to the Billiard Room because the Mustard is blocking entry to the Library

        """
        self.player.selected_player = 'White'
        self.player.location = 'Hallway_06'
        game_state = {'Mustard': 'Library', 'Scarlet': 'Hallway_01', 'Green': 'Study', 'White': 'Hallway_06'}
        move_response = self.player.take_turn(game_state)

        self.assertDictEqual(move_response, {'move': 'Billiard'})

    def test_cannot_move_out_from_current_position_all_moves_are_blocked(self):
        """
        Tests that the player can't move anywhere because all positions are blocked

        """
        self.player.selected_player = 'Plum'
        self.player.location = 'Billiard'
        game_state = {'Mustard': 'Hallway_06', 'White': 'Hallway_04', 'Scarlet': 'Hallway_07',
                      'Peacock': 'Hallway_09', 'Plum': 'Billiard'}

        move_response = self.player.take_turn(game_state)

        self.assertDictEqual(move_response, {'move': ''})

    def test_can_move_to_diagonal_room(self):
        """
        Tests that the player will move to a diagonal room when all other paths are blocked

        """
        self.player.selected_player = 'Green'
        self.player.location = 'Lounge'
        game_state = {'White': 'Hallway_02', 'Scarlet': 'Hallway_05', 'Green': 'Lounge'}

        move_response = self.player.take_turn(game_state)
        subset_test = {'move': 'Conservatory'}

        self.assertEquals(subset_test, self.__subdictionary_from_dictionary(subset_test, move_response))

    def test_move_and_suggest(self):
        """
        Tests that the player can move into the room and make a suggestion.

        """

        game_state = {'White': 'Hallway_02', 'Scarlet': 'Hallway_05', 'Green': 'Lounge'}

        move_response = self.player.take_turn(game_state)

        subset_test = {'suggest': ['Mustard', 'Lounge', 'Knife']}
        self.assertEqual(subset_test, self.__subdictionary_from_dictionary(subset_test, move_response))


    # tests for building the player pad data structure
    def test_creating_pad_data_structure_for_three_players(self):

        pad = Pad(3)

        expected_list_of_keys = ['p01', 'p02', 'p03']
        self.assertEqual(sorted(pad.players_list), expected_list_of_keys)

    def test_one_player1_tells_player2_has_card_player2_marks_pad_column1(self):

        suggested_cards = {'suggest': ['Plum', 'Ballroom', 'Wrench']}
        respond_card = 'Ballroom'

        p01 = self.pad.get_player_table('p01')

        # locate player 1's column 1 for the specified card and put an x in it
        p01['c1'][respond_card] = 'x'

        self.assertEqual(p01['c1'][respond_card], 'x', 'the value in the cell isn\'t x')


    # end tests of the pad data structure

    # TODO
    def test_move_and_accuse(self):
        """
        Tests that the player can move into a room and make an accusation.

        """

        pass


    # helper classes
    def __subdictionary_from_dictionary(self, subset_dictionary, dictionary):
        """
        Helper to replace deprecated assertDictContainsSubset

        :param subset_dictionary: the dictionary subset in which to test
        :param dictionary: the full dictionary that should contain the subset
        :return: subset
        :rtype: dict<str, str>
        """
        return dict([(k, dictionary[k]) for k in subset_dictionary.keys() if k in dictionary.keys()])