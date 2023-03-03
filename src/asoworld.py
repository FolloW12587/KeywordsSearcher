import logging
import os

from web.kwfinder import models


logger = logging.getLogger(__name__)


def upload_regions():
    """ Uploads regions from `resources/regions.csv` """
    path = "resources/regions.csv"

    if not os.path.isfile(path):
        logger.error(f"File {path} doesn't exist!")
        return

    with open(path, 'r') as regions_file:
        for line in regions_file:
            region = models.ASOWorldRegion.objects.filter(
                code=line.split(";")[0]
            ).first()

            if region:
                continue

            region = models.ASOWorldRegion(*line.split(";"))
            region.is_app_store_supported = region.is_app_store_supported == 'true'
            region.is_google_play_supported = region.is_google_play_supported == 'true'
            region.save()

    logger.info("Uploaded.")
