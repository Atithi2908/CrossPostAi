from core.logger import setup_logger

logger = setup_logger("banner_service")

class BannerService:
    def generate_banner(self, text: str) -> str:
        logger.info("Generating banner image")
        return "storage/output/dummy_banner.png"
