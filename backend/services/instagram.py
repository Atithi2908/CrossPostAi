import os
import requests
import urllib.parse
from core.logger import setup_logger
from core.config import settings

logger = setup_logger("instagram_service")

class InstagramService:
    def __init__(self):
        self.api_version = "v19.0"
        self.base_url = f"https://graph.facebook.com/{self.api_version}"

    def get_login_url(self, state: str) -> str:
        logger.info("Generating Facebook login URL for Instagram Graph API")
        
        if not settings.INSTAGRAM_CLIENT_ID:
            logger.error("INSTAGRAM_CLIENT_ID is missing")
            raise ValueError("INSTAGRAM_CLIENT_ID is missing")
            
        params = {
            "client_id": settings.INSTAGRAM_CLIENT_ID,
            "redirect_uri": settings.INSTAGRAM_REDIRECT_URI,
            "state": state,
            "scope": "instagram_basic,pages_show_list,pages_read_engagement,business_management",
            "response_type": "code"
        }
        
        url = f"https://www.facebook.com/{self.api_version}/dialog/oauth?" + urllib.parse.urlencode(params)
        return url
        
    def handle_callback(self, code: str) -> dict:
        logger.info(f"Handling Facebook callback to exchange code")
        
        url = f"{self.base_url}/oauth/access_token"
        params = {
            "client_id": settings.INSTAGRAM_CLIENT_ID,
            "client_secret": settings.INSTAGRAM_CLIENT_SECRET,
            "redirect_uri": settings.INSTAGRAM_REDIRECT_URI,
            "code": code
        }
        
        try:
            # 1. Exchange code for short-lived access token
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            token_data = response.json()
            short_lived_token = token_data.get("access_token")
            
            # 2. Exchange for long-lived access token
            long_lived_params = {
                "grant_type": "fb_exchange_token",
                "client_id": settings.INSTAGRAM_CLIENT_ID,
                "client_secret": settings.INSTAGRAM_CLIENT_SECRET,
                "fb_exchange_token": short_lived_token
            }
            long_lived_resp = requests.get(url, params=long_lived_params, timeout=30)
            long_lived_resp.raise_for_status()
            long_lived_data = long_lived_resp.json()
            
            # 3. Get User's Pages to find connected Instagram Business Account
            access_token = long_lived_data.get("access_token")
            ig_account_id = self._get_instagram_account_id(access_token)
            
            if not ig_account_id:
                raise ValueError("No Instagram Professional account found connected to any Facebook Pages.")
                
            return {
                "access_token": access_token,
                "ig_account_id": ig_account_id
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to authenticate with Facebook/Instagram API: {str(e)}")
            if e.response is not None:
                logger.error(f"Response: {e.response.text}")
            raise
            
    def _get_instagram_account_id(self, access_token: str) -> str:
        # Fetch Facebook Pages
        pages_url = f"{self.base_url}/me/accounts"
        params = {"access_token": access_token}
        
        resp = requests.get(pages_url, params=params, timeout=30)
        logger.info(f"DEBUG /me/accounts status code: {resp.status_code}")
        logger.info(f"DEBUG /me/accounts response: {resp.text}")
        resp.raise_for_status()
        
        pages_json = resp.json()
        pages = pages_json.get("data", [])
        
        # Iterate over pages to find one with an Instagram Business Account
        for page in pages:
            page_id = page.get("id")
            page_name = page.get("name", "Unknown")
            page_token = page.get("access_token")
            has_token = bool(page_token)
            
            logger.info(f"DEBUG Page ID: {page_id} | Page Name: {page_name} | Has Access Token: {has_token}")
            
            ig_url = f"{self.base_url}/{page_id}?fields=instagram_business_account"
            ig_resp = requests.get(ig_url, params={"access_token": page_token}, timeout=30)
            
            logger.info(f"DEBUG /{page_id} status code: {ig_resp.status_code}")
            logger.info(f"DEBUG /{page_id} response: {ig_resp.text}")
            ig_resp.raise_for_status()
            
            ig_data = ig_resp.json()
            
            if "instagram_business_account" in ig_data:
                return ig_data["instagram_business_account"]["id"]
                
        return None

    def get_latest_reel(self, ig_account_id: str, access_token: str) -> dict:
        url = f"{self.base_url}/{ig_account_id}/media"
        params = {
            "fields": "id,caption,media_type,media_url,timestamp",
            "access_token": access_token,
            "limit": 10
        }
        
        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        media_list = resp.json().get("data", [])
        
        for media in media_list:
            if media.get("media_type") == "VIDEO":
                return media
                
        raise ValueError("No video (Reel) found in the recent media.")

    def download_reel(self, ig_account_id: str, access_token: str) -> str:
        logger.info("Downloading reel from Instagram")
        
        if not access_token or not ig_account_id:
            logger.error("Instagram token missing or invalid")
            raise ValueError("Instagram account not connected or missing token data")
        
        try:
            # Get the actual reel
            latest_reel = self.get_latest_reel(ig_account_id, access_token)
            media_url = latest_reel.get("media_url")
            reel_id = latest_reel.get("id")
            
            if not media_url:
                raise ValueError("Could not find media_url for the latest reel")
                
            # Download the video file
            logger.info(f"Downloading video from {media_url}")
            video_resp = requests.get(media_url, stream=True, timeout=60)
            video_resp.raise_for_status()
            
            output_path = os.path.join(settings.OUTPUT_DIR, f"{reel_id}.mp4")
            with open(output_path, "wb") as f:
                for chunk in video_resp.iter_content(chunk_size=8192):
                    f.write(chunk)
                    
            logger.info(f"Reel successfully downloaded to {output_path}")
            return output_path
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to interact with Instagram Graph API: {str(e)}")
            if e.response is not None:
                logger.error(f"Response: {e.response.text}")
            raise
