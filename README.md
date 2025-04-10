# HR Recruitment System

A recruitment management system with WhatsApp integration for screening candidates.

## Features

- Job posting management (jobs/list api, a job_id get/update/delete apis)
each job application would look something like this
  -d '{
    "jobTitle": "jehfiu",
    "department": "Engineering",
    "description": "3rf",
    "requirements": "wf",
    "aiInstructions": "The AI should be friendly but professional. Ask follow-up questions if candidates don't provide enough detail. Focus on technical skills for this role and project experience.",
    "questions": [
        {
            "text": "What specific experience do you have that's relevant to this role?",
            "required": true
        },
        {
            "text": "Can you share examples of relevant projects you've worked on?",
            "required": true
        },
        {
            "text": "What salary range are you expecting for this position?",
            "required": true
        },
        {
            "text": "frjhg13uyfuhgdwe",
            "required": false
        },
        {
            "text": "",
            "required": false
        }
    ]
}'

- Applicant tracking system (- `GET <job_id>/applications`: List applications for a job, `GET /<application_id>`: Get application details, create application endpoint)
make up the data for the application, each application must have the answers for the questions, a summary, also their convo history with the bot. etc 
- WhatsApp integrated AI chat screening 
- WhatsApp conversation flow for job applications
  - Applicants see a list of available jobs
  - applicant selects a job they want to apply for.
  - llm uses tool to fetch job questions and jd and questions the applicant.
  - when the convo is over it uses tool to submit its results (qusetion's answers, ai summary, ai rating, user number, name, resume file ... etc etc)
  - thse are then visible by the job/applications get apis.



## Testing the API

Once the server is running, you can use these curl commands to test it:

### Create a job

```bash
curl -X POST http://localhost:8000/api/jobs/ \
  -H "Content-Type: application/json" \
  -d '{
    "jobTitle": "jehfiu",
    "department": "Engineering",
    "description": "3rf",
    "requirements": "wf",
    "aiInstructions": "The AI should be friendly but professional. Ask follow-up questions if candidates don't provide enough detail. Focus on technical skills for this role and project experience.",
    "questions": [
        {
            "text": "What specific experience do you have that's relevant to this role?",
            "required": true
        },
        {
            "text": "Can you share examples of relevant projects you've worked on?",
            "required": true
        },
        {
            "text": "What salary range are you expecting for this position?",
            "required": true
        },
        {
            "text": "frjhg13uyfuhgdwe",
            "required": false
        },
        {
            "text": "",
            "required": false
        }
    ]
}'
```

### Create an application (public endpoint)

```bash
curl -X POST http://localhost:8000/api/applications/create \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": 1, 
    "applicant_name": "John Doe", 
    "whatsapp_number": "1234567890", 
    "resume_url": "http://example.com/resume.pdf"
    "ai_summary": "...",
    "questions_answers": [
        {
            "text": "What specific experience do you have that's relevant to this role?",
            "required": true
        },
        {
            "text": "Can you share examples of relevant projects you've worked on?",
            "required": true
        },
        {
            "text": "What salary range are you expecting for this position?",
            "required": true
        },
        {
            "text": "frjhg13uyfuhgdwe",
            "required": false
        },
        {
            "text": "",
            "required": false
        }
    ]
  }'
```

## API Endpoints

Note: All endpoints are now public (no authentication required)

### Jobs

- `GET /api/jobs`: List all jobs
- `GET /api/jobs/<job_id>`: Get job details
- `POST /api/jobs`: Create a new job
- `PUT /api/jobs/<job_id>`: Update a job
- `DELETE /api/jobs/<job_id>`: Delete a job

### Applications

- `GET /api/jobs/<job_id>/applications`: List applications for a job
- `GET /api/applications/<application_id>`: Get application details
- `PUT /api/applications/<application_id>/status`: Update application status
- `POST /api/applications/create`: Create a new application (public endpoint)


### WhatsApp Webhook

- `POST /api/webhook/whatsapp`: Receive WhatsApp messages
- `GET /api/webhook/whatsapp`: Verify the WhatsApp webhook

## Default Admin User

Username: admin  
Password: admin123

Note: Authentication is currently disabled on all endpoints.

## Environment Variables

See `.env` for required environment variables. 