# Re:Kite - Google Cloud Deployment Guide

## 🚀 Deploy to Google Cloud Run

Google Cloud Run is a serverless platform that automatically scales your containerized application. Perfect for Re:Kite!

**Benefits:**
- ✅ Pay only for what you use (very cost-effective)
- ✅ Automatic scaling (0 to thousands of requests)
- ✅ Free tier: 2 million requests/month
- ✅ Supports ML models with up to 4GB RAM
- ✅ Built-in HTTPS and custom domains

---

## 📋 Prerequisites

1. **Google Cloud Account**: [Sign up here](https://cloud.google.com/free) (includes $300 free credit)
2. **gcloud CLI**: [Install gcloud](https://cloud.google.com/sdk/docs/install)
3. **Docker** (optional, for local testing): [Install Docker](https://docs.docker.com/get-docker/)

---

## 🔧 Step 1: Set Up Google Cloud Project

### 1.1 Create a New Project

```bash
# Set your project ID (choose a unique name)
export PROJECT_ID="rekite-app"

# Create project
gcloud projects create $PROJECT_ID --name="Re:Kite"

# Set as active project
gcloud config set project $PROJECT_ID
```

### 1.2 Enable Required APIs

```bash
# Enable Cloud Run and Container Registry
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

### 1.3 Set Up Billing

- Go to [Google Cloud Console](https://console.cloud.google.com)
- Navigate to Billing → Link a billing account
- (Required even for free tier, but you won't be charged within free limits)

---

## 🐳 Step 2: Build and Deploy

### Option A: Direct Deploy (Easiest)

This builds and deploys in one command:

```bash
# IMPORTANT: Must navigate to backend directory first!
cd backend

# Verify you're in the right directory (should show Dockerfile)
ls Dockerfile

# Deploy to Cloud Run
gcloud run deploy rekite-backend \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 1 \
  --timeout 300 \
  --max-instances 10 \
  --set-env-vars "DATABASE_URL=postgresql://postgres.rgxxajwpkxldurrmtlhn:Rek1t3r3k01t3rekiite@aws-1-ap-southeast-2.pooler.supabase.com:6543/postgres" \
  --set-env-vars "SECRET_KEY=tsRhPX3RXf+/lFBE05PtfMJzah5Q0KjgGL8hYc4MwGHIpoM+z7knPLADmUTcnGX+e3Eyu0QBzgrf/e+qQiXvsA==" \
  --set-env-vars "ALGORITHM=HS256" \
  --set-env-vars "ACCESS_TOKEN_EXPIRE_MINUTES=30"
```

**Note:** Replace the environment variables with your actual values!

**Common Error:** If you get "backend: is a directory" error, you're in the wrong folder. Make sure you're IN the backend directory before running the deploy command.

### Option B: Build with Docker First (For Testing)

```bash
# Navigate to backend directory
cd backend

# Build Docker image
docker build -t rekite-backend .

# Test locally
docker run -p 8080:8080 \
  -e DATABASE_URL="your-database-url" \
  -e SECRET_KEY="your-secret-key" \
  rekite-backend

# Visit http://localhost:8080/health to test
```

Then deploy:

```bash
# Tag for Google Container Registry
docker tag rekite-backend gcr.io/$PROJECT_ID/rekite-backend

# Push to GCR
docker push gcr.io/$PROJECT_ID/rekite-backend

# Deploy to Cloud Run
gcloud run deploy rekite-backend \
  --image gcr.io/$PROJECT_ID/rekite-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi
```

---

## 🌐 Step 3: Get Your Service URL

After deployment completes, you'll see output like:

```
Service [rekite-backend] revision [rekite-backend-00001-abc] has been deployed and is serving 100 percent of traffic.
Service URL: https://rekite-backend-xxxxxxxxxxxx-uc.a.run.app
```

**Save this URL!** You'll need it for your frontend.

### Test Your Deployment

```bash
# Health check
curl https://your-service-url/health

# API docs
# Visit: https://your-service-url/docs
```

---

## 🎨 Step 4: Deploy Frontend to Vercel

1. Go to [vercel.com](https://vercel.com) and import your repo
2. Set root directory to `frontend`
3. Add environment variable:
   ```
   NEXT_PUBLIC_API_URL=https://your-cloud-run-url
   ```
4. Deploy!

---

## 🔒 Step 5: Configure CORS (Optional)

Update backend to allow your Vercel domain:

```bash
# Update with your Vercel URL
gcloud run services update rekite-backend \
  --set-env-vars "FRONTEND_URL=https://your-app.vercel.app" \
  --region us-central1
```

---

## 💰 Cost Estimation

### Free Tier (No Cost)
- **Requests**: 2 million/month
- **Compute time**: 360,000 GB-seconds/month
- **Network**: 1 GB egress/month

### After Free Tier
- **Compute**: ~$0.00002400 per GB-second
- **Requests**: $0.40 per million requests
- **Memory (2GB)**: ~$0.0000025 per GB-second

**Example:** 100,000 requests/month with 2GB RAM, 500ms avg response:
- Compute: 100,000 × 0.5s × 2GB × $0.0000025 = **$0.25/month**
- Requests: 100,000 / 1,000,000 × $0.40 = **$0.04/month**
- **Total: ~$0.29/month** (well within free tier!)

**Compare to Render:** $7/month for 512MB always-on

---

## 📊 Monitoring & Management

### View Logs

```bash
# Stream logs
gcloud run services logs tail rekite-backend --region us-central1

# Follow logs
gcloud run services logs read rekite-backend --region us-central1 --limit 50
```

### View Metrics

Visit [Cloud Console → Cloud Run → Your Service](https://console.cloud.google.com/run)
- Request count
- Response time
- Error rate
- Memory usage
- CPU utilization

### Update Environment Variables

```bash
gcloud run services update rekite-backend \
  --set-env-vars "NEW_VAR=value" \
  --region us-central1
```

### Update Service Configuration

```bash
# Increase memory
gcloud run services update rekite-backend \
  --memory 4Gi \
  --region us-central1

# Change concurrency
gcloud run services update rekite-backend \
  --concurrency 80 \
  --region us-central1
```

---

## 🔧 Troubleshooting

### Build Fails

**Error: Python packages won't install**
- Check Dockerfile has `build-essential` for compilation
- Verify requirements.txt is valid
- Check logs: `gcloud builds log [BUILD_ID]`

### Out of Memory

**Error: Service uses too much memory**
- Increase memory: `--memory 4Gi`
- Check ML model loading (sentence-transformers needs ~2GB)
- Enable Cloud Logging to see memory spikes

### Cold Starts

**First request after idle is slow (30-60s)**
- ML models take time to load
- Solutions:
  - Set minimum instances: `--min-instances 1` (costs more but faster)
  - Use lighter model (already using all-MiniLM-L6-v2, which is small)
  - Accept cold starts (users wait once, then fast)

### Database Connection Issues

**Error: Can't connect to Supabase**
- Verify `DATABASE_URL` has `sslmode=require` parameter
- Check Supabase allows connections from Google Cloud IPs
- Test connection locally first

### CORS Errors

**Frontend can't connect**
- Verify `FRONTEND_URL` env var is set
- Check main.py CORS configuration
- Ensure `--allow-unauthenticated` flag is set

---

## 🚀 CI/CD with Cloud Build (Optional)

Create `cloudbuild.yaml` in backend directory:

```yaml
steps:
  # Build the container image
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/rekite-backend', '.']
  
  # Push to Container Registry
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/rekite-backend']
  
  # Deploy to Cloud Run
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - 'rekite-backend'
      - '--image=gcr.io/$PROJECT_ID/rekite-backend'
      - '--region=us-central1'
      - '--platform=managed'
      - '--allow-unauthenticated'
      - '--memory=2Gi'

images:
  - 'gcr.io/$PROJECT_ID/rekite-backend'
```

Then trigger builds automatically on git push!

---

## 🎯 Best Practices

### Security
- [ ] Use Secret Manager for sensitive env vars
- [ ] Enable VPC connector for private database access
- [ ] Set up Cloud Armor for DDoS protection
- [ ] Use service accounts with minimal permissions

### Performance
- [ ] Set `--cpu-throttling` based on workload
- [ ] Configure `--max-instances` to control costs
- [ ] Use `--min-instances 1` for critical services (no cold starts)
- [ ] Enable HTTP/2 for better performance

### Cost Optimization
- [ ] Set `--max-instances` to prevent runaway costs
- [ ] Delete old container images from GCR
- [ ] Monitor usage in Billing dashboard
- [ ] Use `--cpu 1` (default) unless you need more

---

## 📚 Additional Resources

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud Run Pricing](https://cloud.google.com/run/pricing)
- [Container Best Practices](https://cloud.google.com/architecture/best-practices-for-building-containers)
- [FastAPI on Cloud Run](https://cloud.google.com/run/docs/quickstarts/build-and-deploy/deploy-python-service)

---

## ✨ Quick Reference

### Common Commands

```bash
# Deploy
gcloud run deploy rekite-backend --source .

# View logs
gcloud run services logs tail rekite-backend

# Update env vars
gcloud run services update rekite-backend --set-env-vars "KEY=value"

# Delete service
gcloud run services delete rekite-backend

# List services
gcloud run services list

# Describe service
gcloud run services describe rekite-backend
```

### Environment Variables Needed

```bash
DATABASE_URL=postgresql://...
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
FRONTEND_URL=https://your-app.vercel.app  # Optional
```

---

## 🎉 You're Done!

Your Re:Kite backend is now running on Google Cloud Run with:
- ✅ Automatic scaling
- ✅ Pay-per-use pricing
- ✅ Global CDN
- ✅ HTTPS included
- ✅ Full ML capabilities

Deploy your frontend to Vercel and you're live! 🚀
