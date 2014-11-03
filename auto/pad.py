import auto.playermatrix as pm

class Pad:
    """
    A Clue-Less note _pad to allow a computer player to track game activity

    """

    def __init__(self, number_of_players):

        # create a dictionary containing all of the players as columns
        # with a set of sub-columns to track cards that are played
        self.player_pad = {}

        for x in range(1, number_of_players + 1):
            self.player_pad['p0' + str(x)] = pm.PlayerMatrix()

    @property
    def players_list(self):
        """
        Gets the list of players in this players _pad

        :rtype : list of dictionary keys
        :return: the list of active players in this player's _pad
        """
        return self.player_pad.keys()

    def get_player_table(self, player_id):
        """
        :param player_id: id of player table to retrieve
        :rtype : Pandas.DataFrame
        :return : the entire table (in the _pad) for this player to track the game
        """
        return self.player_pad[player_id].table