import argparse

from src.keywords import getKeywordsStats
from src.links import uploadLinks


parser = argparse.ArgumentParser(
    description='This programm is written for automate the process of finding links, keywords statistics.', prog='Keywords searcher')
# parser.add_argument('integers', metavar='N', type=int, nargs='+',
#                     help='an integer for the accumulator')
parser.add_argument('--links', dest='links', action='store_const',
                    const=uploadLinks,
                    help='Upload links for the keyword that is set in settings.json.')
parser.add_argument('--kwstats', dest='kwstats', action='store_const',
                    const=getKeywordsStats,
                    help='Upload keywords statistics (Also starts if none of the other parameter were given).')
