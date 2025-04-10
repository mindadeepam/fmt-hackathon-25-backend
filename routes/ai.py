from flask import Blueprint, request, jsonify
from models import db, Application, Job, Conversation, AIAnalysis, Skill
from services.ai_service import analyze_with_ai
from logger import logger

ai = Blueprint('ai', __name__)

@ai.route('/analyze-application', methods=['POST'])
def analyze_application():
    if not request.is_json:
        logger.warning("Analyze application attempted with non-JSON request")
        return jsonify({"msg": "Missing JSON in request"}), 400
    
    data = request.json
    
    if 'application_id' not in data:
        logger.warning("Analyze application attempted without application_id")
        return jsonify({"msg": "Missing application_id field"}), 400
    
    application_id = data['application_id']
    logger.info(f"Analyzing application ID: {application_id}")
    
    try:
        application = Application.query.get_or_404(application_id)
        
        # Get all conversation data
        conversations = Conversation.query.filter_by(application_id=application_id).order_by(Conversation.timestamp).all()
        logger.info(f"Retrieved {len(conversations)} conversation messages for analysis")
        
        conversation_text = "\n".join([f"{'Bot' if c.is_from_bot else 'Applicant'}: {c.message}" for c in conversations])
        
        # Extract job requirements
        job = Job.query.get(application.job_id)
        job_requirements = job.requirements
        
        # Call AI service to analyze the application
        logger.info(f"Calling AI service to analyze application {application_id}")
        analysis_result = analyze_with_ai(application, job_requirements, conversation_text)
        logger.info(f"Received AI analysis with match score: {analysis_result['match_score']}")
        
        # Save or update the analysis
        existing_analysis = AIAnalysis.query.filter_by(application_id=application_id).first()
        
        if existing_analysis:
            logger.info(f"Updating existing analysis for application {application_id}")
            existing_analysis.analysis_text = analysis_result['analysis']
            existing_analysis.key_strengths = analysis_result['key_strengths']
        else:
            logger.info(f"Creating new analysis for application {application_id}")
            new_analysis = AIAnalysis(
                application_id=application_id,
                analysis_text=analysis_result['analysis'],
                key_strengths=analysis_result['key_strengths']
            )
            db.session.add(new_analysis)
        
        # Update match score
        application.match_score = analysis_result['match_score']
        
        # Extract and save skills
        skill_count = 0
        for skill_name in analysis_result['skills']:
            skill = Skill.query.filter_by(name=skill_name).first()
            if not skill:
                logger.info(f"Creating new skill: {skill_name}")
                skill = Skill(name=skill_name)
                db.session.add(skill)
                db.session.flush()
            
            if skill not in application.skills:
                application.skills.append(skill)
                skill_count += 1
        
        logger.info(f"Added {skill_count} skills to application {application_id}")
        
        db.session.commit()
        logger.info(f"Successfully saved analysis for application {application_id}")
        
        return jsonify({
            'analysis': analysis_result['analysis'],
            'key_strengths': analysis_result['key_strengths'],
            'match_score': analysis_result['match_score'],
            'skills': analysis_result['skills']
        }), 200
        
    except Exception as e:
        logger.error(f"Error analyzing application {application_id}", exc_info=True)
        return jsonify({"msg": f"Error analyzing application: {str(e)}"}), 500 