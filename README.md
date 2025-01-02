# CodeLintPR

CodeLintPR is a Django-based microservice that performs automated code analysis on GitHub Pull Requests using AI. The service fetches PR contents via GitHub API and leverages Groq API for intelligent code analysis, providing detailed feedback on code quality, potential issues, and suggestions for improvement.

## Features

- Asynchronous PR analysis using Celery
- Redis caching for improved performance
- GitHub API integration for PR content fetching
- AI-powered code analysis using Groq API
- RESTful API endpoints for task management
- Comprehensive code analysis including style, bugs, performance, and best practices

## Prerequisites

- Python 3.8+
- Redis Server
- Django 4.x
- Celery
- GitHub Account and Personal Access Token
- Groq API Key

## Installation

1. Clone the repository:
```bash
git clone https://github.com/sathwikshetty33/codeLintPR.git
cd django_app
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```


4. Start Redis server:
```bash
redis-server --port 6380
```

5. Start Celery worker:
```bash
celery -A django_app worker --loglevel=info -P eventlet
```

6. Run Django development server:
```bash
python manage.py runserver
```

## API Endpoints

### 1. Start Analysis Task

**Endpoint:** `POST http://127.0.0.1:8000/start-task/`

**Request Body:**
```json
{
    "repo_url": "https://github.com/username/repo",
    "pr_num": 123,
    "github_token": "your_github_token"
}
```

**Response:**
```json
{
    "task_id": "beafd941-5513-42d9-a13c-46983f97ff24",
    "status": "Task Started"
}
```

### 2. Check Task Status

**Endpoint:** `GET http://127.0.0.1:8000/task-status/<task_id>/`

**Response:**
```json
{
    "task_id": "beafd941-5513-42d9-a13c-46983f97ff24",
    "status": "SUCCESS",
    "Result": {
        "task_id": "b3b33e40-795c-4806-bcb4-9d8230949b1c",
        "results": [
            {
                "results": {
                    "issues": [
                        {
                            "type": "style",
                            "line": "1",
                            "description": "Issue description",
                            "suggestion": "Suggested fix"
                        }
                    ]
                },
                "filename": "path/to/file"
            }
        ]
    }
}
```



## Issue Types

The service identifies and reports various types of issues:
- Style: Code formatting and style conventions
- Bugs: Potential bugs and logic errors
- Performance: Performance optimization suggestions
- Best Practices: Coding best practices and standards

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue in the GitHub repository or contact the maintainers.

## Acknowledgments

- Django Rest Framework
- Celery
- Redis
- GitHub API
- Groq API

