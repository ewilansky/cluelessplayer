from enum import Enum, unique

@unique
class Person(Enum):
    Mustard = 1
    Scarlet = 2
    White = 3
    Plum = 4
    Green = 5
    Peacock = 6

@unique
class Weapon(Enum):
    Knife = 1
    Wrench = 2
    Revolver = 3
    Pipe = 4
    Rope = 5
    Candlestick = 6

@unique
class Room(Enum):
    Study = 1
    Hall = 2
    Lounge = 3
    Library = 4
    Billiard = 5
    Dining = 6
    Conservatory = 7
    Ballroom = 8
    Kitchen = 9

@unique
class Lobby(Enum):
    Hallway_01 = 1
    Hallway_02 = 2
    Hallway_03 = 3
    Hallway_04 = 4
    Hallway_05 = 5
    Hallway_06 = 6
    Hallway_07 = 7
    Hallway_08 = 8
    Hallway_09 = 9
    Hallway_10 = 10
    Hallway_11 = 11
    Hallway_12 = 12
