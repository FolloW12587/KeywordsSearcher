from concurrent.futures import ThreadPoolExecutor
import logging

from arguments import parser
import logs
from src.keywords import getKeywordsStats
from src.links import uploadLinks

logger = logging.getLogger(__name__)


def main():
    """ Main function """
    args = parser.parse_args()
    logger.info("Started main function")

    # if flag for upload links was given
    if args.links:
        uploadLinks()
    # if flag for upload keywords stats was given
    if args.kwstats:
        getKeywordsStats()

    # By default if there were no any other flags, start getting keywords statistics
    if not args.links and not args.kwstats:
        getKeywordsStats()
    
    logger.info("Finished")


if __name__ == "__main__":
    main()
