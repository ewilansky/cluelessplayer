import unittest
import logging
import sys
import random
import textwrap
from enum import Enum

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

    def test_game_workflow(self):
        # create player with 6 players (full player board) and deal cards
        players = self._setup_players(6)
        places_on_board = ['Billiard', 'Kitchen', 'Hallway_06', 'Hallway_10', 'Lounge', 'Conservatory']
        game_state = {'positions': {}}

        print('dealt cards and suspects selected/assigned:')
        for player in players:
            cards = self.get_marked_cards(player)
            self.assertEqual(len(cards), 3)
            print('{0} dealt: {1} and selected suspect: {2}'.
                  format(player.player_id, str(cards), player._selected_suspect))
            cards.clear()

            # move players to some places on the board
            player._location = places_on_board.pop()
            # build-up game_state for later testing
            game_state['positions'][player.player_id] = player._location

        # get player06 for further testing
        p02 = players[1]
        marked_cards = set()

        # fill this player's pad with cards that have been learned. Mark everything except for one card, which will
        # be a card that the players hold. Three cards won't be marked since they weren't dealt and they must be
        # the hidden cards. Then, test that the computer player makes a suggestion to uncover
        # who has the remaining card. The room to move to will either be the remaining card or the computer player
        # will move to a known room and make a suggestion to find identify an unknown card.
        for player in players:

            # sub-table for the player whose cards should be marked on p02's playing pad
            player_sub_table = p02._pad.get_player_table(player.player_id)

            # mark each dealt card (except for the last card (card #18) for other computer players on p02's pad
            for card in self.get_marked_cards(player):
                if len(marked_cards) < 17:
                    player_sub_table['c1'][card] = 1
                    # add cards to the marked cards set
                    marked_cards.add(card)

        # region: identify a set of four unknown cards (3 in the middle) and one held by another player)
        all_cards = self._get_cards()
        # the difference will contain the cards in middle with an additional card held by a player
        # The additional card not marked in p02's pad is assumed to be held by another player
        unknown_cards = all_cards.difference(marked_cards)
        # endregion

        # logging.debug('p02 knows of:\n%s', marked_cards)
        print("\np02 knows of {0} cards:".format(len(marked_cards)))
        print(textwrap.fill(str(marked_cards)))

        # assert that p02 is in the lounge
        self.assertEqual(p02._location, game_state['positions'][p02.player_id])

        # display current positions from game state
        self._display_player_position_game_state(game_state)

        # p02 will now be told to take turns. If the logic is right and given the current game state,
        # the player should first move to a hallway since currently p02 is in the lounge.
        turn_msg = p02.take_turn(game_state)
        self.assertIn(turn_msg['move'], ['Hallway_02', 'Hallway_05'])
        print('\np02 requests to move to {0}'.format(turn_msg['move']))

        # the turn_msg is received by the caller and the caller returns an acknowledgement that the move was successful
        # the caller sends that success to the player making the move, like so:
        player_msg = p02.update({'move_made': True})

        # the player tells the caller that the turn is complete
        self.assertEqual(player_msg, {'turn_complete': True})

        # the caller (server) will then call update for all players. The game_state will now look like this:
        game_state = self.get_game_state(players)
        self._display_player_position_game_state(game_state)

        # let's have p02 take more turns to see how this player reacts going forward. The player should now
        # move to a room and make a suggestion from that room
        print('\np02 takes a turn to move from a hallway to a room')
        turn_msg = p02.take_turn(game_state)

        print("\np02's prior moves in move order are:", p02._prior_moves_stack)
        print('\np02 is suspect {0} who starts in {1} as shown in prior moves stack'.
              format(p02._selected_suspect, p02._get_starting_location(p02._selected_suspect)))

        self.assertEqual(p02._get_starting_location(p02._selected_suspect), p02._prior_moves_stack[0])

        print('\np02 is now in the {0} and suggests {1}'.format(turn_msg['move'], turn_msg['suggestion']['cards']))

        # this suggestion should cause the suggested suspect to be moved to the suggested room.
        # match suspect to the proper player id
        player = self._get_player_from_suspect(players, turn_msg)
        # identify the room in the suggestion
        room_in_suggestion = self._match_card_with_type(CardType.room, turn_msg)

        # The caller (server) has the responsibility for completing the action of changing the position of the
        # player suspect in the suggestion and sending that through game_state. When the player in the suggestion
        # receives the position update, it will automatically change its position
        game_state = self.get_game_state(players)
        # adjust the one player's position who was in the suggestion
        game_state['positions'][player.player_id] = room_in_suggestion

        # send position update to all players. In this case, show new location information for the player in the
        # suggestion
        player.update(game_state)

        print('\nplayer id: {0} has suspect: {1} and moves to the {2} room'
              .format(player.player_id, player._selected_suspect, player._location))

        self.assertEqual(player._location, room_in_suggestion)

        # now let's make it the players turn who got moved to a room as a result of a suggestion by another player.
        # In this case, this player makes a suggestion from the current room and doesn't move from that room
        turn_msg = player.take_turn(game_state)

        print('\nThe player {0} stays in the {1} room and suggests {2}'
              .format(turn_msg['suggestion']['from_player'],
                      room_in_suggestion, turn_msg['suggestion']['cards']))

        # proves that the room value is empty when the player takes the turn
        self.assertEqual(turn_msg['move'], '')

    def move(self):
        # mark everything as known except a location that this player must move
        # to in multiple turns before making a suggestion
        pass

    # helper methods
    def _setup_players(self, total_players):
        """
        For creating all players - mock of human players and computer players.

        :param total_players:
        :return: initialized player objects, both mocked human players and computer players
        """

        players = []
        available_suspects = ['Mustard', 'Peacock', 'Plum', 'Green', 'Scarlet', 'White']

        # create a list of dealt hands to distribute to each of the players
        # this includes any human player because dealing the right number of cards
        # (a caller/server responsibility) must include human players.
        list_of_dealt_hands = self._deal_cards(total_players)

        # adding one to the upper-bound since python upper range enum doesn't include the last value in the range.
        for x in range(1, total_players + 1):
            # total players is a combination of human and computer players.
            self.player = Player('p0' + str(x), available_suspects, total_players)

            available_suspects.remove(self.player._selected_suspect)

            # deal this player cards. Must start x at 1 here since the list of dealt
            # hands is a list of lists (zero-based index). The first hand (0 in list) was dealt to the
            # human player so start at 1.
            self.player.receive_cards(list_of_dealt_hands[x - 1])

            # the additional hands of cards will be for the human players. Assigning these cards is out of
            # the control of the computer player and is not part of testing. Just needed to consider
            # human players when determining how many cards to deal to the computer players. Assumption is
            # that there is at least  human player for test setup purposes.
            players.append(self.player)

        return players

    def _deal_cards(self, num_total_players):
        """
        Dealing cards to players. This would normally be a server function.
        :param num_total_players:
        :return: a cards list containing a list of dealt hands.
        """

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
        """
        Convenience method for getting all of the cards in this game
        :rtype : set
        :return: a set of cards
        """
        _suspects = {
            'Scarlet', 'Plum', 'Mustard', 'Green', 'White', 'Peacock'
        }

        _rooms = {
            'Study', 'Hall', 'Lounge', 'Library', 'Billiard', 'Dining', 'Conservatory', 'Ballroom', 'Kitchen'
        }

        _weapons = {
            'Knife', 'Wrench', 'Revolver', 'Pipe', 'Rope', 'Candlestick'
        }

        # TODO remove if this comment isn't removed
        _hallways = {
            'Hallway_01', 'Hallway_02', 'Hallway_03', 'Hallway_04', 'Hallway_05', 'Hallway_06', 'Hallway_07',
            'Hallway_08', 'Hallway_09', 'Hallway_10', 'Hallway_11', 'Hallway_12'
        }

        return _suspects.union(_rooms.union(_weapons))

    def get_marked_cards(self, player):
        """
        Retrieves dealt or discovered cards

        :param player: the player whose cards will be retrieved
        :return: a list of cards
        """

        cards = []
        column = player._pad.get_player_table(player.player_id)['c1']
        i = 0
        for cell in column:
            if cell == 1:
                cards.append(column.index[i])
            i += 1

        return cards

    def get_game_state(self, players):
        """
        Build-up game state by interrogating the player objects in memory
        :param players:
        :return: game_state containing player positions
        """
        game_state = {'positions': {}}

        for player in players:
            # build-up game_state from player information
            game_state['positions'][player.player_id] = player._location

        return game_state

    def _display_player_position_game_state(self, game_state):
        """
        Pretty prints game state

        :param game_state:
        """
        print("\ngame_state positions:",
              textwrap.fill(
                  str(
                      [(key, game_state['positions'][key]) for key in sorted(game_state['positions'].keys())]
                  )
              )
        )

    def _get_player_from_suspect(self, players, turn_msg):
        suspect = self._match_card_with_type(CardType.suspect, turn_msg)

        for player in players:
            if player._selected_suspect == suspect:
                return player

    def _match_card_with_type(self, card_type, turn_msg):
        _suspects = {
            'Scarlet', 'Plum', 'Mustard', 'Green', 'White', 'Peacock'
        }

        _rooms = {
            'Study', 'Hall', 'Lounge', 'Library', 'Billiard', 'Dining', 'Conservatory', 'Ballroom', 'Kitchen'
        }

        _weapons = {
            'Knife', 'Wrench', 'Revolver', 'Pipe', 'Rope', 'Candlestick'
        }

        if CardType.suspect == card_type:
            return turn_msg['suggestion']['cards'].intersection(_suspects).pop()
        elif CardType.room == card_type:
            return turn_msg['suggestion']['cards'].intersection(_rooms).pop()
        else:
            return turn_msg['suggestion']['cards'].intersection(_weapons).pop()


class CardType(Enum):
    suspect = 1
    room = 2
    weapon = 3