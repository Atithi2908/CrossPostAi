import requests
import urllib.parse
from core.logger import setup_logger
from core.config import settings

logger = setup_logger("linkedin_service")

class LinkedInService:
    def __init__(self):
        self.api_version = "v2"
        self.base_url = "https://api.linkedin.com/v2"

    def get_login_url(self, state: str) -> str:
        logger.info("Generating LinkedIn OAuth login URL")
        
        if not settings.LINKEDIN_CLIENT_ID:
            raise ValueError("LINKEDIN_CLIENT_ID is missing")
            
        params = {
            "response_type": "code",
            "client_id": settings.LINKEDIN_CLIENT_ID,
            "redirect_uri": settings.LINKEDIN_REDIRECT_URI,
            "state": state,
            "scope": "openid,profile,w_member_social,email"
        }
        
        url = "https://www.linkedin.com/oauth/v2/authorization?" + urllib.parse.urlencode(params)
        return url

    def handle_callback(self, code: str) -> dict:
        logger.info("Handling LinkedIn OAuth callback")
        
        url = "https://www.linkedin.com/oauth/v2/accessToken"
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": settings.LINKEDIN_REDIRECT_URI,
            "client_id": settings.LINKEDIN_CLIENT_ID,
            "client_secret": settings.LINKEDIN_CLIENT_SECRET
        }
        
        try:
            # 1. Exchange code for access token
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            response = requests.post(url, data=data, headers=headers, timeout=30)
            response.raise_for_status()
            token_data = response.json()
            access_token = token_data.get("access_token")
            
            # 2. Retrieve user info (URN)
            author_urn = self._get_author_urn(access_token)
            
            return {
                "access_token": access_token,
                "author_urn": author_urn
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to authenticate with LinkedIn: {str(e)}")
            if e.response is not None:
                logger.error(f"Response: {e.response.text}")
            raise
            
    def _get_author_urn(self, access_token: str) -> str:
        url = f"{self.base_url}/userinfo"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "X-Restli-Protocol-Version": "2.0.0"
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        user_info = response.json()
        sub = user_info.get("sub")
        if not sub:
            raise ValueError("Could not retrieve 'sub' (URN) from LinkedIn profile")
            
        return f"urn:li:person:{sub}"

    def publish_post(self, text: str, access_token: str, author_urn: str) -> dict:
        logger.info(f"Publishing text post to LinkedIn for author: {author_urn}")
        
        if not access_token or not author_urn:
            raise ValueError("LinkedIn account not connected or missing token data")
            
        url = f"{self.base_url}/ugcPosts"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "X-Restli-Protocol-Version": "2.0.0",
            "Content-Type": "application/json"
        }
        
        payload = {
            "author": author_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": text
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            logger.info("Successfully published post to LinkedIn")
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to publish to LinkedIn: {str(e)}")
            if e.response is not None:
                logger.error(f"Response: {e.response.text}")
            raise
