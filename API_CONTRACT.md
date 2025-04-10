# API Documentation

This document outlines the API endpoints available for the hiring system.

## Base URL

All endpoints are relative to the base URL: `http://localhost:8001`

## Authentication

Currently, the API does not require authentication.

## Jobs API

### Get All Jobs

**Endpoint:** `GET /api/jobs/`

**Response:**
```json
[
  {
    "id": 1,
    "jobTitle": "Software Developer",
    "department": "Engineering",
    "description": "Build cool stuff",
    "requirements": "Python, Flask",
    "aiInstructions": "",
    "created_at": "2023-08-15T10:30:00.000Z",
    "updated_at": "2023-08-15T10:30:00.000Z",
    "questions": [
      {
        "id": 1,
        "text": "Why do you want to work here?",
        "required": true
      }
    ]
  }
]
```

### Get Job by ID

**Endpoint:** `GET /api/jobs/{job_id}`

**Response:**
```json
{
  "id": 1,
  "jobTitle": "Software Developer",
  "department": "Engineering",
  "description": "Build cool stuff",
  "requirements": "Python, Flask",
  "aiInstructions": "",
  "created_at": "2023-08-15T10:30:00.000Z",
  "updated_at": "2023-08-15T10:30:00.000Z",
  "questions": [
    {
      "id": 1,
      "text": "Why do you want to work here?",
      "required": true
    }
  ]
}
```

### Create Job

**Endpoint:** `POST /api/jobs/`

**Request:**
```json
{
  "jobTitle": "Software Developer",
  "department": "Engineering",
  "description": "Build cool stuff",
  "requirements": "Python, Flask",
  "aiInstructions": "Ask about experience with Flask",
  "questions": [
    {
      "text": "Why do you want to work here?",
      "required": true
    }
  ]
}
```

**Response:**
```json
{
  "id": 1,
  "jobTitle": "Software Developer",
  "department": "Engineering",
  "description": "Build cool stuff",
  "requirements": "Python, Flask",
  "aiInstructions": "Ask about experience with Flask",
  "created_at": "2023-08-15T10:30:00.000Z",
  "updated_at": "2023-08-15T10:30:00.000Z",
  "questions": [
    {
      "id": 1,
      "text": "Why do you want to work here?",
      "required": true
    }
  ]
}
```

### Update Job

**Endpoint:** `PUT /api/jobs/{job_id}`

**Request:**
```json
{
  "jobTitle": "Senior Software Developer",
  "questions": [
    {
      "text": "Why do you want to work here?",
      "required": true
    },
    {
      "text": "What is your experience with Flask?",
      "required": true
    }
  ]
}
```

**Response:**
```json
{
  "id": 1,
  "jobTitle": "Senior Software Developer",
  "department": "Engineering",
  "description": "Build cool stuff",
  "requirements": "Python, Flask",
  "aiInstructions": "Ask about experience with Flask",
  "created_at": "2023-08-15T10:30:00.000Z",
  "updated_at": "2023-08-15T11:15:00.000Z",
  "questions": [
    {
      "id": 2,
      "text": "Why do you want to work here?",
      "required": true
    },
    {
      "id": 3,
      "text": "What is your experience with Flask?",
      "required": true
    }
  ]
}
```

### Delete Job

**Endpoint:** `DELETE /api/jobs/{job_id}`

**Response:**
```json
{
  "msg": "Job deleted successfully"
}
```

## Applications API

### Get All Applications

**Endpoint:** `GET /api/applications/`

**Response:**
```json
[
  {
    "id": 1,
    "applicant_name": "John Doe",
    "whatsapp_number": "+1234567890",
    "resume_url": "https://example.com/resume.pdf",
    "status": "new",
    "ai_summary": "",
    "applied_at": "2023-08-15T14:30:00.000Z",
    "job_id": 1,
    "answers": [
      {
        "question": "Why do you want to work here?",
        "answer": "I love the company culture",
        "required": true
      }
    ]
  }
]
```

### Get Applications for Job

**Endpoint:** `GET /api/applications/jobs/{job_id}/applications`

**Response:**
```json
[
  {
    "id": 1,
    "applicant_name": "John Doe",
    "whatsapp_number": "+1234567890",
    "resume_url": "https://example.com/resume.pdf",
    "status": "new",
    "ai_summary": "",
    "applied_at": "2023-08-15T14:30:00.000Z",
    "job_id": 1,
    "answers": [
      {
        "question": "Why do you want to work here?",
        "answer": "I love the company culture",
        "required": true
      }
    ]
  }
]
```

### Get Application by ID

**Endpoint:** `GET /api/applications/{application_id}`

**Response:**
```json
{
  "id": 1,
  "applicant_name": "John Doe",
  "whatsapp_number": "+1234567890",
  "resume_url": "https://example.com/resume.pdf",
  "status": "new",
  "ai_summary": "",
  "applied_at": "2023-08-15T14:30:00.000Z",
  "job_id": 1,
  "answers": [
    {
      "question": "Why do you want to work here?",
      "answer": "I love the company culture",
      "required": true
    }
  ]
}
```

### Update Application Status

**Endpoint:** `PUT /api/applications/{application_id}/status`

**Request:**
```json
{
  "status": "screening"
}
```

**Valid status values:** `new`, `screening`, `interview`, `hired`, `rejected`

**Response:**
```json
{
  "msg": "Status updated successfully"
}
```

### Create Application

**Endpoint:** `POST /api/applications/create`

**Request:**
```json
{
  "job_id": 1,
  "applicant_name": "John Doe",
  "whatsapp_number": "+1234567890",
  "resume_url": "https://example.com/resume.pdf",
  "questions_answers": [
    {
      "text": "Why do you want to work here?",
      "answer": "I love the company culture",
      "required": true
    }
  ]
}
```

**Response:**
```json
{
  "msg": "Application submitted successfully",
  "application_id": 1
}
```
