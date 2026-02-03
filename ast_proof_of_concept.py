import ast

# --- STEP 1: DEFINE TARGET CODE ---
# Simulating a file content that has a hardcoded secret
code_payload = """
def connect_to_aws():
    # This is a dangerous hardcoded credential
    aws_access_key = "AKIA_1234567890_SECRET"
    timeout = 30
    return True
"""

print("=========================================")
print("   SERVERLESS SECURITY SCANNER v1.0      ")
print("=========================================")
print(f"[*] Loading file content ({len(code_payload)} bytes)...")

# --- STEP 2: PARSE INTO AST ---
# transforming raw text into a Tree structure the computer understands
try:
    tree = ast.parse(code_payload)
    print("[*] AST Parsing successful. Analyzing Nodes...")
except SyntaxError:
    print("[!] Syntax Error: Could not parse file.")

# --- STEP 3: TRAVERSE THE TREE ---
# Walking through every node (function, assignment, import, etc.)
issues_found = 0

for node in ast.walk(tree):
    
    # We only care about ASSIGNMENTS (e.g., x = y)
    if isinstance(node, ast.Assign):
        
        # Check all targets (variables being assigned to)
        for target in node.targets:
            if isinstance(target, ast.Name):
                variable_name = target.id.lower()
                
                # --- STEP 4: APPLY SECURITY RULES ---
                # Rule: Flag variables containing 'key', 'secret', or 'token'
                if any(risk in variable_name for risk in ["key", "secret", "token"]):
                    print("\n[!!!] CRITICAL SECURITY ALERT FOUND")
                    print(f" > Risk Type:    Hardcoded Secret")
                    print(f" > Variable:     '{target.id}'")
                    print(f" > Line Number:  {node.lineno}")
                    print(f" > Logic Check:  Variable name implies sensitive data")
                    issues_found += 1

print("=========================================")
print(f"SCAN COMPLETE. Total Threats Detected: {issues_found}")
print("=========================================")