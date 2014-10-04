import random
#   from auto.gameentity import Suspect, Weapon, Room
import itertools

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
        return ['Mustard', 'Scarlet', 'White', 'Plum', 'Green', 'Peacock']

    @property
    def get_rooms(self):
        return ['Study', 'Hall', 'Lounge', 'Library', 'Billiard', 'Dining', 'Conservatory', 'Ballroom', 'Kitchen']

    @property
    def get_weapons(self):
        return ['Knife', 'Wrench', 'Revolver', 'Pipe', 'Rope', 'Candlestick']

    def verify_card(self, card_to_verify):
        """
        Verify that the cards dealt are valid

        :param dealt_cards:
        """

        cards = [self.get_suspects, self.get_rooms, self.get_weapons]

        allCards = list(itertools.chain(*cards))

        if card_to_verify in allCards:
            return True
        else:
            return False

        # for item_type in cards:


            # for name, member in item_type.__members__.items():
            #     # if member.name == name and name == card_to_verify:
            #     if card_to_verify in item_type.__members__.items():
            #         continue
            #     else:
            #         return False

            # var = [name for name, member in item_type.__members__.items() if member.name == name and name == card_to_verify]

            # print('done')
