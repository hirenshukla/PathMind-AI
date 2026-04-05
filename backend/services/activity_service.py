import logging
logger = logging.getLogger(__name__)
async def log_activity(db, user_id: int, action: str, metadata: dict = None):
    logger.info(f"Activity: user={user_id} action={action}")
