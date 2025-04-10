import os
import requests
from dotenv import load_dotenv
from logger import logger

# Load environment variables
load_dotenv()


def send_whatsapp_message(recipient, message):
    """
    Send a WhatsApp message to the recipient.
    
    Args:
        recipient (str): The recipient's phone number
        message (str): The message to send
        
    Returns:
        bool: True if successful, False otherwise
    """
    whatsapp_api_token = os.getenv('WHATSAPP_API_TOKEN')
    whatsapp_api_version = os.getenv('WHATSAPP_API_VERSION', 'v22.0')
    whatsapp_phone_number_id = os.getenv('WHATSAPP_PHONE_NUMBER_ID')
    
    whatsapp_api_url = f"https://graph.facebook.com/{whatsapp_api_version}/{whatsapp_phone_number_id}/messages"
    
    if not whatsapp_api_url or not whatsapp_api_token:
        # Log that WhatsApp integration is not configured
        logger.warning(f"WhatsApp API not configured. Would send to {recipient}: {message[:30]}...")
        return False
    
    try:
        logger.info(f"Sending WhatsApp message to {recipient} (length: {len(message)} chars)")
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient,
            "type": "text",
            "text": {
                "body": message
            }
        }
        
        headers = {
            "Authorization": f"Bearer {whatsapp_api_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(whatsapp_api_url, json=payload, headers=headers)
        if response.status_code != 200:
            logger.error(f"Failed to send WhatsApp message: HTTP {response.status_code} - {response.text}")
            return False
        
        logger.info(f"Successfully sent WhatsApp message to {recipient}")
        return True
    except Exception as e:
        logger.error(f"Error sending WhatsApp message to {recipient}", exc_info=True)
        return False

def get_media_url(media_id):
    """
    Get the URL for a media file from WhatsApp API.
    
    Args:
        media_id (str): The media ID from WhatsApp
        
    Returns:
        str: The URL to download the media, or None if failed
    """
    whatsapp_api_token = os.getenv('WHATSAPP_API_TOKEN')
    whatsapp_api_version = os.getenv('WHATSAPP_API_VERSION', 'v22.0')
    whatsapp_phone_number_id = os.getenv('WHATSAPP_PHONE_NUMBER_ID')
    
    if not all([whatsapp_api_token, whatsapp_phone_number_id]):
        logger.warning("WhatsApp API not fully configured for media download")
        return None
    
    try:
        logger.info(f"Retrieving media URL for media ID: {media_id}")
        
        # Construct the URL to get media URL
        media_url = f"https://graph.facebook.com/{whatsapp_api_version}/{whatsapp_phone_number_id}/media/{media_id}"
        
        headers = {
            "Authorization": f"Bearer {whatsapp_api_token}"
        }
        
        response = requests.get(media_url, headers=headers)
        if response.status_code != 200:
            logger.error(f"Failed to get media URL: HTTP {response.status_code} - {response.text}")
            return None
            
        media_data = response.json()
        media_url = media_data.get('url')
        logger.info(f"Successfully retrieved media URL for media ID {media_id}")
        return media_url
    except Exception as e:
        logger.error(f"Error getting WhatsApp media URL for media ID {media_id}", exc_info=True)
        return None 