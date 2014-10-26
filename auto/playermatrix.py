import numpy as np
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

        player = {'c1': pd.Series(int, index=cards),
                  'c2': pd.Series([set(), set(), set(), set(), set(), set(), set(), set(), set(), set(), set(), set(),
                                   set(), set(), set(), set(), set(), set(), set(), set(), set()],
                                  index=cards)}

        # data frame is a table for this user
        self.table = pd.DataFrame(player)
