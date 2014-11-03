import networkx as nx


class Board:
    """
    The Clue-Less _board graph

    """

    def __init__(self):
        """
        Creates the _board for the game of Clue-Less

        :var _board <networkx.Graph> class variable

        """
        self._board = nx.Graph()
        self._board.add_edges_from([('Study', 'Hallway_01'), ('Study', 'Hallway_03')])
        self._board.add_edges_from([('Hallway_01', 'Hall'), ('Hallway_03', 'Library')])
        self._board.add_edges_from([('Library', 'Hallway_08'), ('Hallway_08', 'Conservatory')])
        self._board.add_edges_from([('Conservatory', 'Hallway_11'), ('Hallway_11', 'Ballroom')])
        self._board.add_edges_from([('Ballroom', 'Hallway_12'), ('Hallway_12', 'Kitchen')])
        self._board.add_edges_from([('Hall', 'Hallway_04'), ('Hallway_04', 'Billiard')])
        self._board.add_edges_from([('Billiard', 'Hallway_09'), ('Hallway_09', 'Ballroom')])
        self._board.add_edges_from([('Hall', 'Hallway_02'), ('Hallway_02', 'Lounge')])
        self._board.add_edges_from([('Lounge', 'Hallway_05'), ('Hallway_05', 'Dining')])
        self._board.add_edges_from([('Dining', 'Hallway_10'), ('Hallway_10', 'Kitchen')])
        self._board.add_edges_from([('Library', 'Hallway_06'), ('Hallway_06', 'Billiard')])
        self._board.add_edges_from([('Billiard', 'Hallway_07'), ('Hallway_07', 'Dining')])
        self._board.add_edges_from([('Conservatory', 'Lounge'), ('Kitchen', 'Study')])

    def neighborhood(self, node, n):
        """
        Determines what nodes are n away from the target node.

        :param node: name of the target node <string>
        :param n: number of nodes away from the target node <int>
        :return: set of nodes set<string>
        """
        path_lengths = nx.single_source_dijkstra_path_length(self._board, node)
        return {node for node, length in path_lengths.items() if length == n}