# bulk_create_comments.py
import json
import os
from pathlib import Path
from dotenv import load_dotenv
import sys
import argparse
from datetime import datetime

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from services.jira_service import JiraService
from utils.file_utils import read_json

# Load environment variables from project root
env_path = project_root / '.env'
load_dotenv(dotenv_path=env_path)

class JiraCommentCreator:
    def __init__(self, verbose=False):
        self.jira_service = JiraService()
        self.verbose = verbose

    def create_comment(self, issue_key, comment_body):
        if self.verbose:
            print(f"\nCreating comment for issue: {issue_key}")
            print(f"Comment body: {comment_body}")

        payload = {
            "body": comment_body
        }
        
        result = self.jira_service.add_comment(issue_key, payload)
        if self.verbose:
            print(f"API Response: {json.dumps(result, indent=2)}")
        return result

    def bulk_create_comments(self, issue_key, comments_data):
        results = []
        if self.verbose:
            print(f"\nStarting bulk creation of {len(comments_data)} comments...")
        
        for i, comment in enumerate(comments_data, 1):
            if self.verbose:
                print(f"\nProcessing comment {i}/{len(comments_data)}")
            result = self.create_comment(issue_key, comment)
            results.append(result)
            print(f"Created comment {i} for issue: {issue_key}")
        
        if self.verbose:
            print(f"\nBulk comment creation completed. Created {len(results)} comments.")
        return results

def generate_security_comments():
    """Generate context-based comments about rate limiting and API security."""
    return [
        {
            "body": f"""
Hey team! 👋 I've been looking into our API security setup, and I think we need to have a discussion about rate limiting. Here's what I found in our current setup:

*Current State (as of {datetime.now().strftime('%Y-%m-%d')}):*
- We're using basic API key authentication
- No rate limiting is in place
- Our API endpoints are potentially vulnerable to abuse

*Why This Matters:*
Without rate limiting, we're at risk of:
- DDoS attacks
- Brute force attempts
- Resource exhaustion
- Unfair usage by some clients

Would love to hear your thoughts on this! Should we prioritize implementing rate limiting first? 🤔
"""
        },
        {
            "body": """
*Quick Tutorial: Rate Limiting Best Practices* 📚

I've been researching rate limiting implementations, and here's a practical guide I put together:

1. *IP-based Rate Limiting*
   ```python
   # Example using Redis
   def check_rate_limit(ip):
       key = f"rate_limit:{ip}"
       current = redis.incr(key)
       if current == 1:
           redis.expire(key, 60)  # 1 minute window
       return current <= 100  # 100 requests per minute
   ```

2. *API Key-based Limits*
   - Different tiers (Free, Pro, Enterprise)
   - Sliding window implementation
   - Burst allowance for spikes

3. *Response Headers*
   ```
   X-RateLimit-Limit: 100
   X-RateLimit-Remaining: 95
   X-RateLimit-Reset: 1625097600
   ```

What do you think about these approaches? I'm particularly interested in your experience with Redis for rate limiting. 🤓
"""
        },
        {
            "body": """
*Security Headers Deep Dive* 🔒

I found this great resource about security headers, and I think we should implement these. Here's a quick guide:

1. *Content Security Policy (CSP)*
   ```nginx
   # Nginx configuration
   add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline';";
   ```

2. *Other Essential Headers*
   ```nginx
   add_header X-Frame-Options "DENY";
   add_header X-Content-Type-Options "nosniff";
   add_header X-XSS-Protection "1; mode=block";
   add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
   ```

I've tested these in our staging environment, and they work great! Anyone want to pair on implementing these in production? 👥
"""
        },
        {
            "body": """
*API Authentication Discussion* 🔑

Hey everyone! I've been thinking about our authentication strategy. Here's what I propose:

1. *JWT Implementation*
   ```python
   # Example JWT token generation
   def generate_token(user_id, role):
       payload = {
           'user_id': user_id,
           'role': role,
           'exp': datetime.utcnow() + timedelta(hours=1)
       }
       return jwt.encode(payload, SECRET_KEY, algorithm='HS256')
   ```

2. *OAuth2 Flow*
   - Authorization Code flow for web apps
   - Client Credentials for service-to-service
   - Refresh token rotation

3. *API Key Management*
   - Key rotation every 90 days
   - Key versioning for zero-downtime rotation
   - Usage tracking and alerts

What's your experience with JWT vs OAuth2? I'm leaning towards JWT for internal services and OAuth2 for third-party access. Thoughts? 💭
"""
        },
        {
            "body": """
*Request Validation Tips & Tricks* 🛠️

I've been working on request validation, and here are some patterns I've found useful:

1. *Schema Validation*
   ```python
   # Using Pydantic for request validation
   from pydantic import BaseModel, Field
   
   class UserRequest(BaseModel):
       username: str = Field(..., min_length=3, max_length=50)
       email: str = Field(..., regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
       age: int = Field(..., gt=0, lt=120)
   ```

2. *Common Validation Rules*
   - Input sanitization
   - Type checking
   - Range validation
   - Pattern matching

3. *Error Handling*
   ```python
   try:
       validated_data = UserRequest(**request.json)
   except ValidationError as e:
       return {"error": "Invalid input", "details": e.errors()}
   ```

Anyone want to share their validation patterns? I'm always looking to improve our approach! 🚀
"""
        },
        {
            "body": """
*Monitoring & Alerting Discussion* 📊

I've been playing with our monitoring setup, and here's what I think we need:

1. *Key Metrics to Track*
   ```prometheus
   # Rate limit violations
   rate_limit_violations_total{endpoint="/api/v1/users", type="ip"}
   
   # Authentication failures
   auth_failures_total{reason="invalid_token"}
   
   # API latency
   http_request_duration_seconds{endpoint="/api/v1/users", method="GET"}
   ```

2. *Alerting Rules*
   ```yaml
   groups:
   - name: api_security
     rules:
     - alert: HighRateLimitViolations
       expr: rate(rate_limit_violations_total[5m]) > 10
       for: 5m
   ```

3. *Dashboard Ideas*
   - Real-time API usage
   - Security incident tracking
   - Performance metrics

I've set up a Grafana dashboard with these metrics. Want to take a look and suggest improvements? 🎯

P.S. The Prometheus + Grafana combo is working really well for us! Highly recommend it. 👍
"""
        }
    ]

def main():
    try:
        # Set up argument parser
        parser = argparse.ArgumentParser(description='Bulk create Jira comments')
        parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
        parser.add_argument('issue_key', help='Jira issue key to add comments to')
        args = parser.parse_args()
        
        # Generate comments
        comments_data = generate_security_comments()
        
        # Create and execute bulk comment creation
        comment_creator = JiraCommentCreator(verbose=args.verbose)
        results = comment_creator.bulk_create_comments(args.issue_key, comments_data)
        
        # Save results to a file
        output_path = project_root / 'jira' / 'comment_results.json'
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
            
        print(f"\nResults saved to: {output_path}")
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 