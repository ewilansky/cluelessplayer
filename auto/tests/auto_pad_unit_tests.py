import unittest
import logging
import sys

import numpy as np

from auto.automaton import Player


class AutoPadUnitTests(unittest.TestCase):
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
        # with four players, 2 players will get 4 cards and 2 players will get 5 cards

        # receive cards from dealer
        self.dealt_cards = ['Wrench', 'Green', 'Study', 'Hall']
        self.player.receive_cards(self.dealt_cards)

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