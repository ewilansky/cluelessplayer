import pandas as pd

class PlayerMatrix:
    def __init__(self):
        """
        Create a player matrix for tracking that player's moves

        :rtype : Pandas.DataFrame
        """
        suspects = {
            'Scarlet', 'Plum', 'Mustard', 'Green', 'White', 'Peacock'
        }

        rooms = {
            'Study', 'Hall', 'Lounge', 'Library', 'Billiard', 'Dining', 'Conservatory', 'Ballroom', 'Kitchen'
        }

        weapons = {
            'Knife', 'Wrench', 'Revolver', 'Pipe', 'Rope', 'Candlestick'
        }

        cards = suspects.union(rooms.union(weapons))

        player = {'c1': pd.Series(int, index=cards),
                  'c2': pd.Series([set(), set(), set(), set(), set(), set(), set(), set(), set(), set(), set(), set(),
                                   set(), set(), set(), set(), set(), set(), set(), set(), set()],
                                  index=cards)}

        # data frame is a table for this user
        self.table = pd.DataFrame(player)
