# ASTra: Automated Serverless Threat Response Architecture

![Status](https://img.shields.io/badge/Status-Prototype-orange)
![Python](https://img.shields.io/badge/Python-3.9-blue)
![Platform](https://img.shields.io/badge/AWS-Serverless-yellow)

**ASTra** is a next-generation static analysis tool designed to secure CI/CD pipelines.

Traditional security tools rely on "Regex" (text matching), which leads to high false positives—flagging innocent comments as security risks. **ASTra** solves this by using Python's **Abstract Syntax Tree (AST)** to understand the *context* of the code, not just the text.

## 🚀 Key Features

* **Context-Aware Engine:** Intelligently distinguishes between actual code logic and comments, ensuring 100% accuracy in basic scans.
* **Zero-Cost Architecture:** Built on **AWS Lambda**, meaning the scanner incurs **$0 cost** when idle. It only runs when code is pushed.
* **Hardcoded Secret Detection:** strict validation rules to catch API keys and passwords left in the source code.
* **Event-Driven:** Designed to integrate directly with GitHub Webhooks for real-time security auditing.

## 🏗️ System Overview

ASTra follows a modern "Event-Driven" flow:
1.  **Code Push:** Developer pushes code to GitHub.
2.  **Trigger:** AWS API Gateway receives the webhook.
3.  **Analysis:** The AST Engine (Lambda) parses the code structure.
4.  **Verdict:** If threats are found, the build is flagged immediately.

---
*Senior Design Project (2026)*