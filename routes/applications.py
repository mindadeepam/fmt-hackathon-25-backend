from flask import Blueprint, request, jsonify
from models import db, Job, Application, Answer
from logger import logger

applications = Blueprint('applications', __name__)

@applications.route('/', methods=['GET'])
def get_applications():
    """Get all applications across all jobs"""
    try:
        applications = Application.query.all()
        logger.info(f"Retrieved {len(applications)} applications across all jobs")
        return jsonify([app.to_dict() for app in applications]), 200
    except Exception as e:
        logger.error("Error retrieving all applications", exc_info=True)
        return jsonify({"msg": f"Error retrieving applications: {str(e)}"}), 500

@applications.route('/jobs/<int:job_id>/applications', methods=['GET'])
def get_applications_for_job(job_id):
    """Get all applications for a specific job"""
    try:
        applications = Application.query.filter_by(job_id=job_id).all()
        logger.info(f"Retrieving applications for job {job_id}")
        return jsonify([app.to_dict() for app in applications]), 200
    except Exception as e:
        logger.error(f"Error retrieving applications for job {job_id}", exc_info=True)
        return jsonify({"msg": f"Error retrieving applications: {str(e)}"}), 500

@applications.route('/<int:application_id>', methods=['GET'])
def get_application(application_id):
    try:
        application = Application.query.get_or_404(application_id)
        logger.info(f"Retrieving application details for ID: {application_id}")
        return jsonify(application.to_dict()), 200
    except Exception as e:
        logger.error(f"Error retrieving application {application_id}", exc_info=True)
        return jsonify({"msg": f"Error retrieving application: {str(e)}"}), 500

@applications.route('/<int:application_id>/status', methods=['PUT'])
def update_application_status(application_id):
    if not request.is_json:
        logger.warning(f"Status update attempted with non-JSON request for application {application_id}")
        return jsonify({"msg": "Missing JSON in request"}), 400
    
    try:
        application = Application.query.get_or_404(application_id)
        data = request.json
        
        if 'status' not in data:
            logger.warning(f"Status update attempted without status field for application {application_id}")
            return jsonify({"msg": "Missing status field"}), 400
        
        # Validate status value
        valid_statuses = ['new', 'screening', 'interview', 'hired', 'rejected']
        if data['status'] not in valid_statuses:
            logger.warning(f"Invalid status '{data['status']}' provided for application {application_id}")
            return jsonify({"msg": f"Invalid status. Must be one of: {', '.join(valid_statuses)}"}), 400
        
        old_status = application.status
        application.status = data['status']
        db.session.commit()
        logger.info(f"Updated application {application_id} status from '{old_status}' to '{data['status']}'")
        
        return jsonify({"msg": "Status updated successfully"}), 200
    except Exception as e:
        logger.error(f"Error updating status for application {application_id}", exc_info=True)
        return jsonify({"msg": f"Error updating status: {str(e)}"}), 500

@applications.route('/create', methods=['POST'])
def create_application():
    """Public endpoint to submit a job application"""
    if not request.is_json:
        logger.warning("Application creation attempted with non-JSON request")
        return jsonify({"msg": "Missing JSON in request"}), 400
    
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['job_id', 'applicant_name', 'whatsapp_number']
        for field in required_fields:
            if field not in data:
                logger.warning(f"Application creation failed - missing {field} field")
                return jsonify({"msg": f"Missing {field} field"}), 400
        
        # Check if job exists
        job = Job.query.get(data['job_id'])
        if not job:
            logger.warning(f"Application creation failed - job ID {data['job_id']} not found")
            return jsonify({"msg": "Job not found"}), 404
        
        # Create new application
        new_application = Application(
            job_id=data['job_id'],
            applicant_name=data['applicant_name'],
            whatsapp_number=data['whatsapp_number'],
            resume_url=data.get('resume_url'),
            ai_summary=data.get('ai_summary', '')
        )
        
        db.session.add(new_application)
        db.session.commit()
        
        # Add answers if provided
        if 'questions_answers' in data and isinstance(data['questions_answers'], list):
            for answer_data in data['questions_answers']:
                if 'text' in answer_data and 'answer' in answer_data:
                    answer = Answer(
                        application_id=new_application.id,
                        question_text=answer_data['text'],
                        answer_text=answer_data['answer'],
                        required=answer_data.get('required', True)
                    )
                    db.session.add(answer)
            
            db.session.commit()
        
        logger.info(f"Created new application {new_application.id} for job {data['job_id']} from {data['applicant_name']}")
        
        return jsonify({
            "msg": "Application submitted successfully",
            "application_id": new_application.id
        }), 201
    except Exception as e:
        logger.error("Error creating application", exc_info=True)
        return jsonify({"msg": f"Error creating application: {str(e)}"}), 500 