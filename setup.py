try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'Autonomous Player for the game, Clueless',
    'author': 'Team Autonomous',
    'url': 'localhost',
    'download_url': 'localhost',
    'author_email': 'autonomous@jhu.edu',
    'version': '0.1',
    'install_requires': [''],
    'packages': ['NAME'],
    'scripts': [],
    'name': 'cluelessplayer'
}

setup(**config, requires=['networkx'])