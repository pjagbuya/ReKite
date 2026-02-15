# Quick Fix: Deploy Re:Kite Backend to Google Cloud Run

## ✅ You Have 3 Options

---

## Option 1: Use cloudbuild.yaml (EASIEST - Use This!)

The [cloudbuild.yaml](../cloudbuild.yaml) file tells Cloud Build where to find your Dockerfile.

### From Command Line:

```powershell
# Navigate to project ROOT (not backend!)
cd "c:\Users\Paul Josef\Downloads\Hackathon Re Kite\Base Project\ReKite"

# Submit build using cloudbuild.yaml
gcloud builds submit --config cloudbuild.yaml

# After build completes, set environment variables
gcloud run services update rekite-backend `
  --region us-central1 `
  --update-env-vars "DATABASE_URL=postgresql://postgres.rgxxajwpkxldurrmtlhn:Rek1t3r3k01t3rekiite@aws-1-ap-southeast-2.pooler.supabase.com:6543/postgres,SECRET_KEY=tsRhPX3RXf+/lFBE05PtfMJzah5Q0KjgGL8hYc4MwGHIpoM+z7knPLADmUTcnGX+e3Eyu0QBzgrf/e+qQiXvsA==,ALGORITHM=HS256,ACCESS_TOKEN_EXPIRE_MINUTES=30"
```

### From Cloud Console UI:

1. Go to [Cloud Run Console](https://console.cloud.google.com/run)
2. Click **"Create Service"**
3. Select **"Continuously deploy from a repository (source-based)"**
4. Click **"Set up with Cloud Build"**
5. Authenticate with GitHub
6. Select repository: `pjagbuya/ReKite`
7. Branch: `main`
8. **Build Configuration**: Select **"Cloud Build configuration file (yaml or json)"**
9. Cloud Build configuration file location: `/cloudbuild.yaml`
10. Click **"Save"**
11. Service name: `rekite-backend`
12. Region: `us-central1`
13. Authentication: **Allow unauthenticated invocations** ✅
14. CPU allocation: **CPU is always allocated**
15. Memory: **2 GiB**
16. Click **"Container, Variables & Secrets, Connections, Security"**
17. Add Environment Variables:
    ```
    DATABASE_URL=postgresql://postgres.rgxxajwpkxldurrmtlhn:Rek1t3r3k01t3rekiite@aws-1-ap-southeast-2.pooler.supabase.com:6543/postgres
    SECRET_KEY=tsRhPX3RXf+/lFBE05PtfMJzah5Q0KjgGL8hYc4MwGHIpoM+z7knPLADmUTcnGX+e3Eyu0QBzgrf/e+qQiXvsA==
    ALGORITHM=HS256
    ACCESS_TOKEN_EXPIRE_MINUTES=30
    ```
18. Click **"Create"**

---

## Option 2: Deploy from Backend Directory (Command Line)

```powershell
# Navigate to BACKEND directory
cd "c:\Users\Paul Josef\Downloads\Hackathon Re Kite\Base Project\ReKite\backend"

# Verify you're in the right place (should show Dockerfile)
dir Dockerfile

# Deploy directly from backend folder
gcloud run deploy rekite-backend `
  --source . `
  --platform managed `
  --region us-central1 `
  --allow-unauthenticated `
  --memory 2Gi `
  --cpu 1 `
  --timeout 300 `
  --max-instances 10 `
  --set-env-vars "DATABASE_URL=postgresql://postgres.rgxxajwpkxldurrmtlhn:Rek1t3r3k01t3rekiite@aws-1-ap-southeast-2.pooler.supabase.com:6543/postgres,SECRET_KEY=tsRhPX3RXf+/lFBE05PtfMJzah5Q0KjgGL8hYc4MwGHIpoM+z7knPLADmUTcnGX+e3Eyu0QBzgrf/e+qQiXvsA==,ALGORITHM=HS256,ACCESS_TOKEN_EXPIRE_MINUTES=30"
```

---

## Option 3: Use PowerShell Script

```powershell
# Navigate to backend directory
cd "c:\Users\Paul Josef\Downloads\Hackathon Re Kite\Base Project\ReKite\backend"

# Run script (will prompt for env vars)
.\deploy-gcp.ps1
```

---

## 🔍 Why You Got the Error

The error **"unexpected error reading Dockerfile: read .../backend: is a directory"** means:

- ❌ You ran `gcloud` from the **ROOT** directory (`ReKite/`)
- ❌ Cloud Build looked for `Dockerfile` in root
- ❌ It found a folder called `backend/` instead

**Solution**: Either use `cloudbuild.yaml` (Option 1) or run from `backend/` directory (Option 2).

---

## ✅ After Successful Deployment

You'll see:

```
Service [rekite-backend] revision [rekite-backend-00001-xyz] has been deployed
Service URL: https://rekite-backend-xxxxxxxxxxxx-uc.a.run.app
```

### Test Your API:

```powershell
# Health check
curl https://your-service-url/health

# Should return: {"status":"healthy"}
```

### Update Frontend:

In Vercel, set environment variable:
```
NEXT_PUBLIC_API_URL=https://your-service-url
```

---

## 🐛 Still Having Issues?

### Check Build Logs:
```powershell
gcloud builds list
gcloud builds log [BUILD_ID]
```

### Common Issues:

**"Permission denied"**
- Enable Cloud Build API: `gcloud services enable cloudbuild.googleapis.com`
- Enable billing for your project

**"Image not found"**
- Make sure Dockerfile is in the right location
- Use `cloudbuild.yaml` from Option 1

**"Out of memory during build"**
- Normal! First build takes 10-15 minutes
- Cloud Build has 4GB RAM for builds

---

## 💰 Cost Check

First deployment is **FREE** (within $300 credit). After that:
- **Free tier**: 2M requests/month, 360K GB-seconds compute
- **Your usage**: Likely $0-2/month for moderate use

---

**Recommendation**: Use **Option 1** with cloudbuild.yaml - it's the most reliable! 🚀
