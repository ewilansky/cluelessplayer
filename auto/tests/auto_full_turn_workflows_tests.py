import unittest
import logging
import sys
import random

from auto.automaton import Player


class AutoFullTurnWorkflowsUnitTests(unittest.TestCase):
    """
    Testing the automaton player's taken turn move actions
    """

    def setUp(self):
        """
        unittest class setup

        """
        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)


    def test_setup_five_computer_players(self):
        """
        Tests that all players are initialized properly and are all in their correct starting position.

        """
        available_suspects = ['Mustard', 'Peacock', 'Plum', 'Green', 'Scarlet', 'White']

        # setup 5 computer players.
        # note player id's start at 1 (e.g., p01). The assumption here is that the one
        # human player is p01. Thus 2 - 7 contains 5 computer players (p02 - p06)
        for x in range(2, 7):
            self.player = Player('p0' + str(x), available_suspects, 6)

            # verify the all players have pads with 6 total players (1 human and 5 computer players)
            self.assertEqual(len(self.player._pad.players_list), 6)

            # verify that all suspects are in their proper starting position
            starting_positions = ['Hallway_02', 'Hallway_03', 'Hallway_05', 'Hallway_08', 'Hallway_11', 'Hallway_12']
            # ensure sorted order
            starting_positions.sort()
            suspects_in_starting_order = ['0-Scarlet', '1-Plum', '2-Mustard', '3-Peacock', '4-Green', '5-White']
            # ensure sorted order
            suspects_in_starting_order.sort()

            # verify that each player is in the proper position
            for ordered_suspect in suspects_in_starting_order:
                suspect_order = int(str.split(ordered_suspect, '-')[0])
                suspect_name = str.split(ordered_suspect, '-')[1]

                if self.player._selected_suspect == suspect_name:
                    self.assertEqual(self.player._location, starting_positions[suspect_order])

            suspect_allocated = self.player._selected_suspect
            available_suspects.remove(suspect_allocated)
            # end verify suspect in correct starting position

    def test_move_suggest(self):
        # create player with 5 other players (full player board) and deal cards
        players = self._setup_computer_players(5, 6)
        places_on_board = ['Billiard', 'Kitchen', 'Hallway_06', 'Hallway_10', 'Lounge']
        cards = []
        for player in players:

            column = player._pad.get_player_table(player.player_id)['c1']

            i = 0
            for cell in column:
                if cell == 1:
                    cards.append(column.index[i])
                i += 1

            # demonstrates that the cards have been dealt and marked on all computer player pads
            print(cards)
            self.assertEqual(len(cards), 3)

            cards.clear()

            # move players to some places on the board
            player._location = places_on_board.pop()

        # fill a player's pad with cards that have been learned
            # p02 is in the billiard (verify this)
            # fill p02's pad so that the only unknown is the Study (no one is blocking a move to that room)
            # fill all of p02's previous room positions so that p02 prefers the study
            # let p02 take turns to see if the player ends-up in the study to make a suggestion


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

    # helper methods
    def _setup_computer_players(self, num_to_create, total_players):
        players = []
        available_suspects = ['Mustard', 'Peacock', 'Plum', 'Green', 'Scarlet', 'White']

        # create a list of dealt hands to distribute to each of the players
        # this includes any human player because dealing the right number of cards
        # (a caller/server responsibility) must include human players.
        list_of_dealt_hands = self._deal_cards(total_players)

        # adding one here is necessary since python upper range enum doesn't
        # include the last value in the range
        for x in range(1, num_to_create + 1):
            # total players is a combination of human and computer players.
            self.player = Player('p0' + str(x), available_suspects, total_players)

            available_suspects.remove(self.player._selected_suspect)

            # deal this player cards
            self.player.receive_cards(list_of_dealt_hands[x])

            # the additional hands of cards will be for the human players. Assigning these cards is out of
            # the control of the computer player and is not part of testing. Just needed to consider
            # human players when determining how many cards to deal to the computer players. Assumption is
            # that there is at least  human player for test setup purposes.
            players.append(self.player)

        return players

    def _deal_cards(self, num_total_players):

        hands = []
        card_list = []

        # create an empty hand list for each player (human & computer)
        for hand in range(1, num_total_players + 1):
            hands.append([])

        # get the cards
        cards = self._get_cards()

        # need a list for shuffle
        for card in cards:
            card_list.append(card)

        # remove three cards to hide (one of each type)
        card_list.remove('Mustard')
        card_list.remove('Knife')
        card_list.remove('Kitchen')

        # shuffle the remaining 18 cards
        random.shuffle(card_list)

        # given the number of players, deal cards. Deal cards to human players too. This is simply
        # simulating what a caller is going to need to do for all players, human and computer
        # c = 18
        # while c > 0:
        while card_list:
            for x in range(0, num_total_players):
                # get a card from the deck
                card = card_list.pop()
                # assign it to a player's hand
                hands[x].append(card)

        return hands

    @staticmethod
    def _get_cards():
        _suspects = {
            'Scarlet', 'Plum', 'Mustard', 'Green', 'White', 'Peacock'
        }

        _rooms = {
            'Study', 'Hall', 'Lounge', 'Library', 'Billiard', 'Dining', 'Conservatory', 'Ballroom', 'Kitchen'
        }

        _weapons = {
            'Knife', 'Wrench', 'Revolver', 'Pipe', 'Rope', 'Candlestick'
        }

        #TODO remove if this comment isn't removed
        _hallways = {
            'Hallway_01', 'Hallway_02', 'Hallway_03', 'Hallway_04', 'Hallway_05', 'Hallway_06', 'Hallway_07',
            'Hallway_08', 'Hallway_09', 'Hallway_10', 'Hallway_11', 'Hallway_12'
        }

        return _suspects.union(_rooms.union(_weapons))
