# 6. Security and Authentication

Security has been implemented at multiple levels.

## Authentication (Identity Provider)
Access to the application is protected by **Amazon Cognito**.
* **OAuth2 / OpenID Connect:** The Chainlit frontend delegates authentication to Cognito.
* **User Pool:** Manages user identities.
* **Callback Whitelisting:** Cognito is configured to accept redirects only to authorized HTTPS domains (`am-cloudnlpchatbot.site`).

## Encryption in Transit
All public traffic is encrypted.
* **SSL/TLS Certificate:** Generated via AWS Certificate Manager (ACM) with automatic DNS validation on Route53.
* **HTTPS Redirect:** The application forces the use of HTTPS.

## Data Segregation
* **DynamoDB:** Chat history is partitioned by `session_id` (corresponding to the user's email). This ensures no user can read another's conversations.
* **VPC Isolation:** Although containers reside in public subnets (to save on NAT Gateway costs), they are protected by Security Groups that block any connection not originating from the Load Balancer.

---
<div align="center">

[← Previous Chapter](05_infrastructure_as_code.md) | [🏠 Back to Home](../README.md) | [Next Chapter: CI/CD →](07_cicd_and_devops.md)

</div>