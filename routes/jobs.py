from flask import Blueprint, request, jsonify
from models import db, Job, Question
from logger import logger

jobs = Blueprint('jobs', __name__)

@jobs.route('/', methods=['GET'])
def get_jobs():
    try:
        jobs = Job.query.all()
        logger.info(f"Retrieved {len(jobs)} jobs")
        return jsonify([job.to_dict() for job in jobs]), 200
    except Exception as e:
        logger.error("Error retrieving jobs", exc_info=True)
        return jsonify({"msg": "Error retrieving jobs"}), 500

@jobs.route('/<int:job_id>', methods=['GET'])
def get_job(job_id):
    try:
        job = Job.query.get_or_404(job_id)
        logger.info(f"Retrieved job details for job ID: {job_id}")
        return jsonify(job.to_dict()), 200
    except Exception as e:
        logger.error(f"Error retrieving job with ID {job_id}", exc_info=True)
        return jsonify({"msg": f"Error retrieving job: {str(e)}"}), 500

@jobs.route('/', methods=['POST'])
def create_job():
    if not request.is_json:
        logger.warning("Job creation attempted with non-JSON request")
        return jsonify({"msg": "Missing JSON in request"}), 400
    
    data = request.json
    
    try:
        # Validate required fields
        required_fields = ['jobTitle', 'department', 'description', 'requirements']
        for field in required_fields:
            if field not in data:
                logger.warning(f"Job creation failed - missing {field} field")
                return jsonify({"msg": f"Missing {field} field"}), 400
        
        # Create new job
        new_job = Job(
            jobTitle=data['jobTitle'],
            department=data['department'],
            description=data['description'],
            requirements=data['requirements'],
            aiInstructions=data.get('aiInstructions', '')
        )
        
        db.session.add(new_job)
        db.session.flush()  # To get the job ID
        
        # Add questions if provided
        questions_added = 0
        if 'questions' in data and isinstance(data['questions'], list):
            for q_data in data['questions']:
                if 'text' in q_data and q_data['text']:
                    question = Question(
                        job_id=new_job.id,
                        text=q_data['text'],
                        required=q_data.get('required', True)
                    )
                    db.session.add(question)
                    questions_added += 1
            
        db.session.commit()
        logger.info(f"Job created successfully with ID: {new_job.id}, added {questions_added} questions")
        return jsonify(new_job.to_dict()), 201
    
    except Exception as e:
        logger.error("Error creating job", exc_info=True)
        return jsonify({"msg": f"Error creating job: {str(e)}"}), 500

@jobs.route('/<int:job_id>', methods=['PUT'])
def update_job(job_id):
    if not request.is_json:
        logger.warning(f"Job update attempted with non-JSON request for job ID: {job_id}")
        return jsonify({"msg": "Missing JSON in request"}), 400
    
    try:
        job = Job.query.get_or_404(job_id)
        data = request.json
        
        logger.info(f"Updating job with ID: {job_id}")
        
        # Update job fields
        if 'jobTitle' in data:
            job.jobTitle = data['jobTitle']
        if 'department' in data:
            job.department = data['department']
        if 'description' in data:
            job.description = data['description']
        if 'requirements' in data:
            job.requirements = data['requirements']
        if 'aiInstructions' in data:
            job.aiInstructions = data['aiInstructions']
        
        # Update questions if provided
        if 'questions' in data and isinstance(data['questions'], list):
            # Delete existing questions
            Question.query.filter_by(job_id=job_id).delete()
            logger.info(f"Deleted existing questions for job ID: {job_id}")
            
            # Add new questions
            questions_updated = 0
            for q_data in data['questions']:
                if 'text' in q_data and q_data['text']:
                    question = Question(
                        job_id=job_id,
                        text=q_data['text'],
                        required=q_data.get('required', True)
                    )
                    db.session.add(question)
                    questions_updated += 1
            
            logger.info(f"Added {questions_updated} new questions for job ID: {job_id}")
        
        db.session.commit()
        logger.info(f"Job updated successfully with ID: {job_id}")
        return jsonify(job.to_dict()), 200
    
    except Exception as e:
        logger.error(f"Error updating job with ID {job_id}", exc_info=True)
        return jsonify({"msg": f"Error updating job: {str(e)}"}), 500

@jobs.route('/<int:job_id>', methods=['DELETE'])
def delete_job(job_id):
    try:
        job = Job.query.get_or_404(job_id)
        db.session.delete(job)
        db.session.commit()
        logger.info(f"Job deleted successfully with ID: {job_id}")
        return jsonify({"msg": "Job deleted successfully"}), 200
    except Exception as e:
        logger.error(f"Error deleting job with ID {job_id}", exc_info=True)
        return jsonify({"msg": f"Error deleting job: {str(e)}"}), 500 