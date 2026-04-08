# The NoSQL Database for Audit Logs
resource "aws_dynamodb_table" "astra_logs" {
  name           = "ASTra_Audit_Logs"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "scan_id"

  attribute {
    name = "scan_id"
    type = "S"
  }
}

# The Email Alert System
resource "aws_sns_topic" "astra_alerts" {
  name = "ASTra_Critical_Alerts"
}