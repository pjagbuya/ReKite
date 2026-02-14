# Re:Kite Deployment Guide - Render & Vercel

## 🚀 Quick Deployment (15 minutes)

### Step 1: Deploy Backend to Render

**Important:** The free tier has 512MB RAM. We use a lightweight version without heavy ML libraries.

1. **Go to [render.com](https://render.com)** and sign up/login

2. **Click "New +"** → **"Web Service"**

3. **Connect your GitHub repository**

4. **Configure the service:**
   ```
   Name: rekite-backend
   Region: Choose closest to you (Singapore for Asia-Pacific)
   Branch: main (or your default branch)
   Root Directory: backend
   Runtime: Python 3
   Build Command: chmod +x build.sh && ./build.sh
   Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```
   
   **Alternative Build Command (if build.sh fails):**
   ```
   pip install --upgrade pip && pip install -r requirements-production.txt
   ```

5. **Select Plan:** Free (512MB RAM - uses lightweight version)

6. **Add Environment Variables:**
   Click "Advanced" → "Add Environment Variable"
   
   Add these variables:
   ```
   DATABASE_URL=postgresql://postgres.rgxxajwpkxldurrmtlhn:Rek1t3r3k01t3rekiite@aws-1-ap-southeast-2.pooler.supabase.com:6543/postgres
   
   SECRET_KEY=tsRhPX3RXf+/lFBE05PtfMJzah5Q0KjgGL8hYc4MwGHIpoM+z7knPLADmUTcnGX+e3Eyu0QBzgrf/e+qQiXvsA==
   
   ALGORITHM=HS256
   
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   
   DEEPGRAM_API_KEY=e52f344a71cd1d3fcb4e8e3476b077b888e6efe3
   ```

7. **Click "Create Web Service"**

8. **Wait for deployment** (first build takes 10-12 minutes due to ML libraries)
   - You'll see logs streaming
   - When done, you'll get a URL like: `https://rekite-backend.onrender.com`

9. **Test your API:**
   - Visit: `https://rekite-backend.onrender.com/health`
   - Should return: `{"status":"healthy"}`
   - Visit: `https://rekite-backend.onrender.com/docs` for API documentation

---

### Step 2: Deploy Frontend to Vercel

1. **Go to [vercel.com](https://vercel.com)** and sign up/login with GitHub

2. **Click "Add New Project"**

3. **Import your GitHub repository**

4. **Configure the project:**
   ```
   Framework Preset: Next.js (auto-detected)
   Root Directory: frontend
   Build Command: npm run build (auto-detected)
   Output Directory: .next (auto-detected)
   Install Command: npm install (auto-detected)
   ```

5. **Add Environment Variable:**
   Click "Environment Variables"
   
   ```
   Name: NEXT_PUBLIC_API_URL
   Value: https://rekite-backend.onrender.com
   ```
   (Replace with your actual Render URL from Step 1)

6. **Click "Deploy"**

7. **Wait for deployment** (~2-3 minutes)
   - You'll get a URL like: `https://rekite-xyz123.vercel.app`

8. **Update Backend CORS (Optional):**
   - Go to Render dashboard → Your service → Environment
   - Add: `FRONTEND_URL=https://your-app.vercel.app`
   - Save and redeploy

---

## ✅ Verify Deployment

1. **Open your Vercel URL**: `https://your-app.vercel.app`
2. **Click "Sign Up"** and create a test account
3. **Login** and test the flashcard functionality

---

## 🔧 Troubleshooting

### Backend Issues

**Build timeout on Render:**
- First build takes 10-12 minutes (normal for ML libraries)
- Subsequent builds are much faster (~3-5 minutes)
- Free tier has 15-minute build limit - should work fine

**Rust/Cargo compilation errors:**
- Make sure `runtime.txt` exists with `python-3.11.8`
- Verify `build.sh` is executable and being used
- If still failing, manually set Python version in Render settings:
  - Dashboard → Settings → Environment → Python Version: 3.11
- The app uses pre-built wheels to avoid Rust compilation

**Out of memory errors (used over 512Mi):**
- Free tier has 512MB RAM limit
- Make sure you're using `requirements-production.txt` (lightweight)
- Verify build command uses: `pip install -r requirements-production.txt`
- If you need ML features, upgrade to Starter plan ($7/month)
- Check logs: Dashboard → Logs to see memory usage

**API not responding:**
- Check Render logs: Dashboard → Your service → Logs
- Verify environment variables are set correctly
- Check if service is sleeping (free tier sleeps after 15min)

**Database connection errors:**
- Verify DATABASE_URL is correct
- Check Supabase is not paused/rate limited
- Test database connection from Supabase dashboard

### Frontend Issues

**Can't connect to backend:**
- Verify NEXT_PUBLIC_API_URL is set correctly
- Check browser console for CORS errors
- Make sure backend URL doesn't have trailing slash

**Environment variable not updating:**
- Redeploy: Vercel Dashboard → Deployments → Redeploy
- Clear browser cache

---

## 💡 Tips

### Free Tier Limitations

**Render (Backend):**
- Sleeps after 15 minutes of inactivity
- First request after sleep takes 30-60 seconds to wake up
- 750 hours/month free
- Solution: Upgrade to $7/month for always-on

**Vercel (Frontend):**
- Always on
- 100GB bandwidth/month (plenty for development)
- No sleep time

### Performance

**Reduce wake-up time:**
- Use a service like [UptimeRobot](https://uptimerobot.com) to ping your API every 5 minutes (keeps it awake)
- Or upgrade to paid tier ($7/month)

### Updates

**Backend updates:**
- Push to GitHub → Render auto-deploys
- Or: Render Dashboard → Manual Deploy → Deploy latest commit

**Frontend updates:**
- Push to GitHub → Vercel auto-deploys
- Instant deployment (~1-2 minutes)

---

## 🎯 Next Steps

After successful deployment:

**Note on Free Tier Deployment:**
- The free tier (512MB RAM) uses `requirements-production.txt` (lightweight version)
- AI features use simple keyword matching instead of ML models
- For full ML features (sentence-transformers), upgrade to Render's Starter plan ($7/month with 512MB+)
- To enable full ML: Change build command to use `requirements.txt` instead

1. **Custom Domain (Optional):**
   - Vercel: Settings → Domains → Add your domain
   - Render: Settings → Custom Domain

2. **SSL/HTTPS:**
   - Both platforms provide free SSL automatically ✅

3. **Monitoring:**
   - Check Render logs for backend errors
   - Use Vercel Analytics for frontend monitoring

4. **Database Backups:**
   - Supabase provides automatic backups
   - Free tier: Daily backups retained for 7 days

---

## 📝 Environment Variables Summary

### Backend (Render)
```
DATABASE_URL=postgresql://postgres.rgxxajwpkxldurrmtlhn:Rek1t3r3k01t3rekiite@aws-1-ap-southeast-2.pooler.supabase.com:6543/postgres
SECRET_KEY=tsRhPX3RXf+/lFBE05PtfMJzah5Q0KjgGL8hYc4MwGHIpoM+z7knPLADmUTcnGX+e3Eyu0QBzgrf/e+qQiXvsA==
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DEEPGRAM_API_KEY=e52f344a71cd1d3fcb4e8e3476b077b888e6efe3
FRONTEND_URL=https://your-app.vercel.app (optional, add after frontend deployed)
```

### Frontend (Vercel)
```
NEXT_PUBLIC_API_URL=https://rekite-backend.onrender.com
```

---

## ✨ You're Done!

Your Re:Kite app is now live and accessible from anywhere! 🎉

**Share your app:**
- Frontend: `https://your-app.vercel.app`
- API Docs: `https://rekite-backend.onrender.com/docs`

Need help? Check the logs or reach out for support!
