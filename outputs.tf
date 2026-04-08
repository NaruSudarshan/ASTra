output "github_webhook_url" {
  value       = "${aws_api_gateway_deployment.api_deployment.invoke_url}/webhook"
  description = "Paste this URL into your GitHub Webhook settings"
}