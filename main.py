from concurrent.futures import ThreadPoolExecutor
import logging

from arguments import parser
import logs
from src.keywords import getKeywordsStats

logger = logging.getLogger(__name__)


def main():
    """ Main function """
    args = parser.parse_args()
    logger.info("Started main function")

    # if flag for upload links was given
    if args.links:
        args.links()

    # if flag for upload keywords stats was given
    if args.kwstats:
        args.kwstats()

    # By default if there were no any other flags, start getting keywords statistics
    if not args.links and not args.kwstats:
        getKeywordsStats()
    
    logger.info("Finished")


if __name__ == "__main__":
    main()
