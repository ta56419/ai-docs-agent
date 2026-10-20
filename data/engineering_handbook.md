# Engineering Handbook (sample knowledge base)

## Remote work
Employees may work remotely up to three days each week with their manager's approval. The team agrees on office days in the weekly planning meeting. Remote work does not change core availability hours, which are 10:00-15:00 in the employee's local time zone.

## Requesting access
Request access to a client environment through the service desk. Include the project name, the systems needed, and the business reason. Never put passwords, API keys, or personal access tokens in a ticket.

## Incident response
Report a suspected security incident to the on-call engineer immediately. Do not investigate production systems on your own. Record the time, affected service, and observed symptoms; do not copy customer data into chat messages.

## Code review
Open a pull request for every change. A change needs one reviewer approval and passing automated checks before it can be merged. Keep pull requests focused and explain how the change was verified.

## Deployment
Production deployments happen through the CI/CD pipeline after review. Do not deploy directly from a developer laptop. For a failed deployment, notify the on-call engineer and follow the rollback runbook.

## Learning budget
Each employee has an annual learning budget of 2,000 PLN. Discuss the course or certification with your manager before purchasing it, then submit the receipt through the expense system.

## Data handling
Use synthetic or anonymized data in development and testing. Store secrets in the approved secret manager. Do not commit credentials or customer data to source control.
