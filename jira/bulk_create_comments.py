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

        result = self.jira_service.add_comment(issue_key, comment_body)
        if self.verbose:
            print(f"API Response: {json.dumps(result, indent=2)}")
        return result

    def bulk_create_comments(self, issue_key, comments_data):
        results = []
        success_count = 0
        failure_count = 0
        errors = []

        if self.verbose:
            print(f"\nStarting bulk creation of {len(comments_data)} comments...")
        
        for i, comment in enumerate(comments_data, 1):
            if self.verbose:
                print(f"\nProcessing comment {i}/{len(comments_data)}")
            try:
                result = self.create_comment(issue_key, comment)
                if result and 'id' in result:
                    success_count += 1
                    results.append(result)
                else:
                    failure_count += 1
                    errors.append(f"Comment {i}: Failed to create. Error: {result}")
            except Exception as e:
                failure_count += 1
                errors.append(f"Comment {i}: {str(e)}")
                if self.verbose:
                    print(f"Error creating comment {i}: {str(e)}")
            
        if self.verbose:
            print(f"\nBulk comment creation completed:")
            print(f"- Successfully created: {success_count} comments")
            print(f"- Failed to create: {failure_count} comments")
            if errors:
                print("\nErrors encountered:")
                for error in errors:
                    print(f"- {error}")

        return {
            "results": results,
            "summary": {
                "total": len(comments_data),
                "success": success_count,
                "failure": failure_count,
                "errors": errors
            }
        }

def generate_security_comments():
    return [
        {
            "body": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "Hey team! 👋 I've been looking into our API security setup, and I think we need to have a discussion about rate limiting. Here's what I found in our current setup:"
                            }
                        ]
                    },
                    {
                        "type": "bulletList",
                        "content": [
                            {
                                "type": "listItem",
                                "content": [
                                    {
                                        "type": "paragraph",
                                        "content": [
                                            {
                                                "type": "text",
                                                "text": "We're using basic API key authentication"
                                            }
                                        ]
                                    }
                                ]
                            },
                            {
                                "type": "listItem",
                                "content": [
                                    {
                                        "type": "paragraph",
                                        "content": [
                                            {
                                                "type": "text",
                                                "text": "No rate limiting is in place"
                                            }
                                        ]
                                    }
                                ]
                            },
                            {
                                "type": "listItem",
                                "content": [
                                    {
                                        "type": "paragraph",
                                        "content": [
                                            {
                                                "type": "text",
                                                "text": "Our API endpoints are potentially vulnerable to abuse"
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "Why This Matters:",
                                "marks": [
                                    {
                                        "type": "strong"
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "type": "bulletList",
                        "content": [
                            {
                                "type": "listItem",
                                "content": [
                                    {
                                        "type": "paragraph",
                                        "content": [
                                            {
                                                "type": "text",
                                                "text": "DDoS attacks"
                                            }
                                        ]
                                    }
                                ]
                            },
                            {
                                "type": "listItem",
                                "content": [
                                    {
                                        "type": "paragraph",
                                        "content": [
                                            {
                                                "type": "text",
                                                "text": "Brute force attempts"
                                            }
                                        ]
                                    }
                                ]
                            },
                            {
                                "type": "listItem",
                                "content": [
                                    {
                                        "type": "paragraph",
                                        "content": [
                                            {
                                                "type": "text",
                                                "text": "Resource exhaustion"
                                            }
                                        ]
                                    }
                                ]
                            },
                            {
                                "type": "listItem",
                                "content": [
                                    {
                                        "type": "paragraph",
                                        "content": [
                                            {
                                                "type": "text",
                                                "text": "Unfair usage by some clients"
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": "Would love to hear your thoughts on this! Should we prioritize implementing rate limiting first? 🤔"
                            }
                        ]
                    }
                ]
            }
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
        output_path = project_root / 'jira' / "data" / 'comment_results.json'
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
            
        print(f"\nResults saved to: {output_path}")
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()