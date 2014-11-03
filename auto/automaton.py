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

    # player_count class variable enforces the maximum # of players allowed. See IndexError in constructor
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
            __board: networkx.Graph
            player_count: int
            instance vars:
            selected_player: string
            dealt_cards: list<string>
            location: string
            _prior_moves: string
            pad: dictionary<auto.PlayerMatrix

        :raise
            IndexError if player count > 5
        """

        if self.player_count <= 5:

            # add to the player count so server knows # active autonomous player
            self.player_count += 1

            # instance variables needed for game play
            self.selected_suspect = self._get_player(available_suspects_list)
            # to start, the location is the starting position for this player based on selected suspect
            self.location = self._get_starting_location(self.selected_suspect)

            # prior moves set will initially contain just the starting position for this player
            self._prior_moves = {self.location}
            # create a player pad for this player with the total number of players specified
            self.pad = Pad(total_players)
            self.player_id = player_id

        else:
            raise IndexError('no more than 5 computer players allowed')

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
        # if 3 <= len(dealt_cards) <= 6:
        # self.dealt_cards = dealt_cards
        # else:

        if not 3 <= len(dealt_cards) <= 6:
            raise IndexError('the number of cards dealt, must be between 3 and 6')

        for card in dealt_cards:
            verified = self._verify_card(card)
            if not verified:
                raise ValueError('the card {0} is not valid'.format(card))

        self._mark_my_cards_on_pad(dealt_cards)

    def update(self, game_state):

        # example game_state for taking a turn that includes a suggestion
        # game_state = {'move': {'location': 'Lounge', 'player_id': 'p01'},
        # 'suggest': {'cards': ['Mustard', 'Lounge', 'Rope'], 'to_player': 'p02'}}
        if 'suggest' in game_state and game_state['suggest']['to_player'] == self.player_id:
            return self._answer(game_state['suggest']['cards'])

        # example game_state for letting the player who made a suggestion know of a response (directed answer)
        # game_state = {'answer': 'Mustard', 'from_player': 'p02'}
        # example game_state for letting other players know of a response (undirected answer)
        # game_state = {'answer': True, 'from_player': 'p02', 'suggested': ['Plum', 'Hall', 'Candlestick']}
        if 'answer' in game_state:
            self._mark_pad(game_state)

            # example game_state when a player makes a move and nothing more
            # game_state = {'move': }

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
        # if there is a suggestion or accusation, the privates will build-up the turn_response
        # with additional information
        # something like turn_response: self._suggest(turn_response)

        return turn_response

    # private functions
    # def _create_pad(self, number_players_in_game):
    #     """
    #     Create a note pad based on the number of players in the game
    #     :param number_players_in_game:
    #     """
    #     return Pad(number_players_in_game)

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
    def _get_location(self):

        """
        Get the location of this player and store it as an instance variable for tracking location.

        :return: current location
        :rtype: str
        """
        return self.location

    def _set_location(self, game_state):
        """
        Sets the current location based on the game_state returned by the caller/server

        :param game_state: {'positions': {<pid>: <location>, ...}}
        :return:
        """

        self.location = game_state['positions'][self.player_id]
        self._prior_moves.add(self.location)

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
        # set current location to the position reported in game_state
        self._set_location(game_state)
        # get the possible next moves, given the current location
        moves = self._next_moves(self.location)

        available_moves = set()
        # if next moves show a match in the set of prior moves, then eliminate it from next_moves set
        for move in moves:
            if move not in self._prior_moves:
                available_moves.add(move)

        # if available_moves is an empty set, then randomly select an available move
        if not available_moves:
            pick_me = random.sample(moves, 1)
            available_moves.add(pick_me[0])

        return available_moves

    def _make_move(self, available_moves):

        """
        Make a move

        :param available_moves:
        :return: a dictionary containing the move command and a location to move or empty string
        :rtype : dict{'move':<str>} example: {'move': {'location': 'Kitchen', 'player': 'p01'},


        """
        turn_response = {'move': {'location': '', 'player': self.player_id}}

        for move in available_moves:
            if move not in self._prior_moves:
                # populate the move key with this move (will be sent to caller)
                turn_response['move']['location'] = move
                # add the move to prior moves list
                self._prior_moves.add(move)
                return turn_response
            elif move in self._prior_moves:
                # take this move if it's available even if it has already been taken. Nothing else to do
                turn_response['move']['location'] = move
                return turn_response

        return turn_response

    def _answer(self, suggestion):

        """
        Ask this computer player a question about whether they have one of three cards

        :param suggestion: list<string> containing three valid card values.

        :return: string containing a valid card value or no_match
        """

        my_cards = self.pad.get_player_table(self.player_id)['c1']

        # improve this by preferring not to return room cards because there are more
        # room cards than any other cards. Helps to keep the other players guessing.
        for card in suggestion:
            if card in my_cards:
                return card
            else:
                return 'no_match'

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

    def _mark_pad(self, game_state):

        # three possible suggestions are: True ("I have one of the cards suggested") if this player is not the one
        # making the suggestion. False, ("I don't have one of the cards suggested") whether or not this player is
        # the one making the suggestion. The actual card if this player is the one making the suggestion and there is
        # a match to share.

        """
        Given the suggestion, mark this player's pad.
        :param game_state:
        """

        # example game_state for letting other players know of a response (undirected answer)
        # game_state = {'answer': True, 'from_player': 'p02', 'suggested': ['Plum', 'Hall', 'Candlestick']}


        answer = game_state['answer']
        responding_player = game_state['from_player']
        # for the current player, get the sub-table for the responding player
        responding_player_tbl = self.pad.get_player_table(responding_player)

        if answer is True:
            card01 = game_state['suggested'][0]
            card02 = game_state['suggested'][1]
            card03 = game_state['suggested'][2]

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


    def _get_player(self, available_players_list):
        """
        Randomly choose a player from a list of available players. This determines starting position on board.

        :param available_players_list:list
        :return: a randomly selected player
        :rtype : str
        """
        return random.choice(available_players_list)


    def _get_starting_location(self, selected_player):
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
