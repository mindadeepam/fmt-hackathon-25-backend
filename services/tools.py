import json
from typing import Optional, List
from models import db, Job, Question, Application, Answer
from datetime import datetime
from logger import logger

def get_available_jobs() -> str:
    """
    Get a list of all available jobs.
    
    Returns:
        str: JSON string with all available jobs
    """
    try:
        jobs = Job.query.all()
        logger.info(f"Retrieved {len(jobs)} available jobs")
        return json.dumps([job.to_dict() for job in jobs])
    except Exception as e:
        logger.error("Error retrieving available jobs", exc_info=True)
        return json.dumps({"error": "Failed to retrieve jobs"})

def get_job_details(job_id: int) -> str:
    """
    Get detailed information about a specific job.
    
    Args:
        job_id: int: The ID of the job to retrieve
        
    Returns:
        str: Detailed information about the job
    """
    try:
        job = Job.query.get(job_id)
        if not job:
            logger.warning(f"Job not found with ID: {job_id}")
            return "Job not found."
        
        logger.info(f"Retrieved details for job ID: {job_id}")
        return json.dumps(job.to_dict())
    except Exception as e:
        logger.error(f"Error retrieving job details for job ID {job_id}", exc_info=True)
        return json.dumps({"error": "Failed to retrieve job details"})

def get_job_questions(job_id: int) -> str:
    """
    Get all screening questions for a specific job.
    
    Args:
        job_id: int: The ID of the job
        
    Returns:
        str: JSON string with all questions for the job
    """
    try:
        questions = Question.query.filter_by(job_id=job_id).all()
        if not questions:
            logger.info(f"No questions found for job ID: {job_id}")
            return "No questions found for this job."
        
        logger.info(f"Retrieved {len(questions)} questions for job ID: {job_id}")
        return json.dumps([question.to_dict() for question in questions])
    except Exception as e:
        logger.error(f"Error retrieving questions for job ID {job_id}", exc_info=True)
        return json.dumps({"error": "Failed to retrieve job questions"})

def submit_application(
    job_id: int, 
    applicant_name: str, 
    whatsapp_number: str, 
    answers: Optional[List[dict]] = None,
    resume_url: Optional[str] = None,
    ai_summary: Optional[str] = None
) -> str:
    """
    Submit a new application for a job.
    
    Args:
        job_id: int: The ID of the job to apply for
        applicant_name: str: The name of the applicant
        whatsapp_number: str: The WhatsApp number of the applicant
        answers: List[dict]: Optional list of question answers
        resume_url: str: Optional URL to the resume
        ai_summary: str: Optional AI summary of the application
        
    Returns:
        str: JSON with the application ID and confirmation message
    """
    try:
        # Check if job exists
        job = Job.query.get(job_id)
        if not job:
            logger.warning(f"Cannot submit application - job not found with ID: {job_id}")
            return json.dumps({"success": False, "message": "Job not found."})
        
        # Create new application
        application = Application(
            job_id=job_id,
            applicant_name=applicant_name,
            whatsapp_number=whatsapp_number,
            resume_url=resume_url,
            ai_summary=ai_summary,
            status="new"
        )
        
        db.session.add(application)
        db.session.commit()
        
        # Add answers if provided
        if answers and isinstance(answers, list):
            for answer_data in answers:
                if 'question' in answer_data and 'answer' in answer_data:
                    answer = Answer(
                        application_id=application.id,
                        question_text=answer_data['question'],
                        answer_text=answer_data['answer'],
                        required=answer_data.get('required', True)
                    )
                    db.session.add(answer)
            
            db.session.commit()
            logger.info(f"Added {len(answers)} answers to application {application.id}")
        
        logger.info(f"Application submitted: ID={application.id}, Name={applicant_name}, Job ID={job_id}")
        
        return json.dumps({
            "success": True, 
            "message": "Application submitted successfully.",
            "application_id": application.id
        })
    except Exception as e:
        logger.error(f"Error submitting application for job ID {job_id}", exc_info=True)
        return json.dumps({"success": False, "message": f"Error submitting application: {str(e)}"})
