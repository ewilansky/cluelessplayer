import unittest
import logging
import sys

import auto.playermatrix as pm
from auto.automaton import Player


class AutoSuggestAccuseUnitTests(unittest.TestCase):
    """
    Testing the automaton player's suggest and accuse logic
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

    def test_update_workflow_p01_makes_suggestion_p02_responds_with_only_possible_match(self):

        """
        Test everything that happens AFTER a computer player takes a turn
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

        game_state = {'move_made': True, 'answer': {'from_player': 'p02', 'card': 'Mustard'}}
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

        # current player from test setup is p04. A player who should get an undirected response
        game_state = {'answer': {'from_player': 'p02', 'has_card': True}, 'cards': {'Plum', 'Hall', 'Candlestick'}}

        self.player.update(game_state)

        # verify that p04 has marked the p02 sub-table with the fact that one of these three cards are held by p02
        for card in game_state['cards']:
            self.assertTrue(1 in self.player._pad.get_player_table('p02')['c2'][card])

    def test_p01_makes_suggestion_to_p04_p04_responds_with_no_card_match(self):
        """
        All players should not mark anything if p04 doesn't have any cards asked
        """

        # will begin by checking that p01 (the asking player) doesn't mark anything
        self.player.player_id = 'p01'
        game_state = {'answer': {'from_player': 'p04', 'has_card': False}, 'cards': {'Plum', 'Kitchen', 'Candlestick'}}
        self.player.update(game_state)

        # get the p04 sub-table in p01's _pad
        p04_tbl = self.player._pad.get_player_table('p04')

        # get some other player sub-table in p01's _pad (to verify the card doesn't get marked)
        p02_tbl = self.player._pad.get_player_table('p02')

        # check p01's _pad
        for card in game_state['cards']:
            # c1 for all cards is not marked with a 1 since p01 responded with no match
            self.assertFalse(p04_tbl.c1[card] == 1)
            # c2 for all cards is empty since p01 responded with no match
            self.assertFalse(1 in p04_tbl.c2[card])

            # some other sub-table in p01's _pad is also empty after this update.
            self.assertFalse(p02_tbl.c1[card] == 1)
            self.assertFalse(1 in p02_tbl.c2[card])

        # end region tests for building and working with the player _pad data structure

        # region this player taking turns

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
            Tests that the player can make an accusation.
        """
        # mark all cells in c1 sub-tables except for three total. Three remaining open cells means that it's time
        # to make an accusation. p04 is current player from test setup

        # using private methods for directly marking pad (this is just for setting-up the pre-condition)
        player_matrix = pm.PlayerMatrix()
        cards = player_matrix.table.axes[0].tolist()
        # remove three cards to simulate the hidden cards
        cards.remove('Plum')
        cards.remove('Rope')
        cards.remove('Dining')

        # p03 is going to tell p04 this card so remove it from cards to be marked as a pre-condition
        cards.remove('Kitchen')

        # p04 was dealt cards that were marked when p04 was instantiated. So remove these cards too
        cards.remove('Study')
        cards.remove('Green')
        cards.remove('Wrench')
        cards.remove('Hall')

        # cards to be marked
        # p01 has 5 cards
        for card in cards[0:5]:
            self.player._pad.get_player_table('p01')['c1'][card] = 1
        # p02 has 5 cards, we know 4 of them
        for card in cards[5:10]:
            self.player._pad.get_player_table('p02')['c1'][card] = 1
        # p03 has 4 cards
        for card in cards[10:14]:
            self.player._pad.get_player_table('p03')['c1'][card] = 1
        # p04 has 4 cards, which were dealt and marked on the pad for this player

        # part way through a turn. So far, p04 has moved and made a suggestion. As a result,
        # p03 responds with a match of Kitchen. This is the final condition needed for p04
        # to make an accusation. Server responds with the following:
        game_state = {'move_made': True, 'answer': {'from_player': 'p03', 'card': 'Kitchen'}}

        actual_response = self.player.update(game_state)

        # for table debugging. Not necessary for the test.
        # pd = self.player._pad
        # tp01 = pd.get_player_table('p01').c1
        # tp02 = pd.get_player_table('p02').c1
        # tp03 = pd.get_player_table('p03').c1
        # tp04 = pd.get_player_table('p04').c1
        #
        # logging.debug('p01:\n%s p02:\n%s, p03:\n%s, p04:\n%s', tp01, tp02, tp03, tp04)

        # since a move was already made, all that will be done is to make an accusation
        # and state that the player is finished taking a turn
        expected_response = {'accusation': {'from_player': 'p04', 'cards': {'Plum', 'Rope', 'Dining'}},
                             'turn_complete': True}

        self.assertEqual(expected_response, actual_response)