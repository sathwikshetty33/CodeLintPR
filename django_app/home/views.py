import http
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import IsAuthenticated
from celery.result import AsyncResult
from django.contrib.auth import authenticate, user_logged_in
from django.core.serializers import serialize
from .serializer import *
from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from .serializer import loginSearializer
from .tasks import analyizer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_task(request):
    data = request.data
    repo_url = data.get('repo_url')
    pr_num = data.get('pr_num')
    github_token = data.get('github_token')
    task = analyizer.delay(repo_url, pr_num, github_token)
    return Response({"task_id": task.id,
                     "status" : "Task Started",

              })
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def status_task(request,task_id):
    result = AsyncResult(task_id)
    return Response({"task_id": task_id,
                     "status" : result.state,
                     "Result": result.result
                     })


from rest_framework.views import APIView
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework import status


@method_decorator(csrf_exempt, name='dispatch')
class LoginAPI(APIView):
    authentication_classes = []  # Explicitly allow unauthenticated access
    permission_classes = []  # No permission checks for login

    def post(self, request):
        try:
            # Print debugging information
            print('Login request received')

            # Use request.data directly for DRF
            username = request.data.get('username')
            password = request.data.get('password')

            # Validate input
            if not username or not password:
                return Response({
                    "error": "Username and password are required"
                }, status=status.HTTP_400_BAD_REQUEST)

            # Authenticate user
            user = authenticate(username=username, password=password)

            if user is None:
                print(f"Authentication failed for user: {username}")
                return Response({
                    "error": "Invalid username or password"
                }, status=status.HTTP_401_UNAUTHORIZED)

            # Create or get existing token
            token, created = Token.objects.get_or_create(user=user)

            print(f"Login successful for user: {username}")
            return Response({
                "token": token.key,
                "user_id": user.id,
                "username": user.username
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Exception in login API: {str(e)}")
            return Response({
                "error": f"Server error: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class registerapi(APIView):
    def post(self, request):
        data = request.data
        serializer = loginSearializer(data=data)
        if not serializer.is_valid():
            return Response({"some error": serializer.errors})

        if User.objects.filter(username=serializer.data['username']).exists():
            return Response({
                "error" : "username already exsists"
            })
            # Create new user
        try:
            user = User.objects.create_user(  # Use create_user instead of create
                username=serializer.data['username'],
                password=serializer.data['password']
            )
            return Response({
                "status": "success"
            })
        except Exception as e:
            return Response({
                "error": "Failed to create user"
            })


import json
import logging
from django.conf import settings
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime

logger = logging.getLogger(__name__)


def send_email_notification(to_email, subject, html_content, text_content=None):
    """
    Send email using Django's built-in email service
    """
    try:
        # Use Django's EmailMultiAlternatives for HTML emails
        if text_content is None:
            text_content = strip_tags(html_content)

        # Create the email
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[to_email]
        )

        # Attach HTML content
        email.attach_alternative(html_content, "text/html")

        # Send the email
        email.send()

        logger.info(f"Email sent successfully to {to_email}")
        return True

    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}")
        return False


def format_analysis_results(analysis_result, repo_url, pr_num):
    """
    Format the analysis results into a nice HTML email
    Enhanced to handle complex analysis structure
    """
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                margin: 0;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            .container {{
                max-width: 800px;
                margin: 0 auto;
                background-color: white;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                overflow: hidden;
            }}
            .header {{ 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }}
            .header h2 {{
                margin: 0;
                font-size: 24px;
                font-weight: 600;
            }}
            .repo-info {{ 
                background-color: #f8f9fa;
                padding: 20px;
                border-left: 4px solid #007bff;
                margin: 0;
            }}
            .repo-info h3 {{
                color: #333;
                margin-top: 0;
                font-size: 18px;
            }}
            .repo-info p {{
                margin: 8px 0;
                color: #666;
            }}
            .results {{ 
                padding: 20px;
            }}
            .results h3 {{
                color: #333;
                border-bottom: 2px solid #eee;
                padding-bottom: 10px;
                margin-bottom: 20px;
            }}
            .analysis-summary {{
                background-color: #e3f2fd;
                border: 1px solid #2196f3;
                padding: 15px;
                border-radius: 6px;
                margin-bottom: 20px;
                font-weight: 600;
                color: #1976d2;
            }}
            .file-section {{
                margin-bottom: 30px;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                overflow: hidden;
            }}
            .file-header {{
                background-color: #37474f;
                color: white;
                padding: 12px 16px;
                margin: 0;
                font-size: 16px;
                font-weight: 600;
            }}
            .issues-count {{
                background-color: #fff3e0;
                padding: 8px 16px;
                font-size: 14px;
                color: #ef6c00;
                font-weight: 500;
            }}
            .issue-type-section {{
                margin: 15px;
            }}
            .issue-type-header {{
                color: #424242;
                font-size: 16px;
                margin: 15px 0 10px 0;
                padding: 8px 0;
                border-bottom: 1px solid #eee;
            }}
            .issue-item {{
                margin: 10px 0;
                padding: 15px;
                border-radius: 6px;
                border-left: 4px solid #ccc;
            }}
            .security-issue {{
                background-color: #ffebee;
                border-left-color: #f44336;
            }}
            .best-practice-issue {{
                background-color: #f3e5f5;
                border-left-color: #9c27b0;
            }}
            .style-issue {{
                background-color: #e8f5e8;
                border-left-color: #4caf50;
            }}
            .performance-issue {{
                background-color: #fff8e1;
                border-left-color: #ff9800;
            }}
            .bug-issue {{
                background-color: #fce4ec;
                border-left-color: #e91e63;
            }}
            .unknown-issue {{
                background-color: #f5f5f5;
                border-left-color: #757575;
            }}
            .issue-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 8px;
            }}
            .issue-number {{
                background-color: #666;
                color: white;
                padding: 2px 8px;
                border-radius: 12px;
                font-size: 12px;
                font-weight: 600;
            }}
            .issue-line {{
                background-color: #e0e0e0;
                padding: 2px 8px;
                border-radius: 12px;
                font-size: 12px;
                color: #424242;
                font-weight: 500;
            }}
            .issue-description {{
                margin: 8px 0;
                color: #333;
                line-height: 1.5;
            }}
            .issue-suggestion {{
                margin: 8px 0;
                color: #555;
                background-color: rgba(255,255,255,0.7);
                padding: 8px;
                border-radius: 4px;
                font-style: italic;
                line-height: 1.4;
            }}
            .no-bugs {{ 
                background-color: #e8f5e8;
                border: 1px solid #4caf50;
                color: #2e7d32;
                padding: 20px;
                border-radius: 6px;
                text-align: center;
                font-size: 18px;
                font-weight: 600;
            }}
            .analysis-info {{
                background-color: #e3f2fd;
                border: 1px solid #2196f3;
                color: #1976d2;
                padding: 15px;
                border-radius: 6px;
                margin: 10px 0;
            }}
            .footer {{ 
                background-color: #f8f9fa;
                padding: 20px;
                text-align: center;
                font-size: 12px;
                color: #666;
                border-top: 1px solid #eee;
            }}
            .footer p {{
                margin: 0;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>🔍 PR Security Analysis Report</h2>
            </div>

            <div class="repo-info">
                <h3>📋 Repository Information</h3>
                <p><strong>Repository:</strong> {repo_url}</p>
                <p><strong>Pull Request:</strong> #{pr_num}</p>
                <p><strong>Analysis Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
            </div>

            <div class="results">
                <h3>📊 Analysis Results</h3>
                {format_result_content(analysis_result)}
            </div>

            <div class="footer">
                <p>This report was automatically generated by the PR Security Analysis System.</p>
                <p>For questions or issues, please contact your development team.</p>
            </div>
        </div>
    </body>
    </html>
    """

    # Generate text version
    text_template = f"""
    PR SECURITY ANALYSIS REPORT
    ==========================

    Repository: {repo_url}
    Pull Request: #{pr_num}
    Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}

    ANALYSIS RESULTS:
    {format_result_content_text(analysis_result)}

    ---
    This report was automatically generated by the PR Security Analysis System.
    """

    return html_template, text_template


def format_result_content(result):
    """
    Format the analysis result content for HTML email
    Enhanced to handle the complex nested structure from the analysis
    """
    if not result:
        return '<div class="no-bugs">✅ No issues found in this PR!</div>'

    # Handle the complex nested structure from your analysis
    if isinstance(result, dict):
        # Check if it's the outer structure with task_id and results
        if 'results' in result and isinstance(result['results'], list):
            return format_analysis_files(result['results'])

        # Handle simple dict with issues
        elif 'issues' in result:
            return format_issues_html(result['issues'])

        # Handle other dict formats
        elif result.get('bugs') or result.get('issues'):
            bugs = result.get('bugs', []) + result.get('issues', [])
            if bugs:
                return format_issues_html(bugs)
            else:
                return '<div class="no-bugs">✅ No issues found in this PR!</div>'
        else:
            return f'<div class="analysis-summary">📊 Analysis completed with custom result format</div>'

    # Handle list of issues directly
    elif isinstance(result, list):
        if result:
            return format_issues_html(result)
        else:
            return '<div class="no-bugs">✅ No issues found in this PR!</div>'

    # Handle string result
    elif isinstance(result, str):
        return f'<div class="analysis-info">ℹ️ {result}</div>'

    return '<div class="analysis-info">ℹ️ Analysis completed</div>'


def format_analysis_files(results_list):
    """
    Format the analysis results for multiple files
    """
    if not results_list:
        return '<div class="no-bugs">✅ No issues found in this PR!</div>'

    html_content = ""
    total_issues = 0

    for file_result in results_list:
        if 'filename' in file_result and 'results' in file_result:
            filename = file_result['filename']
            file_issues = file_result['results'].get('issues', [])

            if file_issues:
                total_issues += len(file_issues)
                html_content += f'''
                <div class="file-section">
                    <h4 class="file-header">📁 {filename}</h4>
                    <div class="issues-count">Found {len(file_issues)} issue(s)</div>
                    {format_issues_html(file_issues)}
                </div>
                '''

    if total_issues == 0:
        return '<div class="no-bugs">✅ No issues found in this PR!</div>'

    summary = f'<div class="analysis-summary">🔍 <strong>Total Issues Found:</strong> {total_issues} across {len(results_list)} file(s)</div>'

    return summary + html_content


def format_issues_html(issues):
    """
    Format individual issues for HTML display
    """
    if not issues:
        return '<div class="no-bugs">✅ No issues in this file!</div>'

    # Group issues by type
    issues_by_type = {}
    for issue in issues:
        issue_type = issue.get('type', 'unknown')
        if issue_type not in issues_by_type:
            issues_by_type[issue_type] = []
        issues_by_type[issue_type].append(issue)

    html_content = ""

    # Define icons and colors for different issue types
    type_config = {
        'security': {'icon': '🔒', 'class': 'security-issue', 'label': 'Security Issues'},
        'best_practice': {'icon': '💡', 'class': 'best-practice-issue', 'label': 'Best Practice Issues'},
        'style': {'icon': '🎨', 'class': 'style-issue', 'label': 'Style Issues'},
        'performance': {'icon': '⚡', 'class': 'performance-issue', 'label': 'Performance Issues'},
        'bug': {'icon': '🐛', 'class': 'bug-issue', 'label': 'Bug Issues'},
        'unknown': {'icon': '❓', 'class': 'unknown-issue', 'label': 'Other Issues'}
    }

    for issue_type, type_issues in issues_by_type.items():
        config = type_config.get(issue_type, type_config['unknown'])

        html_content += f'''
        <div class="issue-type-section">
            <h5 class="issue-type-header">{config['icon']} {config['label']} ({len(type_issues)})</h5>
        '''

        for i, issue in enumerate(type_issues, 1):
            line = issue.get('line', 'N/A')
            description = issue.get('description', 'No description provided')
            suggestion = issue.get('suggestion', 'No suggestion provided')

            html_content += f'''
            <div class="issue-item {config['class']}">
                <div class="issue-header">
                    <span class="issue-number">#{i}</span>
                    <span class="issue-line">Line {line}</span>
                </div>
                <div class="issue-description">
                    <strong>Issue:</strong> {description}
                </div>
                <div class="issue-suggestion">
                    <strong>Suggestion:</strong> {suggestion}
                </div>
            </div>
            '''

        html_content += '</div>'

    return html_content


def format_result_content_text(result):
    """
    Format the analysis result content for plain text email
    Enhanced to handle the complex nested structure
    """
    if not result:
        return "✅ No issues found in this PR!"

    # Handle the complex nested structure from your analysis
    if isinstance(result, dict):
        # Check if it's the outer structure with task_id and results
        if 'results' in result and isinstance(result['results'], list):
            return format_analysis_files_text(result['results'])

        # Handle simple dict with issues
        elif 'issues' in result:
            return format_issues_text(result['issues'])

        # Handle other dict formats
        elif result.get('bugs') or result.get('issues'):
            bugs = result.get('bugs', []) + result.get('issues', [])
            if bugs:
                return format_issues_text(bugs)
            else:
                return "✅ No issues found in this PR!"
        else:
            return "📊 Analysis completed with custom result format"

    # Handle list of issues directly
    elif isinstance(result, list):
        if result:
            return format_issues_text(result)
        else:
            return "✅ No issues found in this PR!"

    # Handle string result
    elif isinstance(result, str):
        return f"ℹ️ {result}"

    return "ℹ️ Analysis completed"


def format_analysis_files_text(results_list):
    """
    Format the analysis results for multiple files (text version)
    """
    if not results_list:
        return "✅ No issues found in this PR!"

    text_content = ""
    total_issues = 0

    text_content += f"🔍 TOTAL ISSUES SUMMARY:\n"

    for file_result in results_list:
        if 'filename' in file_result and 'results' in file_result:
            filename = file_result['filename']
            file_issues = file_result['results'].get('issues', [])
            total_issues += len(file_issues)
            text_content += f"   📁 {filename}: {len(file_issues)} issue(s)\n"

    if total_issues == 0:
        return "✅ No issues found in this PR!"

    text_content += f"\nTOTAL: {total_issues} issues across {len(results_list)} file(s)\n\n"
    text_content += "=" * 60 + "\n"

    for file_result in results_list:
        if 'filename' in file_result and 'results' in file_result:
            filename = file_result['filename']
            file_issues = file_result['results'].get('issues', [])

            if file_issues:
                text_content += f"\n📁 FILE: {filename}\n"
                text_content += "-" * 40 + "\n"
                text_content += format_issues_text(file_issues)
                text_content += "\n"

    return text_content


def format_issues_text(issues):
    """
    Format individual issues for text display
    """
    if not issues:
        return "✅ No issues in this file!"

    # Group issues by type
    issues_by_type = {}
    for issue in issues:
        issue_type = issue.get('type', 'unknown')
        if issue_type not in issues_by_type:
            issues_by_type[issue_type] = []
        issues_by_type[issue_type].append(issue)

    text_content = ""

    # Define icons for different issue types
    type_config = {
        'security': {'icon': '🔒', 'label': 'SECURITY ISSUES'},
        'best_practice': {'icon': '💡', 'label': 'BEST PRACTICE ISSUES'},
        'style': {'icon': '🎨', 'label': 'STYLE ISSUES'},
        'performance': {'icon': '⚡', 'label': 'PERFORMANCE ISSUES'},
        'bug': {'icon': '🐛', 'label': 'BUG ISSUES'},
        'unknown': {'icon': '❓', 'label': 'OTHER ISSUES'}
    }

    for issue_type, type_issues in issues_by_type.items():
        config = type_config.get(issue_type, type_config['unknown'])

        text_content += f"\n{config['icon']} {config['label']} ({len(type_issues)}):\n"
        text_content += "-" * (len(config['label']) + 10) + "\n"

        for i, issue in enumerate(type_issues, 1):
            line = issue.get('line', 'N/A')
            description = issue.get('description', 'No description provided')
            suggestion = issue.get('suggestion', 'No suggestion provided')

            text_content += f"\n  #{i} [Line {line}]\n"
            text_content += f"     Issue: {description}\n"
            text_content += f"     Fix: {suggestion}\n"

    return text_content


@api_view(['POST'])
@permission_classes([AllowAny])
def github_actions_analyze_pr(request):
    """
    Endpoint for GitHub Actions to analyze PR and send email notification
    This endpoint runs the analysis and sends results via email using Django's mail service
    """
    try:
        data = request.data

        # Extract required parameters
        repo_url = data.get('repo_url')
        pr_num = data.get('pr_num')
        github_token = data.get('github_token')
        email = data.get('email')

        # Validate required parameters
        if not all([repo_url, pr_num, github_token, email]):
            return Response({
                "error": "Missing required parameters",
                "required": ["repo_url", "pr_num", "github_token", "email"]
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check if API key is configured before starting analysis
        if not settings.GROQ_API_KEY:
            logger.error("OpenAI API key is not configured")
            return Response({
                "status": "error",
                "message": "AI analysis service is not properly configured. Please check API key settings."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        task = analyizer.delay(repo_url, pr_num, github_token)

        try:
            # Wait for the task to complete with timeout
            result = task.get(timeout=300)  # 5 minute timeout

            # Check if the analysis result contains API errors
            if isinstance(result, dict) and 'results' in result:
                for file_result in result['results']:
                    if 'results' in file_result and 'error' in file_result['results']:
                        error_msg = file_result['results'].get('message', 'Unknown API error')

                        # Handle specific API key errors
                        if 'Invalid API Key' in error_msg or 'invalid_api_key' in error_msg:
                            logger.error(f"API Key error during analysis: {error_msg}")
                            return Response({
                                "status": "error",
                                "message": "Analysis failed due to invalid API credentials. Please check your API key configuration.",
                                "error_details": error_msg
                            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                        # Handle other API errors
                        elif 'API_ERROR' in file_result['results'].get('error', ''):
                            logger.error(f"API error during analysis: {error_msg}")
                            return Response({
                                "status": "error",
                                "message": "Analysis failed due to API service error. Please try again later.",
                                "error_details": error_msg
                            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # If analysis completed successfully, format and send email
            subject = f"PR Analysis Results - {repo_url} (PR #{pr_num})"
            html_content, text_content = format_analysis_results(result, repo_url, pr_num)

            # Send email using Django's email service
            email_sent = send_email_notification(email, subject, html_content, text_content)

            if email_sent:
                return Response({
                    "status": "success",
                    "message": "PR analysis completed and email sent successfully",
                    "task_id": task.id,
                    "email_sent_to": email
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "status": "partial_success",
                    "message": "PR analysis completed but email sending failed",
                    "task_id": task.id,
                    "result": result
                }, status=status.HTTP_200_OK)

        except Exception as task_error:
            logger.error(f"Task execution error: {str(task_error)}")
            return Response({
                "status": "error",
                "message": f"Analysis task failed: {str(task_error)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except Exception as e:
        logger.error(f"Error in github_actions_analyze_pr: {str(e)}")
        return Response({
            "status": "error",
            "message": f"Analysis failed: {str(e)}"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#
# # Optional: Async version if you prefer not to wait for task completion
# @api_view(['POST'])
# @permission_classes([AllowAny])
# def github_actions_analyze_pr_async(request):
#     """
#     Async version - starts analysis and sends email when complete
#     Uses Django's email service
#     """
#     try:
#         data = request.data
#
#         # Extract required parameters
#         repo_url = data.get('repo_url')
#         pr_num = data.get('pr_num')
#         github_token = data.get('github_token')
#         email = data.get('email')
#
#         # Validate required parameters
#         if not all([repo_url, pr_num, github_token, email]):
#             return Response({
#                 "error": "Missing required parameters",
#                 "required": ["repo_url", "pr_num", "github_token", "email"]
#             }, status=status.HTTP_400_BAD_REQUEST)
#
#         # Start the analysis task with email callback
#         task = analyizer_with_email.delay(repo_url, pr_num, github_token, email)
#
#         return Response({
#             "status": "started",
#             "message": "PR analysis started. Email will be sent when complete.",
#             "task_id": task.id
#         }, status=status.HTTP_202_ACCEPTED)
#
#     except Exception as e:
#         logger.error(f"Error in github_actions_analyze_pr_async: {str(e)}")
#         return Response({
#             "status": "error",
#             "message": f"Failed to start analysis: {str(e)}"
#         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)