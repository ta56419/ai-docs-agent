# Developer Workflow (sample)

## Local setup
Use the Python version pinned by the project and create an isolated virtual environment. Install the dependencies listed by the project before running its checks.

## Branches and pull requests
Create a short-lived branch from the current main branch. Use a descriptive commit message and open a pull request with a summary, testing notes, and any deployment impact.

## Automated checks
Run the unit test suite and lint checks before requesting review. CI repeats these checks on every pull request. A failing required check must be fixed or explicitly explained before merge.

## Secrets and configuration
Read configuration from environment variables or the approved secret manager. Keep local environment files out of version control and rotate any credential that was accidentally exposed.

## Database changes
Write schema changes as versioned migrations. Verify migrations against a disposable local database and include a rollback plan for changes that may affect existing records.
