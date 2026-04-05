import logging
logger = logging.getLogger(__name__)
async def send_verification_email(email: str, name: str):
    logger.info(f"[EMAIL] Verification -> {email}")
async def send_reset_email(email: str, token: str):
    logger.info(f"[EMAIL] Reset -> {email}")
