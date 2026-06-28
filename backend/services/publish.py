from core.logger import setup_logger
from services.linkedin import LinkedInService

logger = setup_logger("publish_service")

class PublishService:
    def __init__(self):
        self.linkedin_service = LinkedInService()

    def publish_to_linkedin(self, text: str, access_token: str, author_urn: str) -> dict:
        """
        Unified method to publish content to LinkedIn using provided tokens
        """
        logger.info("PublishService: Initiating LinkedIn publish")
        
        if not access_token or not author_urn:
            raise ValueError("LinkedIn account not connected or missing token data")
            
        result = self.linkedin_service.publish_post(text, access_token, author_urn)
        logger.info("PublishService: Successfully published to LinkedIn")
        return result
