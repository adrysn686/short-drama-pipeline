# One-time local setup: copies the env template and brings up the stack.
if (-not (Test-Path .env)) {
    Copy-Item .env.example .env
    Write-Output "Created .env from .env.example - fill in API keys before starting the pipeline."
}

docker compose up -d
Write-Output "n8n:      http://localhost:5678"
Write-Output "API docs: http://localhost:8000/docs"
