import random

class Player:
    # only class variable (might not be needed by dealer, but here for convenience)
    player_count = 0

    def __init__(self, available_players_list):
        if self.player_count <= 5:

            # select a player
            self.selected_player = self.get_player(available_players_list)

            # add to the player count so server knows # active autonomous player
            self.player_count += 1

            # instance variables needed for game play
            self.dealt_cards = []
        else:
            raise IndexError('no more than 5 computer players allowed')

    # randomly select a player from the list
    def get_player(self, available_players_list: list):
        """
        :param available_players_list:
        :return: a randomly selected player
        """

        return random.choice(available_players_list)

    def receive_cards(self, dealt_cards: list):
        """
        Receive a set of cards from the dealer and store them.

        :param  dealt_cards
        @return:  dealt cards
        """
        if dealt_cards.count(self) >= 3 or dealt_cards.count(self) <= 6:
            self.dealt_cards = dealt_cards
        else:
            raise IndexError('the number of cards dealt, must be between 3 and 6')

        return self.dealt_cards