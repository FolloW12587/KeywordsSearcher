import argparse


parser = argparse.ArgumentParser(
    description='This programm is written for automate the process of finding links, keywords statistics.', prog='Keywords searcher')
parser.add_argument('--links', action='store_true',
                    help='Upload links for the keyword that is set in settings.json.')
parser.add_argument('--kwstats', action='store_true',
                    help='Upload keywords statistics (Also starts if none of the other parameter were given).')
# parser.add_argument('--mergestats', action='store_true',
#                     help='Merges statistics for given days.')
parser.add_argument('--mergestats', metavar='D', type=str, nargs='*',
                    help='Merges statistics for given days.')
