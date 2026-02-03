import ast

# --- CONFIGURATION ---
# Mock payload: Simulating a file with a hardcoded AWS key for testing detection logic
code_payload = """
def connect_to_aws():
    # TODO: This credential needs to be moved to Environment Variables
    aws_access_key = "AKIA_1234567890_SECRET"
    timeout = 30
    return True
"""

print("=========================================")
print("   ASTRA SECURITY ENGINE v1.0 (PoC)      ")
print("=========================================")
print(f"[*] Loading target buffer ({len(code_payload)} bytes)...")

# --- PARSING PHASE ---
# Convert source code into Abstract Syntax Tree to analyze structure
try:
    tree = ast.parse(code_payload)
    print("[*] AST Parsing successful. Starting traversal...")
except SyntaxError:
    print("[!] Fatal: Syntax Error. Cannot parse invalid Python code.")

# --- ANALYSIS PHASE ---
issues_found = 0

# Walk through every node in the code tree
for node in ast.walk(tree):
    
    # Filter: We only analyze Assignment nodes (x = y) to ignore comments/docstrings
    if isinstance(node, ast.Assign):
        
        for target in node.targets:
            if isinstance(target, ast.Name):
                variable_name = target.id.lower()
                
                # Heuristic: Check if variable name suggests sensitive data
                # If name contains 'key', 'secret', etc., we inspect the value.
                if any(risk in variable_name for risk in ["key", "secret", "token"]):
                    
                    print("\n[!!!] CRITICAL SECURITY ALERT FOUND")
                    print(f" > Risk Type:    Hardcoded Secret")
                    print(f" > Variable:     '{target.id}'")
                    print(f" > Line Number:  {node.lineno}")
                    print(f" > Reason:       Variable name implies sensitive data")
                    issues_found += 1

print("=========================================")
print(f"SCAN COMPLETE. Total Threats Detected: {issues_found}")
print("=========================================")