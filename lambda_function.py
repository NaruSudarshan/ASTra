import json
import ast
import urllib.request
import urllib.error
import boto3
import os
import uuid
from datetime import datetime

# Initialize AWS SDK clients
dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')

# Load environment variables
DYNAMODB_TABLE = os.environ.get('DYNAMODB_TABLE', 'ASTra_Audit_Logs')
SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN')

class SecurityScanner(ast.NodeVisitor):
    """Traverses the AST to find hardcoded secrets and dangerous functions."""
    def __init__(self):
        self.issues = []
        self.risk_keywords = ["key", "secret", "token", "password", "auth", "credential"]

    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name):
                var_name = target.id.lower()
                if any(risk in var_name for risk in self.risk_keywords):
                    if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                        self.issues.append(f"Line {node.lineno}: Hardcoded secret in '{target.id}'")
        self.generic_visit(node)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name) and node.func.id in ['eval', 'exec', 'system']:
            self.issues.append(f"Line {node.lineno}: Dangerous RCE function '{node.func.id}' detected")
        self.generic_visit(node)

def fetch_code_from_github(raw_url):
    """Downloads the raw Python file from GitHub without needing external libraries."""
    try:
        req = urllib.request.Request(raw_url)
        with urllib.request.urlopen(req) as response:
            return response.read().decode('utf-8')
    except urllib.error.URLError as e:
        print(f"Failed to fetch code: {e}")
        return None

def lambda_handler(event, context):
    """Main entry point triggered by GitHub Webhook via API Gateway."""
    print("ASTra Engine Triggered.")
    
    # 1. Parse the incoming GitHub Webhook JSON
    try:
        body = json.loads(event.get('body', '{}'))
    except json.JSONDecodeError:
        return {"statusCode": 400, "body": "Invalid JSON payload"}

    # We only care about "push" events with commits
    if 'commits' not in body:
        return {"statusCode": 200, "body": "Not a push event or no commits. Ignored."}

    repository_name = body['repository']['full_name']
    all_issues = []

    # 2. Extract modified Python files from the commits
    for commit in body['commits']:
        commit_id = commit['id']
        for file_path in commit.get('added', []) + commit.get('modified', []):
            if file_path.endswith('.py'):
                
                # Construct the raw GitHub URL for public repos
                raw_url = f"https://raw.githubusercontent.com/{repository_name}/{commit_id}/{file_path}"
                source_code = fetch_code_from_github(raw_url)
                
                if not source_code:
                    continue

                # 3. Parse into AST and Scan
                try:
                    tree = ast.parse(source_code)
                    scanner = SecurityScanner()
                    scanner.visit(tree)
                    
                    if scanner.issues:
                        all_issues.append({
                            "file": file_path,
                            "commit": commit_id,
                            "violations": scanner.issues
                        })
                except SyntaxError:
                    print(f"Syntax Error in {file_path}. Skipping.")

    # 4. Handle Results (Save to DB and Alert)
    if all_issues:
        scan_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        # Write to DynamoDB
        table = dynamodb.Table(DYNAMODB_TABLE)
        table.put_item(Item={
            'scan_id': scan_id,
            'timestamp': timestamp,
            'repository': repository_name,
            'threats': all_issues
        })
        
        # Send Email Alert via SNS
        alert_message = f"ASTra CRITICAL ALERT\n\nRepository: {repository_name}\nThreats Found:\n"
        for issue in all_issues:
            alert_message += f"\nFile: {issue['file']}\n"
            for violation in issue['violations']:
                alert_message += f" - {violation}\n"
                
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject=f"Security Alert: Hardcoded Secrets in {repository_name}",
            Message=alert_message
        )
        
        print(f"Threats detected and logged under Scan ID: {scan_id}")
        return {"statusCode": 200, "body": "Scan complete. Threats detected and reported."}

    print("Scan complete. Code is safe.")
    return {"statusCode": 200, "body": "Scan complete. No threats found."}