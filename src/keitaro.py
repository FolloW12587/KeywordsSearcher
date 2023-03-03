from datetime import date
import logging

from web.kwfinder.services.keitaro import KeitaroAPIService
from web.kwfinder import models

logger = logging.getLogger(__name__)


def update_keitaro_stats(date_from: date, date_to: date):
    """ Uploads keitaro statistics for period from `date_from` to `date_to`.

    Args:
        date_from (date): start of the period
        date_to (date): end of the period
    """
    logger.info(f"Uploading keitaro stats for period {date_from} to {date_to}")
    campaign_ids = list(models.App.objects.filter(
        is_active=True).values_list("campaign_id", flat=True))

    if len(campaign_ids) == 0:
        logger.info("No active campaigns to update stats.")
        return

    service = KeitaroAPIService()

    rows = service.getReport(
        campaign_id_list=campaign_ids,
        date_from=date_from,
        date_to=date_to
    )
    logger.info(f"Uploaded {len(rows)} rows. Updating database.")

    for row in rows:
        app = models.App.objects.filter(
            campaign_id=row[models.KeitaroDailyAppData.CAMPAIGN_ID_FIELD_NAME]).first()

        stat = models.KeitaroDailyAppData.objects.filter(
            app=app,
            date=row[models.KeitaroDailyAppData.DATE_FIELD_NAME]
        ).first()

        if stat == None:
            stat = models.KeitaroDailyAppData(
                date=row[models.KeitaroDailyAppData.DATE_FIELD_NAME],
                app=app
            )

        stat.unique_users_count = row[models.KeitaroDailyAppData.UNIQUE_USERS_COUNT_FIELD_NAME]
        stat.conversions_count = row[models.KeitaroDailyAppData.CONVERSIONS_COUNT_FIELD_NAME]
        stat.sales_count = row[models.KeitaroDailyAppData.SALES_COUNT_FIELD_NAME]
        stat.revenue = row[models.KeitaroDailyAppData.REVENUE_FIELD_NAME]

        stat.save()

    logger.info("Update ended!")
