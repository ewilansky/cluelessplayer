import random
import itertools
from auto.board import Board
from auto.pad import Pad

"""
    :module:: automaton
    :platform: Unix, Windows
    :synopsis: A useful module indeed.

    :moduleauthor:: Ethan Wilansky, Shambhavi Sanskrit and Henoke Shiferaw

"""

class Player:
    """
    The player class to be instantiated for each requested Clue-Less computer/AI player

    """
    __board = Board()
    # this class variable (might not be needed by dealer, but here for convenience)
    player_count = 0

    def __init__(self, available_players_list):
        """
        Instantiate a player for the game and provided that the upper-limit of
        allowed players has not been reached.

        :param available_players_list [list <string>]
        :var
            __board <networkx.Graph> (scope: class)
            player_count <int> (scope: class)
            selected_player <string> (scope: instance)
            dealt_cards [list<string>] (scope: instance)
            location <string> (scope: instance)

        :raise
            IndexError if player count > 5
        """
        if self.player_count <= 5:

            # add to the player count so server knows # active autonomous player
            self.player_count += 1

            # instance variables needed for game play
            self.selected_player = self.__get_player(available_players_list)
            self.dealt_cards = []
            self.location = self.get_starting_location(self.selected_player)
            # prior moves will initially contain just the starting position for this player
            self.prior_moves = [self.location]

        else:
            raise IndexError('no more than 5 computer players allowed')

    def get_starting_location(self, selected_player):
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

    def __get_player(self, available_players_list):
        """
        Randomly choose a player from a list of available players.

        :param self:
        :return: a randomly selected player
        :rtype : str
        """
        return random.choice(available_players_list)

    def receive_cards(self, dealt_cards: list):
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
            verified = self.__verify_card(card)
            if not verified:
                raise ValueError('the card {0} is not valid'.format(card))

        return self.dealt_cards

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

    def __verify_card(self, card_to_verify):

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

    def __filter_moves(self, game_state):

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
            if move not in game_state.values():
                available_moves.add(move)
        return available_moves

    def __make_move(self, available_moves):

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

    def take_turn(self, game_state: dict):

        # move block
        """
        Take a turn given the game state.

        :param game_state: dictionary containing the state of the game position, suggestion and accusation keys.
          Key values are dictionaries as described in the interface specification.
        :return: dictionary containing a moveto, suggest and accuse key. Suggest and accuse values are lists of string
        """
        available_moves = self.__filter_moves(game_state)
        turn_response = self.__make_move(available_moves)
        # still need to make suggest and accuse functions that get called here
        # suggest block
        # initially, all that's known are the cards in my deck and any suggestions made prior to this turn
        # I will be creating a table with a column for each player and multiple cells/player (probably 10 or 12)
        # in the player's column. Each row will be a card.

        return turn_response

    def notify_card_revealed(self, response: dict):

        # from the response, figure out what cards where asked ad whether the other player said they had a
        # a card. If so, mark the internal players table and calculate whether you can figure out
        # which card was revealed.

        """
        Reveal that a card was revealed and optionally, depending on who asked, the card that was revealed.

        :param response: dictionary containing a response with three keys match, card and player_name. Match is a
          Boolean, player_name is a string and card is a string. Card will contain a value only if the server is
          sending a response to the Autonomous player who asked if another player had a card.
        """

        print(response["match"])
        pass


    def question(self, question_asked: dict):

        """
        Ask this computer player a question about whether they have one of three cards
        :param question_asked: dictionary containing two keys: player_name <string> and cards<list>. Cards should
          contain three string values.
        :return:
        """
        answer = "I don't have that card"

        return answer