# On-call Runbook (sample)

## Incident severity
Declare a SEV-1 incident when a customer-facing service is unavailable for most users, customer data may be exposed, or critical transactions are failing. The incident commander coordinates response and keeps a timestamped event log.

## First response
The first responder acknowledges an alert within five minutes, posts the incident channel link, and identifies the affected service. Do not make speculative production changes before the incident commander assigns an action.

## Customer communication
The incident commander approves external status updates. Share confirmed impact and the next update time; do not speculate about root cause or include customer identifiers.

## Recovery and review
After service is stable, record the recovery time and verify key user journeys. Schedule a blameless review within five business days and track follow-up actions with owners and due dates.
