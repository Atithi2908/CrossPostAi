import os
from groq import Groq
from core.logger import setup_logger
from core.config import settings

logger = setup_logger("rewrite_service")

class RewriteService:
    def __init__(self):
        if settings.GROQ_API_KEY:
            self.client = Groq(api_key=settings.GROQ_API_KEY)
            self.model = "llama-3.3-70b-versatile"
        else:
            self.client = None
            logger.warning("Groq API key not configured")

    def rewrite_for_linkedin(self, transcript: str) -> str:
        logger.info("Rewriting transcript for LinkedIn using Groq")
        
        if not transcript.strip():
            logger.warning("Empty transcript provided")
            return ""
            
        if not self.client:
            logger.error("Groq API key is missing")
            raise ValueError("Groq API key is missing")
            
        prompt = f"""
Convert the following video transcript into a professional, engaging LinkedIn post.

Requirements:
- Preserve the original meaning.
- Improve grammar and readability.
- Create an engaging opening hook.
- Break the content into short paragraphs (1-2 sentences each).
- Add a concise call-to-action at the end.
- Generate 3-5 relevant hashtags at the bottom.

Transcript:
{transcript}
"""
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                model=self.model,
            )
            result = chat_completion.choices[0].message.content
            
            if not result:
                logger.error("Empty response from Groq")
                raise Exception("Empty response from Groq")
                
            logger.info("Successfully generated LinkedIn post")
            return result
            
        except Exception as e:
            logger.error(f"Error during Groq generation: {str(e)}")
            raise
