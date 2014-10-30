import random
import itertools
from auto.board import Board
from auto.pad import Pad

"""
    :module:: automaton
    :platform: Unix, Windows
    :synopsis: The AI/Computer Player object for the game of Clue-Less.

    :moduleauthor: Ethan Wilansky, Shambhavi Sanskrit and Henoke Shiferaw

"""


class Player:
    """
    The player class to be instantiated for each requested Clue-Less computer/AI player

    """
    __board = Board()
    # this class variable (might not be needed by dealer, but here for convenience)
    player_count = 0

    def __init__(self, player_id, available_suspects_list, total_players):
        """
        Instantiate a player for the game and provided that the upper-limit of
        allowed players has not been reached.

        :param player_id: the id assigned to this player by the caller (p01 - p06)
        :param available_suspects_list [list <string>]
        :param total_players: int

        :var
            class vars:
            __board <networkx.Graph>
            player_count <int>
            instance vars:
            selected_player <string>
            dealt_cards [list<string>]
            location <string>
            prior_moves <string>
            pad [dictionary<auto.PlayerMatrix>]

        :raise
            IndexError if player count > 5
        """

        if self.player_count <= 5:

            # add to the player count so server knows # active autonomous player
            self.player_count += 1

            # instance variables needed for game play
            self.selected_suspect = self._get_player(available_suspects_list)
            self.dealt_cards = []
            self.location = self.get_starting_location(self.selected_suspect)
            # prior moves will initially contain just the starting position for this player
            self.prior_moves = [self.location]
            # create a player pad for this player with the total number of players specified
            self.pad = Pad(total_players)
            self.player_id = player_id

        else:
            raise IndexError('no more than 5 computer players allowed')

    @staticmethod
    def get_starting_location(selected_player):
        """
        Gets the starting position of the selected player.

        :param selected_player <string>
        :return: the selected player's starting hallway position
        :rtype : str
        """
        starting_positions = {
            'Scarlet': 'Hallway_02',
            'Mustard': 'Hallway_03',
            'White': 'Hallway_05',
            'Green': 'Hallway_06',
            'Peacock': 'Hallway_07',
            'Plum': 'Hallway_08'
        }

        return starting_positions[selected_player]

    @staticmethod
    def _get_player(available_players_list):
        """
        Randomly choose a player from a list of available players.

        :param self:
        :return: a randomly selected player
        :rtype : str
        """
        return random.choice(available_players_list)

    def receive_cards(self, dealt_cards):
        """
        Receive a set of cards from the dealer and store them.

        :param dealt_cards: list
        :return:  dealt cards
        :rtype: list<str>
        :raise:
            IndexError if # of cards not between 3 and 6
            ValueError if cards dealt are not in Cards data structure
        """
        if 3 <= len(dealt_cards) <= 6:
            self.dealt_cards = dealt_cards
        else:
            raise IndexError('the number of cards dealt, must be between 3 and 6')

        for card in dealt_cards:
            verified = self._verify_card(card)
            if not verified:
                raise ValueError('the card {0} is not valid'.format(card))

        self._mark_my_cards_on_pad(dealt_cards)

    def create_pad(self, number_players_in_game):
        """
        Create a note pad based on the number of players in the game
        :param number_players_in_game:
        """
        return Pad(number_players_in_game);

    @property
    def _get_suspects(self):
        """
        Get the suspects that are valid for this game.

        :return: valid suspects
        :rtype: list<str>
        """
        return ['Mustard', 'Scarlet', 'White', 'Plum', 'Green', 'Peacock']

    @property
    def _get_rooms(self):
        """
        Get the rooms that are valid for this game.

        :return: valid rooms
        :rtype: list<str>
        """
        return ['Study', 'Hall', 'Lounge', 'Library', 'Billiard', 'Dining', 'Conservatory', 'Ballroom', 'Kitchen']

    @property
    def _get_weapons(self):
        """
        Get the weapons that are valid for this game.

        :return: valid weapons
        :rtype: list<str>
        """
        return ['Knife', 'Wrench', 'Revolver', 'Pipe', 'Rope', 'Candlestick']

    @property
    def _get_lobbies(self):

        """
        Get the lobbies that are valid for this game.

        :return: valid lobbies
        :rtype: list<str>
        """
        return ['Hallway_01', 'Hallway_02', 'Hallway_03', 'Hallway_04', 'Hallway_05', 'Hallway_06', 'Hallway_07',
                'Hallway_08', 'Hallway_09', 'Hallway_10', 'Hallway_11', 'Hallway_12']

    @property
    def get_location(self):

        """
        Get the location of this player and store it as an instance variable for tracking location.

        :return: current location
        :rtype: str
        """
        return self.location

    def _verify_card(self, card_to_verify):

        """
        Verify that the card dealt is valid

        :param: card_to_verify <string>
        :return: true if card is valid. Otherwise, false
        :rtype: bool
        """
        cards = [self._get_suspects, self._get_rooms, self._get_weapons]
        allCards = list(itertools.chain(*cards))

        if card_to_verify in allCards:
            return True
        else:
            return False

    def _next_moves(self, current_location):
        """
        Finds all possible locations that can be the next move from the player's current position.

        :param current_location:
        :return: a list of possible next moves
        :rtype: list<str>
        """
        return self.__board.neighborhood(current_location, 1)

    def _filter_moves(self, game_state):

        """
        Find current position and next moves. This removes moves that are blocked.

        :param game_state:
        :return: available, non-blocked moves
        :rtype: set<str>
        """
        current_location = self.get_location
        moves = self._next_moves(current_location)
        available_moves = set()
        # if next moves show a match in game_state dictionary, then eliminate it from next_moves set
        for move in moves:
            if move not in game_state['Positions'].values():
                available_moves.add(move)
        return available_moves

    def _make_move(self, available_moves):

        """
        Make a move

        :param available_moves:
        :return: a dictionary containing the move command and a location to move or empty string
        :rtype : dict{'move':<str>}

        """
        turn_response = {}

        for move in available_moves:
            if move not in self.prior_moves:
                # populate the move key with this move (will be sent to caller)
                turn_response['move'] = move
                # add the move to prior moves list
                self.prior_moves.append(move)
                return turn_response
            elif move in self.prior_moves:
                # take this move if it's available even if it has already been taken. Nothing else to do
                turn_response['move'] = move
                return turn_response

        turn_response['move'] = ''
        return turn_response

    def take_turn(self, game_state):

        # move block
        """
        Take a turn given the game state.

        :param game_state: dictionary containing the state of the game position, suggestion and accusation keys.
          Key values are dictionaries as described in the interface specification.
        :return: dictionary containing a moveto, suggest and accuse key. Suggest and accuse values are lists of string
        """
        available_moves = self._filter_moves(game_state)
        turn_response = self._make_move(available_moves)
        # still need to make suggest and accuse functions that get called here
        # suggest block
        # initially, all that's known are the cards in my deck and any suggestions made prior to this turn
        # I will be creating a table with a column for each player and multiple cells/player (probably 10 or 12)
        # in the player's column. Each row will be a card.

        return turn_response

    def question(self, question_asked):

        """
        Ask this computer player a question about whether they have one of three cards

        :param question_asked: dictionary containing two keys: player_name <string> and cards<list>. Cards should
          contain three string values.
        :return:
        """
        answer = "I don't have that card"

        return answer

    def _mark_my_cards_on_pad(self, dealt_cards):

        """
        Mark the cards this player was dealt.

        :type dealt_cards: list
        :param dealt_cards: 
        """
        player_tbl = self.pad.get_player_table(self.player_id)

        for card in dealt_cards:
            # get this player's sub-table and mark that they have this set of cards (from 3 to 6)
            player_tbl['c1'][card] = 1

    def mark_pad(self, suggestion):

        # three possible suggestions are: True ("I have one of the cards suggested") if this player is not the one
        # making the suggestion. False, ("I don't have one of the cards suggested") whether or not this player is
        # the one making the suggestion. The actual card if this player is the one making the suggestion and there is
        # a match to share.

        """
        Given the suggestion, mark this player's pad.
        :param suggestion:
        """

        answer = suggestion['responded']
        responding_player = suggestion['player']
        # for the current player, get the sub-table for the responding player
        responding_player_tbl = self.pad.get_player_table(responding_player)

        if answer is True:
            card01 = suggestion['suggested'][0]
            card02 = suggestion['suggested'][1]
            card03 = suggestion['suggested'][2]

            # get the tracking cell lists
            cell01 = responding_player_tbl['c2'][card01]
            cell02 = responding_player_tbl['c2'][card02]
            cell03 = responding_player_tbl['c2'][card03]

            # check if any of the cards have been asked of this player before. If so, add the greatest increment
            # to each of the cells. This is done here by getting the length of the union of the cells and adding 1
            new_entry = len(cell01.union(cell02.union(cell03))) + 1
            cell01.add(new_entry)
            cell02.add(new_entry)
            cell03.add(new_entry)

        elif answer is False:
            pass
        else:
            card_provided = answer

            # locate player 1's column 1 for the specified card and put a 1 in it
            responding_player_tbl['c1'][answer] = 1

            self._clear_c2_cells(card_provided)

    def _clear_c2_cells(self, card_provided):
        # clear the corresponding col2 cell for the answered card
        # and do this for all of the players including this player
        for player in self.pad.players_list:
            tbl = self.pad.get_player_table(player)
            tbl['c2'][card_provided].clear()
