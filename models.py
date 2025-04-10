from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jobTitle = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.Text, nullable=False)
    aiInstructions = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())
    
    # Relationships
    questions = db.relationship('Question', backref='job', lazy=True, cascade="all, delete-orphan")
    applications = db.relationship('Application', backref='job', lazy=True, cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            'id': self.id,
            'jobTitle': self.jobTitle,
            'department': self.department,
            'description': self.description,
            'requirements': self.requirements,
            'aiInstructions': self.aiInstructions,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'questions': [question.to_dict() for question in self.questions]
        }

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    text = db.Column(db.String(255), nullable=False)
    required = db.Column(db.Boolean, default=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'text': self.text,
            'required': self.required
        }

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    applicant_name = db.Column(db.String(100), nullable=False)
    whatsapp_number = db.Column(db.String(20), nullable=False)
    resume_url = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), default='new')  # new, screening, interview, hired, rejected
    applied_at = db.Column(db.DateTime, default=datetime.now())
    ai_summary = db.Column(db.Text, nullable=True)
    
    # Relationships
    answers = db.relationship('Answer', backref='application', lazy=True, cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            'id': self.id,
            'applicant_name': self.applicant_name,
            'whatsapp_number': self.whatsapp_number,
            'resume_url': self.resume_url,
            'status': self.status,
            'ai_summary': self.ai_summary,
            'applied_at': self.applied_at.isoformat(),
            'job_id': self.job_id,
            'answers': [answer.to_dict() for answer in self.answers]
        }

class Answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('application.id'), nullable=False)
    question_text = db.Column(db.String(255), nullable=False)
    answer_text = db.Column(db.Text, nullable=False)
    required = db.Column(db.Boolean, default=True)
    
    def to_dict(self):
        return {
            'question': self.question_text,
            'answer': self.answer_text,
            'required': self.required
        }
