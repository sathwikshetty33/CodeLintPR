# CodeLintPR

CodeLintPR is a Django-based microservice that performs automated code analysis on GitHub Pull Requests using AI. The service fetches PR contents via GitHub API and leverages Groq API for intelligent code analysis, providing detailed feedback on code quality, potential issues, and suggestions for improvement.

## Features

- Asynchronous PR analysis using Celery
- Redis caching for improved performance
- GitHub API integration for PR content fetching
- AI-powered code analysis using Groq API
- RESTful API endpoints for task management
- Comprehensive code analysis including style, bugs, performance, and best practices
- Authentication system using DRF's token-based authentication
- Docker containerization for easy deployment

## Prerequisites

- Docker
- Docker Compose
- GitHub Account and Personal Access Token
- Groq API Key

## Docker Deployment

### 1. Clone the Repository

```bash
git clone https://github.com/sathwikshetty33/codeLintPR.git
cd codeLintPR
```

### 2. Environment Configuration

Create a `.env` file in the project root with the following variables:
```
GITHUB_TOKEN=your_github_token
GROQ_API_KEY=your_groq_api_key
DJANGO_SECRET_KEY=your_django_secret_key
DEBUG=False
ALLOWED_HOSTS=*
```

### 3. Build and Run with Docker Compose

```bash
docker-compose up --build
```

### 4. Accessing the Application

- Web Application: `http://localhost:8000`
- Celery Worker: Running in the same container
- Redis: Available at `redis://localhost:6380`

### Docker Compose Configuration

The `docker-compose.yml` file defines two services:

1. **Web Service (`codelintpr_app`)**:
   - Builds the Django application
   - Runs Django development server
   - Starts Celery worker
   - Exposes port 8000

2. **Redis Service (`codelintpr_redis`)**:
   - Uses latest Redis image
   - Runs on port 6380
   - Serves as message broker and result backend for Celery

### Docker Image Management

#### Build the Image
```bash
docker-compose up sathwikshetty50/codelintpr .
```
#### Find Image at sathwikshetty50/codelintpr

### Additional Docker Commands

- Stop containers: `docker-compose down`
- View running containers: `docker ps`
- View logs: `docker-compose logs web`
- Access Django shell: `docker-compose exec web python manage.py shell`


## Troubleshooting

- Ensure all environment variables are set
- Check Docker and Docker Compose versions
- Verify network ports are not in use
- Check container logs for specific errors

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
- Docker
- GitHub API
- Groq API
