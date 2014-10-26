import unittest
import itertools
from auto.automaton import Player


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
        self.player = Player(available_players, 4)

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

    # tests for building the player pad data structure
    def test_creating_pad_data_structure_for_four_players(self):

        """
        Tests that a player pad for four players was created.
        """
        expected_list_of_keys = ['p01', 'p02', 'p03', 'p04']
        self.assertEqual(sorted(self.player.pad.players_list), expected_list_of_keys)

    def test_x_tells_y_that_x_has_card_suggested_by_y_and_y_marks_cell01_to_track_the_card(self):
        # scenario: Player 2 asks player 1 if he/she/it has a card. Player 1 responds that he/she/it
        # has one of the cards suggested. As a result, player2 marks a card cell in column 1 ('c1')
        # with an x for player1. Player 2 is a Computer player, Player 1 could be a human or a computer player

        """
        Tests that the proper cell is marked on this players pad for p01
        """
        suggestion = {'suggested': ['Plum', 'Ballroom', 'Wrench'], 'player': 'p01', 'responded': 'Ballroom'}
        respond_card = suggestion['responded']

        self.player.mark_pad(suggestion)

        p01 = self.player.pad.get_player_table(suggestion['player'])

        self.assertEqual(p01['c1'][respond_card], 'x', 'the value in the cell isn\'t x')

    def test_x_in_cell01_should_clear_cell02_for_all_other_players(self):
        # scenario: following an answer to a suggestion, this player has confirmed that answering
        # player has one of the suggested cards. Therefore, this player must check cell02 of the corresponding card
        # for all other players and clear those cells

        # pre-conditions, cell01 for a card (card=White) has just been marked (for p01) on this player's pad
        suggestion = {'suggested': ['White', 'Billiard', 'Rope'], 'player': 'p01', 'responded': 'White'}
        self.player.mark_pad(suggestion)
        # pre-condition, some other players show cell02 for a card (card=White) with values
        suggestion = {'suggested': ['White', 'Kitchen', 'Revolver'], 'player': 'p02', 'responded': True}
        self.player.mark_pad(suggestion)
        suggestion = {'suggested': ['Green', 'Ballroom', 'Pipe'], 'player': 'p03', 'responded': True}
        self.player.mark_pad(suggestion)
        suggestion = {'suggested': ['White', 'Conservatory', 'Candlestick'], 'player': 'p02', 'responded': True}
        self.player.mark_pad(suggestion)

        self.player.pad.get_player_table('p02')
        self.player.pad.get_player_table('p03')




    def test_x_tells_y_that_x_has_a_suggested_card_other_computer_players_mark_their_pad(self):

        # scenario: When a suggestion is made, all other Computer players should mark their pads if
        # one player tells another player that he/she/it has a card. The other computer players won't
        # know which card, just that the response was positive. Therefore, columns 2 - 8 for each player
        # gets marked with a number for a particular card. Each column gets a unique number from 1 - 7

        """
        Tests that computer players not involved in a suggestion, mark their pads based on a positive response
        from the suggestion.
        """
        suggestion = {'suggested': ['Mustard', 'Kitchen', 'Revolver'], 'player': 'p01', 'responded': True}
        first_card = suggestion['suggested'][0].lower()
        second_card = suggestion['suggested'][1].lower()
        third_card = suggestion['suggested'][2].lower()

        self.player.mark_pad(suggestion)

        p01 = self.player.pad.get_player_table(suggestion['player'])

        self.assertTrue(1 in p01['c2'][first_card] and 1 in p01['c2'][second_card] and 1 in p01['c2'][third_card])

    def test_already_a_one_in_col2_for_one_of_the_card_suggested_so_two_in_next_col(self):
        # scenario: a suggestion was made between two other players (not this player). One of the suggested
        # cards has already been marked on this player's pad in column 2. Meaning that this player has heard
        # that the player answering has one of the cards being asked. Therefore, mark the next column over
        # for the answering player.

        """
        Tests that the column 2 (c3) gets a 2 for the cards suggested between two other players
        """
        # setup player's pad so that three card cells already have a 1 in c2.
        p03 = self.player.pad.get_player_table('p03')
        p03['c2']['scarlet'].add(1)
        p03['c2']['hall'].add(1)
        p03['c2']['rope'].add(1)

        # the suggestion to player 3 already contains rope so mark the next column over for player 3
        suggestion = {'suggested': ['Mustard', 'Kitchen', 'Rope'], 'player': 'p03', 'responded': True}
        first_card = suggestion['suggested'][0].lower()
        second_card = suggestion['suggested'][1].lower()
        third_card = suggestion['suggested'][2].lower()

        self.player.mark_pad(suggestion)

        self.assertTrue(2 in p03['c2'][first_card] and 2 in p03['c2'][second_card] and 2 in p03['c2'][third_card],
                        '2 in {0}:{1}, 2 in {2}:{3}, 2 in {4}:{5}'.format(first_card, 2 in p03['c2'][first_card],
                        second_card, 2 in p03['c2'][second_card], third_card, 2 in p03['c2'][third_card]))

        # end tests of the pad data structure
        # TODO: once the pad logic is solid, you can move on to the move and suggest and move and accuse tests

    def test_move_and_suggest(self):
        """
        Tests that the player can move into the room and make a suggestion.
        """
        # just contains the part of the game state that includes where players are currently located
        game_state = {'White': 'Hallway_02', 'Scarlet': 'Hallway_05', 'Green': 'Lounge'}

        move_response = self.player.take_turn(game_state)

        subset_test = {'suggest': ['Mustard', 'Lounge', 'Knife']}

        #TODO this test won't pass just yet. The take_turn function still needs to be able to make
        # suggestions and accusations. Once Pad is finished and functioning, then figure out how to
        # make a suggestion. Next, come back to this test to ensure that the suggestion is called
        # from self.player.take_turn so that the move_response contains a suggestion to test
        self.assertEqual(subset_test, self.__subdictionary_from_dictionary(subset_test, move_response))

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
        """
        return dict([(k, dictionary[k]) for k in subset_dictionary.keys() if k in dictionary.keys()])