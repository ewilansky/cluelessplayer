import random
import itertools

class Player:
    # only class variable (might not be needed by dealer, but here for convenience)
    player_count = 0

    def __init__(self, available_players_list):
        """
        Instantiate a player for the game and provided that the upper-limit of
        allowed players has not been reached.

        :param available_players_list:
        :raise IndexError:
        """
        if self.player_count <= 5:

            # add to the player count so server knows # active autonomous player
            self.player_count += 1

            # instance variables needed for game play
            self.selected_player = self.get_player(available_players_list)
            self.dealt_cards = []
            self.location = self.get_starting_location(self.selected_player)

        else:
            raise IndexError('no more than 5 computer players allowed')

    @staticmethod
    def get_starting_location(selected_player):
        """
        Gets the starting position of the selected player.

        :param selected_player:
        :return: the players starting position
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

    def get_player(self, available_players_list: list):
        """
        Randomly choose a player from a list of available players.

        :param self:
        :return: a randomly selected player
        """
        return random.choice(available_players_list)

    def receive_cards(self, dealt_cards: list):
        """
        Receive a set of cards from the dealer and store them.

        :param  dealt_cards
        @return:  dealt cards
        """
        if 3 <= len(dealt_cards) <= 6:
            self.dealt_cards = dealt_cards
        else:
            raise IndexError('the number of cards dealt, must be between 3 and 6')

        for card in dealt_cards:
            verified = self.verify_card(card)
            if not verified:
                raise ValueError('the card {0} is not valid'.format(card))

        return self.dealt_cards

    @property
    def get_suspects(self):
        """
        Get the suspects that are valid for this game.

        :return: valid suspects
        """
        return ['Mustard', 'Scarlet', 'White', 'Plum', 'Green', 'Peacock']

    @property
    def get_rooms(self):
        """
        Get the rooms that are valid for this game.

        :return: valid rooms
        """
        return ['Study', 'Hall', 'Lounge', 'Library', 'Billiard', 'Dining', 'Conservatory', 'Ballroom', 'Kitchen']

    @property
    def get_weapons(self):
        """
        Get the weapons that are valid for this game.

        :return: valid weapons
        """
        return ['Knife', 'Wrench', 'Revolver', 'Pipe', 'Rope', 'Candlestick']

    @property
    def get_lobbies(self):
        """
        Get the lobbies that are valid for this game.

        :return: valid lobbies
        """
        return ['Hallway_01', 'Hallway_02', 'Hallway_03', 'Hallway_04', 'Hallway_05', 'Hallway_06', 'Hallway_07',
                'Hallway_08', 'Hallway_09', 'Hallway_10', 'Hallway_11', 'Hallway_12']

    def verify_card(self, card_to_verify):
        """
        Verify that the card dealt is valid

        :param card_to_verify
        """
        cards = [self.get_suspects, self.get_rooms, self.get_weapons]
        allCards = list(itertools.chain(*cards))

        if card_to_verify in allCards:
            return True
        else:
            return False

    def get_location(self):
        return self.location