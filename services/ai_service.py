import os
import json
from dotenv import load_dotenv
from typing import Optional, Dict, Any, List
from logger import logger

# Load environment variables
load_dotenv()

# Try to import tool functions
from services.tools import (
    get_job_details,
    get_available_jobs,
    get_job_questions,
    submit_application,
)

# Try to initialize Gemini client if package is available
from google import genai
from google.genai import types

# Initialize Gemini client with API key if available

client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))
logger.info("Successfully initialized Gemini client")


def talk_to_HR_agent(phone_number: str, text: str, media_url: Optional[str] = None, mime_type: Optional[str] = None, job_id: Optional[int] = None):
    """
    Single entry point for the HR agent that handles conversation and returns responses.
    
    Args:
        phone_number: The WhatsApp phone number of the user
        text: The text message from the user
        media_url: Optional URL to any media the user sent
        mime_type: Optional MIME type of the media
        job_id: Optional ID of a specific job to focus on
        
    Returns:
        str: The AI-generated response
    """
    # If Gemini API key is not configured, return a default response
    if not os.getenv('GEMINI_API_KEY'):
        logger.warning("Gemini API key not configured")
        return "Thank you for your message. Our HR team will review your application soon."
    
    try:
        logger.info(f"Processing message from {phone_number}")
        
        # Create a system prompt for Gemini
        system_prompt = """
        You are an AI HR Assistant for a company. Your primary role is to help candidates apply for jobs
        and answer their questions about available positions.
        
        You can help users with:
        1. Finding available job listings
        2. Providing details about specific jobs
        3. Getting screening questions for a position
        4. Submitting their job application
        
        Be professional, friendly, and conversational. Focus on understanding the candidate's
        needs and helping them find the right position.
        
        This conversation is happening over WhatsApp. Format your responses appropriately:
        - Use *bold* for emphasis
        - Use _italics_ for highlighting key points
        - Break long text into shorter paragraphs
        - Use numbered lists (1. Item) or bullet points (- Item) for clarity
        """
        
        # If a job ID is provided, add specific instructions for that job
        if job_id:
            try:
                from models import Job
                job = Job.query.get(job_id)
                if job and job.aiInstructions:
                    system_prompt += f"\n\nSpecial instructions for {job.jobTitle} role: {job.aiInstructions}"
                    logger.info(f"Added job-specific instructions for job_id: {job_id}")
            except Exception as e:
                logger.error(f"Error getting job details for job_id {job_id}", exc_info=True)
        
        system_prompt += f"\n\nthese are the available jobs right now: {get_available_jobs()}"

        # Handle media if provided
        media_context = ""
        if media_url and mime_type:
            logger.info(f"Media detected: {mime_type}")
            if "image" in mime_type:
                media_context = f"The user has shared an image with you. "
            elif "video" in mime_type:
                media_context = f"The user has shared a video with you. "
            elif "audio" in mime_type:
                media_context = f"The user has shared an audio message with you. "
            elif "application/pdf" in mime_type:
                media_context = f"The user has shared a PDF document with you. "
                
            if media_context:
                system_prompt += f"\n\n{media_context}You can acknowledge this, but you cannot view its contents directly."
                
        # Format conversation for Gemini
        contents = [{"role": "user", "parts": [{"text": text}]}]
        
        logger.info("Calling Gemini API with automatic function calling")
        # Call the Gemini API with automatic function calling
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                config=types.GenerateContentConfig(
                    tools=[
                        get_job_details,
                        get_available_jobs,
                        get_job_questions,
                        submit_application,
                    ],
                    automatic_function_calling=types.AutomaticFunctionCallingConfig(
                        disable=False
                    ),
                    temperature=0.7,
                    system_instruction=system_prompt,
                ),
                contents=contents
            )
            
            # Extract the final response
            final_response = response.text
            logger.info("Received response from Gemini API")
            
        except Exception as api_error:
            logger.error("Error calling Gemini API", exc_info=True)
            raise api_error
                
        return final_response
        
    except Exception as e:
        error_msg = f"Error processing message: {str(e)}"
        logger.error(error_msg, exc_info=True)
        
        # Return a default error response
        default_error_response = "I apologize, but I'm experiencing some technical difficulties. Our HR team will follow up with you shortly."
        return default_error_response 