# Re:Kite Google Cloud Run Deployment Script (PowerShell)
# This script automates the deployment process for Windows users

Write-Host "🚀 Re:Kite Google Cloud Deployment" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Check if gcloud is installed
try {
    $null = gcloud --version
} catch {
    Write-Host "❌ gcloud CLI not found. Please install it first:" -ForegroundColor Red
    Write-Host "   https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
    exit 1
}

# Prompt for project ID
$PROJECT_ID = Read-Host "Enter your Google Cloud Project ID (e.g., rekite-app)"

if ([string]::IsNullOrWhiteSpace($PROJECT_ID)) {
    Write-Host "❌ Project ID cannot be empty" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "📋 Configuration:" -ForegroundColor Green
Write-Host "   Project ID: $PROJECT_ID"
Write-Host "   Region: us-central1"
Write-Host "   Service: rekite-backend"
Write-Host ""

# Set project
Write-Host "🔧 Setting up project..." -ForegroundColor Yellow
gcloud config set project $PROJECT_ID

# Enable required APIs
Write-Host "🔌 Enabling required APIs..." -ForegroundColor Yellow
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com

# Prompt for environment variables
Write-Host ""
Write-Host "🔐 Environment Variables" -ForegroundColor Cyan
Write-Host "Please provide your environment variables:" -ForegroundColor Cyan
Write-Host ""

$DATABASE_URL = Read-Host "DATABASE_URL"
$SECRET_KEY = Read-Host "SECRET_KEY"

if ([string]::IsNullOrWhiteSpace($DATABASE_URL) -or [string]::IsNullOrWhiteSpace($SECRET_KEY)) {
    Write-Host "❌ DATABASE_URL and SECRET_KEY are required" -ForegroundColor Red
    exit 1
}

# Optional frontend URL
$FRONTEND_URL = Read-Host "FRONTEND_URL (optional, press Enter to skip)"

# Build deployment command
$envVars = @(
    "DATABASE_URL=$DATABASE_URL",
    "SECRET_KEY=$SECRET_KEY",
    "ALGORITHM=HS256",
    "ACCESS_TOKEN_EXPIRE_MINUTES=30"
)

if (-not [string]::IsNullOrWhiteSpace($FRONTEND_URL)) {
    $envVars += "FRONTEND_URL=$FRONTEND_URL"
}

$envVarsString = $envVars -join ","

Write-Host ""
Write-Host "🐳 Building and deploying to Cloud Run..." -ForegroundColor Cyan
Write-Host "This will take 10-15 minutes for the first deployment..." -ForegroundColor Yellow
Write-Host ""

# Make sure we're in the backend directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# Verify Dockerfile exists
if (-not (Test-Path "Dockerfile")) {
    Write-Host "❌ Dockerfile not found! Make sure you're in the backend directory." -ForegroundColor Red
    exit 1
}

# Execute deployment
gcloud run deploy rekite-backend `
  --source . `
  --platform managed `
  --region us-central1 `
  --allow-unauthenticated `
  --memory 2Gi `
  --cpu 1 `
  --timeout 300 `
  --max-instances 10 `
  --set-env-vars $envVarsString

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Deployment complete!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📝 Next steps:" -ForegroundColor Cyan
    Write-Host "   1. Copy the Service URL shown above"
    Write-Host "   2. Update your frontend NEXT_PUBLIC_API_URL to use this URL"
    Write-Host "   3. Test your API: visit [SERVICE_URL]/health"
    Write-Host "   4. View API docs: visit [SERVICE_URL]/docs"
    Write-Host ""
    Write-Host "🎉 Your Re:Kite backend is now live on Google Cloud Run!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "❌ Deployment failed. Check the error messages above." -ForegroundColor Red
    Write-Host "💡 Common issues:" -ForegroundColor Yellow
    Write-Host "   - Make sure you're in the backend directory"
    Write-Host "   - Verify billing is enabled for your project"
    Write-Host "   - Check that all APIs are enabled"
    exit 1
}
