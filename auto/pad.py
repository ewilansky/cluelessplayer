import pandas as pd
import auto.playermatrix as pm


class Pad:
    """
    A Clue-Less note pad to allow a computer player to track game activity

    """

    def __init__(self, number_of_players):

        # create a dictionary containing all of the players as columns
        # with a set of sub-columns to track cards that are played
        self.players_pad = {}
        for x in range(1, number_of_players + 1):
            self.players_pad['p0' + str(x)] = pm.PlayerMatrix()

    @property
    def players_list(self):
        return self.players_pad.keys()

    def get_player_table(self, player_id):
        return self.players_pad[player_id].table

    def has_card(self, card, player):

        """
        Record that another user has a card

        :param card:
        :raise ValueError: if card specified is invalid
        """

        # is the player currently in the pad (check the columns)

        has_card = True
        if card in self.suspects:
            self.suspects[card] = has_card
        elif card in self.weapons:
            self.weapons[card] = has_card
        elif card in self.rooms:
            self.rooms[card] = has_card
        else:
            raise ValueError('invalid card specified')

    def player_revealed_card(self, cards_asked):
        """
        Record that a player told another player that they had one of the cards suggested

        :param cards_asked: dictionary containing weapon, room and suspect keys
        :exception ValueError if three valid cards are not specified
        """
        if 'weapon' and 'room' and 'suspect' not in cards_asked:
            raise ValueError('specify weapon, room and suspect keys')
        else:
            self.weapons[cards_asked['weapon']] += 0b0000010
            self.weapons[cards_asked['room']] += 0b0000010
            self.weapons[cards_asked['suspect']] += 0b0000010