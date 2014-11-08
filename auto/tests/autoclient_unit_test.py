import unittest
import itertools
import logging
import sys
import numpy as np

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
        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

        available_suspects = ['Peacock', 'Plum', 'Green', 'Mustard']

        # create a computer player and specify the total number of players in this game
        self.player = Player('p04', available_suspects, 4)

        # receive cards from dealer
        self.dealt_cards = ['Wrench', 'Green', 'Study']
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
        Test that the players current _location is correctly returned.
        """
        location = self.player._get_location

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
                                    self.player.player_id: 'Hallway_09', 'p05': 'Billiard'}}

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
        expected_response = {'move': {'player': 'p03', 'location': 'Conservatory'}}

        self.assertEquals(expected_response, self._subdictionary_from_dictionary(expected_response, move_response))

    # region tests for building and working with the player _pad data structure
    def test_creating_pad_data_structure_for_four_players(self):

        """
        Tests that a player _pad for four players was created.
        """
        expected_list_of_keys = ['p01', 'p02', 'p03', 'p04']
        self.assertEqual(sorted(self.player._pad.players_list), expected_list_of_keys)

    def test_p01_answers_p04_has_one_card_suggested(self):
        # scenario: p04 asks p01 if he/she/it has a card. p01 responds that he/she/it
        # has one of the cards suggested. As a result, p04 marks p01's sub-table c1 Plum
        # p04 is a Computer player, p01 could be a human or a computer player

        """
        Tests that the proper cell is marked on this players (p04's) _pad for the p01 sub-table
        """

        game_state = {'move_made': True, 'answer': {'from_player': 'p01', 'card': 'Plum'}}

        self.player.update(game_state)

        p01 = self.player._pad.get_player_table('p01')

        self.assertEqual(p01.c1.Plum, 1, 'the value in the cell isn\'t 1')

    def test_1_in_c1_for_card_should_clear_c2_for_card_in_all_other_player_sub_tables(self):
        # scenario: following an answer to a suggestion, this player has confirmed that answering
        # player has one of the suggested cards. Therefore, this player must clear all c2 values for the
        # corresponding card on all player sub-tables, including this player

        # player id from setup (self.player) is p04. Looking at this player's _pad

        # pre-condition, setup some other player sub-tables in p04's _pad to show c2 for card = White with values
        game_state = {'answer': {'has_card': True, 'from_player': 'p02'},
                      'cards': {'White', 'Kitchen', 'Revolver'}}
        self.player.update(game_state)

        suggestion = {'answer': {'has_card': True, 'from_player': 'p02'},
                      'cards': {'White', 'Ballroom', 'Pipe'}}
        self.player.update(game_state)

        suggestion = {'answer': {'has_card': True, 'from_Player': 'p02'},
                      'cards': {'White', 'Conservatory', 'Candlestick'}}
        self.player.update(game_state)

        players = ['p01', 'p02', 'p03', 'p04']

        for player in players:
            # verify that no player sub-tables show c1 White marked
            self.assertTrue(self.player._pad.get_player_table(player).c1.White, np.nan)
            if player == 'p02':
                p02_tbl = self.player._pad.get_player_table(player)
                # verify that the p02 player sub-table show c2 White with 1, 2 and 3 (3 suggestions)
                self.assertTrue(1 and 2 and 3 in p02_tbl.c2.White)

        # if you want to look at table contents:
        # logging.debug('p02 c2:\n%s', p02_tbl.c2.White)

        # action-condition, c1 for a card (card = White) has just been confirmed and marked (for p01)
        # on this player's _pad
        game_state = {'move_completed': True, 'answer': {'card': 'White', 'from_player': 'p01'}}
        self.player.update(game_state)

        # assert values after the action condition
        for player in players:
            if player == 'p01':
                # verify that the this player (p04) has marked c1 White with a 1
                self.assertEqual(self.player._pad.get_player_table(player).c1.White, 1)
            if player != 'p01':
                # verify that the other players do not have suspect White marked in the White cell
                self.assertFalse(self.player._pad.get_player_table(player).c1.White == 1)
            # verify that c2 is clear for all of the player sub-tables
            self.assertFalse(1 in self.player._pad.get_player_table(player).c2.White)

    def test_p01_tells_other_player_has_a_suggested_card_all_other_computer_players_mark_their_pads(self):

        # scenario: When a suggestion is made, all other Computer players should mark their pads if
        # one player tells another player that he/she/it has a card. The other computer players won't
        # know which card, just that the response was positive. Therefore, c2 for each player's _pad
        # gets appended with a number (increment) for a particular card.

        """
        Tests that computer players not involved in a suggestion, mark their pads based on a positive response
        from the suggestion.
        """
        game_state = {'answer': {'from_player': 'p01', 'has_card': True}, 'cards': {'Mustard', 'Kitchen', 'Revolver'}}

        cards = game_state['cards']

        self.player.update(game_state)

        p01 = self.player._pad.get_player_table(game_state['answer']['from_player'])

        for card in cards:
            self.assertTrue(1 in p01['c2'][card])

        # self.assertTrue(1 in p01['c2'][first_card] and 1 in p01['c2'][second_card] and 1 in p01['c2'][third_card])

    def test_already_a_one_in_c2_for_one_of_the_cards_suggested_so_append_two_to_all_three_answered_card_cells(self):
        # scenario: a suggestion was made between two other players (not this player p04). One of the suggested
        # cards has already been marked in c2 for a sub-table being tracked by p04. Meaning that p04 has heard
        # that the player answering has one of the cards being asked. Therefore, in p04's _pad, enter a 2 in the player
        # sub-table for teh player answering.

        """
        Tests that the column 2 (c3) gets a 2 for the cards suggested between two other players
        """
        # setup player's _pad so that three card cells already have a 1 in c2.
        p03 = self.player._pad.get_player_table('p03')
        p03['c2']['Scarlet'].add(1)
        p03['c2']['Hall'].add(1)
        p03['c2']['Rope'].add(1)

        # the suggestion to p03 already contains rope so next value increment is 2
        game_state = {'answer': {'from_player': 'p03', 'has_card': True}, 'cards': {'Mustard', 'Kitchen', 'Rope'}}
        answer = game_state['answer']
        cards = game_state['cards']

        self.player.update(game_state)

        for card in cards:
            self.assertTrue(2 in p03['c2'][card])

    def test_update_workflow_p01_makes_suggestion_p02_responds_with_only_possible_match(self):

        """
        Test everything that happens after a computer player is told to take a turn
        """

        # set the player to p02
        self.player.player_id = 'p02'

        # setup p02's _pad so that p02 has some cards marked
        p02 = self.player._pad.get_player_table('p02')
        p02['c1']['Mustard'] = 1
        p02['c2']['Scarlet'].add(1)
        p02['c2']['Lounge'].add(1)
        p02['c2']['Knife'].add(1)

        # setup p01 to take a turn
        self.player.player_id = 'p01'

        # server tells p01 to take a turn and passes position information to p01. This part
        # isn't tested here. p01 then puts together a move response to be sent to the server
        # via update

        # move response from p01 to server's request to take_turn.
        game_state = {'move': 'Lounge', 'suggestion': {'from_player': 'p01', 'cards': {'Mustard', 'Lounge', 'Rope'}}}
        response = self.player.update(game_state)

        # server will send all players (in order), p01's response. It's fine to send the update to all players
        # as long as the player who needs to answer is included in game_state
        # direct the message to p02 to simulate the server asking p02 for a response:
        self.player.player_id = 'p02'
        game_state = {'suggestion': {'to_player': 'p02', 'cards': {'Mustard', 'Lounge', 'Rope'}}}
        response = self.player.update(game_state)
        self.assertEqual(response, 'Mustard')

        # send the same game_state to another player and verify that they don't respond because they are not p02
        # and they don't have a card
        self.player.player_id = 'p03'
        self.assertIsNone(self.player.update(game_state))

        # server sends an update to 'p01' with acknowledgement of their move and the card revealed by the other player
        self.player.player_id = 'p01'
        game_state = {'move_made': True, 'answer': {'from_player': 'p02', 'card': response}}
        response = self.player.update(game_state)
        # verify that p01 marked their pad that p02 has Mustard and they returned 'turn_complete': True
        self.assertEqual(self.player._pad.get_player_table('p02')['c1'].Mustard, 1)
        self.assertTrue(response['turn_complete'])

        # server sends an update to all players telling them a card was revealed
        self.player.player_id = 'p03'
        game_state = {'answer': {'from_player': 'p02', 'has_card': True}, 'cards': {'Mustard', 'Lounge', 'Rope'}}
        cards = game_state['cards']
        self.player.update(game_state)

        for card in cards:
            self.assertTrue(2 in self.player._pad.get_player_table('p02')['c2'][card])

    def test_p01_makes_suggestion_to_p02_and_other_players_like_p03_do_not_respond(self):
        # set the player to p03
        self.player.player_id = 'p03'

        # setup p02's _pad so that p02 has some cards marked
        p02 = self.player._pad.get_player_table('p02')
        p02['c1']['Mustard'] = 1
        p02['c2']['Scarlet'] = 1
        p02['c2']['Lounge'] = 1
        p02['c2']['Knife'] = 1
        p02['c2']['Rope'] = 1

        game_state = {'move': {'_location': 'Kitchen', 'player': 'p01'},
                      'suggest': {'cards': ['Scarlet', 'Kitchen', 'Rope'], 'to_player': 'p02'}}

        self.assertIsNone(self.player.update(game_state))

    def test_update_provided_to_p01_following_matching_card_answer_given_by_p02(self):
        # set the player to p01
        self.player.player_id = 'p01'
        game_state = {'answer': 'Mustard', 'from_player': 'p02'}
        # mark column 2 for some other player to verify the column get cleared following
        # confirmation that p02 has the card
        self.player._pad.get_player_table('p03')['c2']['Mustard'].add(1)
        self.player._pad.get_player_table('p03')['c2']['Mustard'].add(2)

        self.player.update(game_state)

        # p01 marked it's _pad in the p02 column 1 Mustard cell with a 1
        self.assertEquals(self.player._pad.get_player_table('p02')['c1']['Mustard'], 1)
        # p01 cleared it's _pad in the other player's column 2
        self.assertFalse(self.player._pad.get_player_table('p03')['c2']['Mustard'])

    def test_update_to_all_players_about_answer_to_suggestion(self):
        """
            All players other than the player making a suggestion and the player answering should mark
            their c2 card columns for the suggested cards
            """

        # set the player to p04. A player who should get an undirected response
        self.player.player_id = 'p04'
        game_state = {'answer': True, 'from_player': 'p02', 'suggested': ['Plum', 'Hall', 'Candlestick']}

        self.player.update(game_state)

        # verify that p04 has marked the p02 sub-table with the fact that one of these three cards are held by p02
        for card in game_state['suggested']:
            self.assertTrue(1 in self.player._pad.get_player_table('p02')['c2'][card])


    def test_p01_makes_suggestion_to_p04_p04_responds_with_no_card_match(self):
        """
            All players should not mark anything if p04 doesn't have any cards asked

            """
        # will begin by checking that p01 (the asking player) doesn't mark anything
        self.player.player_id = 'p01'
        game_state = {'answer': False, 'from_player': 'p04', 'suggested': ['Plum', 'Hall', 'Candlestick']}
        self.player.update(game_state)

        # get the p04 sub-table in p01's _pad
        p04_tbl = self.player._pad.get_player_table('p04')

        # get some other player sub-table in p01's _pad (to verify the card doesn't get marked)
        p02_tbl = self.player._pad.get_player_table('p02')

        # check p01's _pad
        for card in game_state['suggested']:
            # c1 for all cards is not marked with a 1 since p01 responded with no match
            self.assertFalse(p04_tbl.c1[card] == 1)
            # c2 for all cards is empty since p01 responded with no match
            self.assertFalse(1 in p04_tbl.c2[card])

            # some other sub-table in p01's _pad is also empty after this update.
            self.assertFalse(p02_tbl.c1[card] == 1)
            self.assertFalse(1 in p02_tbl.c2[card])

        # end region tests for building and working with the player _pad data structure

        # region this player taking turns

    def test_move_to_only_available_new_move(self):
        """
            Tests that the player can move into the room and make a suggestion.
            """
        # part of the game_state sent by server showing where players are currently positioned.
        # this show this player, p04 in the Kitchen. Therefore, valid next moves for p04 are
        # Hallway_08, Hallway_10 or Study
        game_state = {'positions': {'p01': 'Hallway_02', 'p02': 'Hallway_05', 'p03': 'Lounge', 'p04': 'Kitchen'}}

        # because no player blocking these places, this player (p04) can move to
        # Hallway_12, Hallway_10 or Study

        # add prior moves taken by this player
        self.player._prior_moves.add('Hallway_12')
        self.player._prior_moves.add('Study')

        move_response = self.player.take_turn(game_state)

        subset_test = {'move': {'_location': 'Hallway_10', 'player': self.player.player_id}}

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

        self.assertIn(move_response['move']['_location'], expected_response)

    def test_suggest(self):
        # scenario: p04 moves to Hall and suggests Hall, Mustard, Candlestick because:
        # - it's a valid next move (currently in Hallway_01, 02 or 04)
        # - c1 is not marked for Hall, Mustard or Candlestick in any player sub-table

        # put player in Hallway_01
        self.player._location = 'Hallway_01'
        # mark that the player has already been in the study
        self.player._prior_moves.add('Study')
        # player4 was dealt Wrench, Green, Study

        # think about how you decide what to suggest. Pretty much if c1 is empty, the card is available to guess
        # might have to mark 1 for everything except these three cells in c1 across all sub-tables

    def test_accuse(self):
        """
            Tests that the player can move into a room and make an accusation.
        """
        pass

    # end region this player taking turns

    # region helper classes
    def _subdictionary_from_dictionary(self, subset_dictionary, dictionary):
        """
            Helper to replace deprecated assertDictContainsSubset

            :param subset_dictionary: the dictionary subset in which to test
            :param dictionary: the full dictionary that should contain the subset
            """
        return dict(
            [(k, dictionary[k]) for k in subset_dictionary.keys() if k in dictionary.keys()])  # end region helper classes
