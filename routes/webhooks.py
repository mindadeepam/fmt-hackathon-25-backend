from flask import Blueprint, request, jsonify
from services.whatsapp import send_whatsapp_message
from services.ai_service import talk_to_HR_agent
from logger import logger
from typing import Optional
from models import Job, Question, db

webhooks = Blueprint('webhooks', __name__)

@webhooks.route('/whatsapp', methods=['POST'])
def whatsapp_webhook():
    """Handle incoming WhatsApp messages using the HR agent"""
    try:
        # Parse incoming WhatsApp data
        data = request.json
        data = data['entry'][0]['changes'][0]['value']
        if 'messages' in data:
            message = data['messages'][0]
            phone_number = message['from']

            # Extract message content based on type
            message_type = message.get('type', 'text')
            message_text = ''
            media_url = None
            mime_type = None
            
        if message_type == 'text':
            message_text = message['text']['body'].strip()
        elif message_type == 'image':
            media_url = message['image'].get('url', '')
            mime_type = 'image/jpeg'  # Default mime type for WhatsApp images
            message_text = message.get('caption', 'Image')
        elif message_type == 'video':
            media_url = message['video'].get('url', '')
            mime_type = 'video/mp4'  # Default mime type for WhatsApp videos
            message_text = message.get('caption', 'Video')
        elif message_type == 'audio':
            media_url = message['audio'].get('url', '')
            mime_type = 'audio/ogg'  # Default mime type for WhatsApp audio
            message_text = 'Audio message'
        elif message_type == 'document':
            media_url = message['document'].get('url', '')
            mime_type = message['document'].get('mime_type', 'application/octet-stream')
            message_text = message.get('caption', 'Document')
        
        # Log the incoming message
        logger.info(f"Message from {phone_number}: {message_text} | Media: {media_url} | Type: {mime_type}")
        
        # Process with the HR agent
        response = talk_to_HR_agent(
            phone_number=phone_number,
            text=message_text,
            media_url=media_url,
            mime_type=mime_type
        )
        
        # Send the response back to WhatsApp
        send_whatsapp_message(phone_number, response)
        logger.info(f"Sent response to {phone_number}")
        
        return "", 200
        
    except KeyError as ke:
        logger.error(f"Invalid WhatsApp webhook format: KeyError on {str(ke)}", exc_info=True)
        return "", 200  # Always return 200 to WhatsApp to avoid retries
    except Exception as e:
        logger.error(f"Error processing WhatsApp webhook", exc_info=True)
        return "", 200  # Always return 200 to WhatsApp to avoid retries

@webhooks.route('/whatsapp/verify', methods=['GET'])
def verify_webhook():
    """Verify webhook for WhatsApp Business API"""
    try:
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        verify_token = "testing"  # This should be loaded from environment variables
        
        if mode and token:
            if mode == 'subscribe' and token == verify_token:
                logger.info('WEBHOOK_VERIFIED - WhatsApp verification successful')
                return challenge, 200
            else:
                logger.warning(f'Verification Failed: mode={mode}, token={token}')
                return 'Verification Failed', 403
        
        logger.warning('Invalid webhook verification request - missing parameters')
        return 'Invalid Request', 400
    except Exception as e:
        logger.error("Error verifying webhook", exc_info=True)
        return 'Server Error', 500

@webhooks.route('/api/jobs', methods=['POST'])
def create_job():
    """Create a new job and its questions"""
    if not request.is_json:
        logger.warning("Job creation attempted with non-JSON request in webhooks")
        return jsonify({"error": "Request must be JSON"}), 400
    
    try:
        data = request.json
        logger.info(f"Received job creation request: {data.get('jobTitle', 'No title')}")
        
        # Validate required fields
        if not data.get('jobTitle'):
            logger.warning("Job creation failed - missing jobTitle field")
            return jsonify({"error": "Job title is required"}), 400
            
        if not data.get('department'):
            logger.warning("Job creation failed - missing department field")
            return jsonify({"error": "Department is required"}), 400
        
        # Create new job
        new_job = Job(
            title=data.get('jobTitle'),
            department=data.get('department'),
            description=data.get('description', ''),
            requirements=data.get('requirements', ''),
            ai_instructions=data.get('aiInstructions', '')
        )
        
        db.session.add(new_job)
        db.session.flush()  # To get the job ID
        
        # Create questions
        questions_added = 0
        for idx, question_data in enumerate(data.get('questions', [])):
            if question_data.get('text'):  # Only add non-empty questions
                question = Question(
                    job_id=new_job.id,
                    text=question_data.get('text'),
                    is_required=question_data.get('required', False),
                    order=idx
                )
                db.session.add(question)
                questions_added += 1
        
        db.session.commit()
        logger.info(f"Created job ID {new_job.id} with {questions_added} questions")
        
        return jsonify({
            "id": new_job.id, 
            "message": "Job created successfully",
            "title": new_job.title,
            "questionCount": questions_added
        }), 201
    except Exception as e:
        logger.error("Error creating job from webhook", exc_info=True)
        db.session.rollback()
        return jsonify({"error": f"Failed to create job: {str(e)}"}), 500 