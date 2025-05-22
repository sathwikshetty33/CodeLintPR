# 🔍 CodeLintPR

<div align="center">
  <h3>AI-Powered Automated Code Analysis for GitHub Pull Requests</h3>
  <p>A dual-purpose solution: Interactive Web Interface + Automated GitHub Actions Integration</p>
  
  [![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)](https://hub.docker.com/r/sathwikshetty50/codelintpr)
  [![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-Compatible-green?logo=github-actions)](https://github.com/features/actions)
  [![Django](https://img.shields.io/badge/Django-5.0+-green?logo=django)](https://djangoproject.com/)
  [![Celery](https://img.shields.io/badge/Celery-Async-red?logo=celery)](https://docs.celeryq.dev/)
</div>

---

## ✨ Dual-Mode Features

CodeLintPR offers two powerful ways to analyze your code:

### 🌐 **Web Interface Mode**
- **Interactive Dashboard** - User-friendly web interface for manual PR analysis
- **Real-time Results** - Watch your analysis progress in real-time
- **Detailed Reports** - Comprehensive analysis results with suggestions
- **Manual Control** - Analyze any public GitHub repository on-demand
- **Task Management** - Track and manage multiple analysis tasks

### 🤖 **GitHub Actions Integration Mode**
- **Automated Workflow** - Trigger analysis on every PR automatically
- **CI/CD Integration** - Seamlessly integrate into your development workflow
- **Email Notifications** - Get analysis results delivered to your inbox
- **PR Comments** - Automatic status updates on pull requests
- **Zero Manual Intervention** - Set it up once, analyze forever

### 🔧 **Core Capabilities**
- 🤖 **AI-Powered Analysis** - Leverages Groq API for intelligent code review
- ⚡ **Asynchronous Processing** - Non-blocking analysis using Celery workers
- 🔄 **GitHub Integration** - Seamless PR content fetching via GitHub API
- 📊 **Comprehensive Analysis** - Code style, bugs, performance, and best practices
- 🔒 **Secure Authentication** - Token-based API authentication
- 📧 **Email Notifications** - Get analysis results delivered to your inbox
- 🐳 **Container Ready** - Fully dockerized for easy deployment

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ (for local development)
- Docker (for containerized deployment)
- Redis Server
- GitHub Personal Access Token
- Groq API Key

### Option 1: Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/sathwikshetty33/codeLintPR.git
   cd django_app
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   
   Create a `.env` file in the project root:
   ```env

   GROQ_API_KEY=your_groq_api_key
   
   CELERY_BROKER_URL=redis://localhost:6379/0
   CELERY_RESULT_BACKEND=redis://localhost:6379/0
   ```

5. **Start services**
   ```bash
   # Start Redis
   redis-server
   
   # Run migrations and start Django server
   python manage.py migrate
   python manage.py runserver
   
   # In another terminal, start Celery worker
   celery -A django_app worker --loglevel=info
   ```

### Option 2: Docker Deployment

#### Quick Start with Docker Hub Image


1. **Run CodeLintPR**
   ```bash
   docker run -d --name codelintpr \
     -p 8000:8000 \
     -e GROQ_API_KEY=your_groq_api_key \
     -e CELERY_BROKER_URL=redis://your_redis_container_name:6379/0 \
     -e CELERY_RESULT_BACKEND=redis://your_redis_container_name:6379/0 \
     sathwikshetty50/codelintpr
   ```

## 📖 Usage Documentation

### 🌐 Web Interface Usage

#### Accessing the Web Interface
- **URL**: `http://localhost:8000` (local) or your deployed domain
- **Admin Panel**: `http://localhost:8000/admin`

#### Manual PR Analysis via Web Interface

1. **Navigate to the Dashboard**
   - Open your browser and go to the application URL
   - You'll see the CodeLintPR dashboard

2. **Submit Analysis Request**
   - **Repository URL**: Enter the GitHub repository URL (e.g., `https://github.com/user/repo`)
   - **PR Number**: Enter the pull request number you want to analyze
   - **GitHub Token**: Your personal access token (if not set in environment)

3. **Monitor Progress**
   - Results will be displayed on completion

4. **View Results**
   - Detailed analysis report with:
     - 🐛 Bug detection and suggested fixes
     - 📏 Code style improvements
     - ⚡ Performance optimization suggestions
     - 🛡️ Security best practices
     - 📚 Documentation recommendations

#### Web Interface Endpoints
```
GET  /                          - Main dashboard
POST /analyze-pr/               - Submit PR for analysis
GET  /task-status/<task_id>/    - Check analysis status
GET  /admin/                    - Django admin interface
```

#### Example Web Usage Flow
```bash
# 1. Submit analysis via web form or API
curl -X POST "http://localhost:8000/analyze-pr/" \
  -H "Content-Type: application/json" \
  -d '{
    "repo_url": "https://github.com/user/repo",
    "pr_number": 123,
    "github_token": "your_token",
    "email": "your_email@example.com"
  }'

# Response: {"task_id": "abc123-def456-789"}

# 2. Check status
curl "http://localhost:8000/task-status/abc123-def456-789/"

# Response: {"status": "SUCCESS", "result": {...}}
```

---

### 🤖 GitHub Actions Integration Usage

#### Setting Up Automated PR Analysis

Transform your development workflow by automatically analyzing every pull request!

#### 1. Configure Repository Secrets

Navigate to **Settings > Secrets and variables > Actions** in your GitHub repository:

| Secret Name | Description | Required | Example |
|-------------|-------------|----------|---------|
| `EMAIL_HOST_PASSWORD` | Email app password for notifications | ✅ | `your_gmail_app_password` |
| `EMAIL_HOST_USER` | Email address for sending notifications | ✅ | `your_email@gmail.com` |
| `GITHUBSSS_TOKEN` | GitHub Personal Access Token with repo access | ✅ | `ghp_xxxxxxxxxxxx` |
| `GROQ_API_KEY` | Groq API key for AI analysis | ✅ | `gsk_xxxxxxxxxxxx` |
| `NOTIFICATION_EMAIL` | Email to receive analysis results | ✅ | `team@company.com` |

#### 2. Create Workflow File

Create `.github/workflows/pr-analysis.yml`:

```yaml
name: 🔍 CodeLintPR Analysis

on:
  pull_request:
    types: [opened, synchronize, reopened]

permissions:
  contents: read
  pull-requests: write
  issues: write

jobs:
  analyze-pr:
    runs-on: ubuntu-latest
    name: AI Code Review
    
    steps:
    - name: 🚀 Start Redis Service
      run: |
        echo "Starting Redis..."
        docker run -d --name redis -p 6380:6380 redis:latest redis-server --port 6380
        sleep 10
        
        # Verify Redis connectivity
        for i in {1..10}; do
          if docker exec redis redis-cli -p 6380 ping; then
            echo "✅ Redis is ready!"
            break
          fi
          echo "⏳ Attempt $i: Waiting for Redis..."
          sleep 2
        done

    - name: 🔧 Deploy CodeLint Service
      run: |
        echo "🚀 Starting CodeLint analysis service..."
        docker run -d --name codelint \
          -p 8000:8000 \
          -e CELERY_BROKER_URL=redis://172.17.0.1:6380/0 \
          -e CELERY_RESULT_BACKEND=redis://172.17.0.1:6380/0 \
          -e DEBUG=true \
          -e ALLOWED_HOSTS="*" \
          -e EMAIL_HOST_PASSWORD="${{ secrets.EMAIL_HOST_PASSWORD }}" \
          -e EMAIL_HOST_USER="${{ secrets.EMAIL_HOST_USER }}" \
          -e GROQ_API_KEY="${{ secrets.GROQ_API_KEY }}" \
          --entrypoint="" \
          sathwikshetty50/codelintpr \
          bash -c "
            python manage.py runserver 0.0.0.0:8000 &
            sleep 10 &&
            celery -A django_app worker --loglevel=info -P eventlet &
            wait
          "
        
        echo "⏳ Waiting for services to initialize..."
        sleep 25

    - name: 🔍 Analyze Pull Request
      run: |
        echo "🤖 Starting AI-powered code analysis..."
        curl -X POST "http://localhost:8000/github-actions-analyze-pr/" \
          -H "Content-Type: application/json" \
          -d "{
            \"repo_url\": \"${{ github.repository }}\",
            \"pr_num\": \"${{ github.event.pull_request.number }}\",
            \"github_token\": \"${{ secrets.GITHUBSSS_TOKEN }}\",
            \"email\": \"${{ secrets.NOTIFICATION_EMAIL }}\"
          }" \
          -v

    - name: 💬 Update PR with Analysis Status
      if: always()
      uses: actions/github-script@v6
      with:
        script: |
          const status = '${{ job.status }}' === 'success' ? '✅' : '❌';
          const message = `${status} **CodeLintPR Analysis Complete**
          
          🤖 Your pull request has been analyzed using AI-powered code review.
          📧 Detailed results have been sent to the configured email address.
          
          **Analysis Coverage:**
          - 🐛 Bug detection and fixes
          - 📏 Code style and formatting
          - ⚡ Performance optimizations  
          - 🛡️ Security best practices
          - 📚 Code documentation suggestions
          
          *Analysis powered by Groq AI*`;
          
          await github.rest.issues.createComment({
            issue_number: context.issue.number,
            owner: context.repo.owner,
            repo: context.repo.repo,
            body: message
          });

    - name: 🧹 Cleanup Resources
      if: always()
      run: |
        docker stop redis codelint || true
        docker rm redis codelint || true
```

#### 3. Workflow Behavior

**Automatic Triggers:**
- ✅ New pull requests opened
- ✅ Existing pull requests updated (new commits)
- ✅ Pull requests reopened

**What Happens:**
1. 🚀 GitHub Actions starts the workflow
2. 🔧 CodeLintPR service deploys automatically
3. 🔍 AI analyzes the PR code changes
4. 📧 Results sent via email to configured address
5. 💬 PR gets updated with analysis status comment
6. 🧹 Resources cleaned up automatically

#### 4. Customizing the Integration

**Custom Workflow Triggers:**
```yaml
on:
  pull_request:
    types: [opened, synchronize]
    branches: [main, develop]  # Only analyze PRs to specific branches
  workflow_dispatch:           # Allow manual triggering
```

**Custom Email Templates:**
Modify the email configuration in your environment variables to customize notification format.

**Branch Protection Rules:**
Consider requiring the CodeLintPR analysis to pass before allowing merges:
```yaml
# In branch protection rules
- Required status checks: "AI Code Review"
```

---

## 📋 API Reference

### Web Interface Endpoints

| Endpoint | Method | Description | Parameters |
|----------|--------|-------------|------------|
| `/` | GET | Main dashboard interface | - |
| `/analyze-pr/` | POST | Submit PR for manual analysis | `repo_url`, `pr_number`, `github_token`, `email` |
| `/task-status/<task_id>/` | GET | Check analysis task status | `task_id` (path parameter) |
| `/health/` | GET | Service health check | - |

### GitHub Actions Endpoints

| Endpoint | Method | Description | Parameters |
|----------|--------|-------------|------------|
| `/github-actions-analyze-pr/` | POST | GitHub Actions integration endpoint | `repo_url`, `pr_num`, `github_token`, `email` |

### Response Formats

**Analysis Submission Response:**
```json
{
  "task_id": "abc123-def456-789",
  "status": "PENDING",
  "message": "Analysis started successfully"
}
```

**Task Status Response:**
```json
{
  "task_id": "abc123-def456-789",
  "status": "SUCCESS",
  "result": {
    "bugs_found": 3,
    "style_issues": 5,
    "performance_suggestions": 2,
    "security_recommendations": 1,
    "detailed_analysis": "..."
  }
}
```

---

## 🔧 Configuration

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GITHUB_TOKEN` | ✅ | - | GitHub Personal Access Token |
| `GROQ_API_KEY` | ✅ | - | Groq API key for AI analysis |
| `DJANGO_SECRET_KEY` | ✅ | - | Django secret key |
| `DEBUG` | ❌ | `False` | Enable debug mode |
| `ALLOWED_HOSTS` | ❌ | `*` | Allowed hosts for Django |
| `EMAIL_HOST` | ❌ | `smtp.gmail.com` | SMTP server host |
| `EMAIL_PORT` | ❌ | `587` | SMTP server port |
| `EMAIL_USE_TLS` | ❌ | `True` | Use TLS for email |
| `EMAIL_HOST_USER` | ⚠️ | - | Email username (required for GitHub Actions) |
| `EMAIL_HOST_PASSWORD` | ⚠️ | - | Email password (required for GitHub Actions) |
| `CELERY_BROKER_URL` | ❌ | `redis://localhost:6379/0` | Celery broker URL |
| `CELERY_RESULT_BACKEND` | ❌ | `redis://localhost:6379/0` | Celery result backend |

⚠️ = Required for GitHub Actions integration, optional for web interface

---

## 🛠️ Development & Contributing

### Local Development Setup

1. Fork and clone the repository
2. Set up virtual environment and install dependencies
3. Configure environment variables
4. Run tests: `python manage.py test`
5. Start development server

### Code Style

```bash
# Format code
black .
flake8 .

# Run tests
python manage.py test
```

### Contributing Guidelines

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Write** tests for new functionality
4. **Commit** changes (`git commit -m 'Add amazing feature'`)
5. **Push** to branch (`git push origin feature/amazing-feature`)
6. **Open** a Pull Request

---

## 🔒 Security Best Practices

- 🔐 Store sensitive data in environment variables, never in code
- 🔄 Rotate GitHub tokens and API keys regularly
- 🌐 Use HTTPS in production environments
- 🐳 Keep Docker images updated
- 📧 Use app passwords for Gmail (not your regular password)
- 🔒 Limit GitHub token permissions to minimum required scope

---

## 🐛 Troubleshooting

### Web Interface Issues

**Service not starting:**
- ✅ Check environment variables are set correctly
- ✅ Verify Redis is running: `redis-cli ping`
- ✅ Check Django logs for errors

**Analysis not working:**
- ✅ Verify GitHub token has repository access
- ✅ Check Groq API key is valid
- ✅ Ensure repository is public or token has private repo access

### GitHub Actions Issues

**Workflow failing:**
- ✅ Check all secrets are configured in repository settings
- ✅ Verify secret names match exactly (case-sensitive)
- ✅ Check workflow logs for specific error messages

**Email notifications not working:**
- ✅ Verify SMTP settings are correct
- ✅ For Gmail, use App Password instead of regular password
- ✅ Check spam/junk folder for emails

**Analysis not triggering:**
- ✅ Ensure workflow file is in `.github/workflows/` directory
- ✅ Check workflow triggers match your use case
- ✅ Verify repository has Actions enabled

### Common Error Solutions

```bash
# Check Redis connectivity
redis-cli -h localhost -p 6379 ping

# View container logs
docker logs codelint

# Check Celery worker status
celery -A django_app inspect active
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- 🧠 **Groq** - For providing powerful AI capabilities
- 🐙 **GitHub** - For the comprehensive API and Actions platform
- 🌶️ **Django & Celery** - For the robust backend framework
- 🐳 **Docker** - For containerization excellence
- ⚡ **Redis** - For fast caching and message brokering

---

<div align="center">
  <p>Made with ❤️ for the developer community</p>
  <p>
    <a href="https://github.com/sathwikshetty33/codeLintPR/issues">🐛 Report Bug</a> ·
    <a href="https://github.com/sathwikshetty33/codeLintPR/issues">💡 Request Feature</a> ·
    <a href="https://github.com/sathwikshetty33/codeLintPR">⭐ Star this Project</a>
  </p>
</div>
