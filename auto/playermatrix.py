import pandas as pd


class PlayerMatrix:
    def __init__(self):
        """
        Create a player matrix for tracking a player answers to suggestions.

        :var
            _suspects: dictionary
            _rooms: dictionary
            _weapons: dictionary
            _cards: dictionary
            _tracker: dictionary<Pandas.Series>

        :rtype : Pandas.DataFrame
        """
        _suspects = {
            'Scarlet', 'Plum', 'Mustard', 'Green', 'White', 'Peacock'
        }

        _rooms = {
            'Study', 'Hall', 'Lounge', 'Library', 'Billiard', 'Dining', 'Conservatory', 'Ballroom', 'Kitchen'
        }

        _weapons = {
            'Knife', 'Wrench', 'Revolver', 'Pipe', 'Rope', 'Candlestick'
        }

        _cards = _suspects.union(_rooms.union(_weapons))

        _tracker = {'c1': pd.Series(int, index=_cards),
                    'c2': pd.Series(
                        [set(), set(), set(), set(), set(), set(), set(), set(), set(), set(), set(), set(),
                         set(), set(), set(), set(), set(), set(), set(), set(), set()],
                        index=_cards)}

        # data frame is a table for this user
        self.table = pd.DataFrame(_tracker)
