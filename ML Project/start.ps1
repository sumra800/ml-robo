param(
    [switch]$Build
)

$ErrorActionPreference = "Stop"

Write-Host "Starting AI Waste Sorting stack with Docker Compose..."

if ($Build) {
    docker compose up --build
}
else {
    docker compose up
}
