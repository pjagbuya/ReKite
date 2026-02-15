#!/bin/bash

# Re:Kite Google Cloud Run Deployment Script
# This script automates the deployment process

set -e  # Exit on error

echo "🚀 Re:Kite Google Cloud Deployment"
echo "=================================="

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI not found. Please install it first:"
    echo "   https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Prompt for project ID
read -p "Enter your Google Cloud Project ID (e.g., rekite-app): " PROJECT_ID

if [ -z "$PROJECT_ID" ]; then
    echo "❌ Project ID cannot be empty"
    exit 1
fi

echo ""
echo "📋 Configuration:"
echo "   Project ID: $PROJECT_ID"
echo "   Region: us-central1"
echo "   Service: rekite-backend"
echo ""

# Set project
echo "🔧 Setting up project..."
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "🔌 Enabling required APIs..."
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com

# Prompt for environment variables
echo ""
echo "🔐 Environment Variables"
echo "Please provide your environment variables:"
echo ""

read -p "DATABASE_URL: " DATABASE_URL
read -p "SECRET_KEY: " SECRET_KEY

if [ -z "$DATABASE_URL" ] || [ -z "$SECRET_KEY" ]; then
    echo "❌ DATABASE_URL and SECRET_KEY are required"
    exit 1
fi

# Optional frontend URL
read -p "FRONTEND_URL (optional, press Enter to skip): " FRONTEND_URL

# Build deployment command
DEPLOY_CMD="gcloud run deploy rekite-backend \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 1 \
  --timeout 300 \
  --max-instances 10 \
  --set-env-vars DATABASE_URL='$DATABASE_URL' \
  --set-env-vars SECRET_KEY='$SECRET_KEY' \
  --set-env-vars ALGORITHM=HS256 \
  --set-env-vars ACCESS_TOKEN_EXPIRE_MINUTES=30"

if [ ! -z "$FRONTEND_URL" ]; then
    DEPLOY_CMD="$DEPLOY_CMD --set-env-vars FRONTEND_URL='$FRONTEND_URL'"
fi

echo ""
echo "🐳 Building and deploying to Cloud Run..."
echo "This will take 10-15 minutes for the first deployment..."
echo ""

# Navigate to backend directory
cd "$(dirname "$0")"

# Execute deployment
eval $DEPLOY_CMD

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📝 Next steps:"
echo "   1. Copy the Service URL shown above"
echo "   2. Update your frontend NEXT_PUBLIC_API_URL to use this URL"
echo "   3. Test your API: visit [SERVICE_URL]/health"
echo "   4. View API docs: visit [SERVICE_URL]/docs"
echo ""
echo "🎉 Your Re:Kite backend is now live on Google Cloud Run!"
