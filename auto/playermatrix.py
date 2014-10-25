import pandas as pd


class PlayerMatrix:
    def __init__(self):
        """
        Create a player matrix for tracking that player's moves

        :rtype : Pandas.DataFrame
        """
        suspects = {
            'scarlet', 'plum', 'mustard', 'green', 'white', 'peacock'
        }

        rooms = {
            'study', 'hall', 'lounge', 'library', 'billiard', 'dining', 'conservatory', 'ballroom', 'kitchen'
        }

        weapons = {
            'knife', 'wrench', 'revolver', 'pipe', 'rope', 'candlestick'
        }

        cards = suspects.union(rooms.union(weapons))

        # for n in range(1 in number_of_players):
        player = {'c1': pd.Series(index=cards),
                  'c2': pd.Series(index=cards),
                  'c3': pd.Series(index=cards),
                  'c4': pd.Series(index=cards),
                  'c5': pd.Series(index=cards),
                  'c6': pd.Series(index=cards),
                  'c7': pd.Series(index=cards),
                  'c8': pd.Series(index=cards)}

        # data frame is a table for this user
        self.table = pd.DataFrame(player)
