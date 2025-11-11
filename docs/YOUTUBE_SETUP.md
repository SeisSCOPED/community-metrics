# YouTube Metrics Setup Guide

This guide explains how to set up YouTube metrics collection for your community dashboard.

## Why Use YouTube Data API?

YouTube heavily obfuscates their channel data to prevent scraping. While this system includes a web scraping fallback, it's **highly unreliable** and often returns zeros. The YouTube Data API provides:

- ✅ Accurate, real-time data
- ✅ Reliable subscriber counts
- ✅ Total view counts
- ✅ Video counts
- ✅ Fast and efficient
- ✅ Free tier with generous quota (10,000 units/day)

Channel statistics queries use minimal quota (~5 units per request), so daily updates are well within the free tier.

## Setup Steps

### 1. Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Enter a project name (e.g., "Community Metrics Dashboard")
4. Click "Create"

### 2. Enable YouTube Data API v3

1. In your project, go to "APIs & Services" → "Library"
2. Search for "YouTube Data API v3"
3. Click on it and click "Enable"

### 3. Create API Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "API Key"
3. Your API key will be generated
4. (Optional) Click "Restrict Key" to limit usage:
   - Under "API restrictions", select "Restrict key"
   - Select "YouTube Data API v3"
   - Under "Application restrictions", you can:
     - Select "HTTP referrers" and add your GitHub Actions IP (not recommended as IPs change)
     - Or leave unrestricted but monitor usage
5. Click "Save"

### 4. Add API Key to GitHub Secrets

1. Go to your GitHub repository
2. Navigate to Settings → Secrets and variables → Actions
3. Click "New repository secret"
4. Name: `YOUTUBE_API_KEY`
5. Value: Paste your API key
6. Click "Add secret"

### 5. (Optional) Add to Config for Local Testing

If you want to test locally:

1. Open `config.yaml`
2. Uncomment the `api_key` line under `youtube`
3. Paste your API key
4. **Important**: Don't commit this file with your API key! Add it to `.gitignore` if needed

```yaml
youtube:
  channel_url: "https://www.youtube.com/@scoped6259"
  api_key: "AIzaSy..."  # Your API key here
```

## Finding Your Channel URL

Your YouTube channel URL should be in one of these formats:

- `https://www.youtube.com/@customhandle` (Custom handle - preferred)
- `https://www.youtube.com/channel/UC...` (Channel ID format)

To find it:
1. Go to YouTube and sign in
2. Click your profile icon → "Your channel"
3. Copy the URL from your browser

## Testing the Setup

### Test Locally

```bash
# Set the API key environment variable
export YOUTUBE_API_KEY="your-api-key-here"

# Run the collection script
python scripts/collect_metrics.py

# Check the output
cat metrics/latest.json | grep -A 5 youtube
```

You should see:
```json
"youtube": {
  "enabled": true,
  "channel_url": "https://www.youtube.com/@scoped6259",
  "subscribers": 156,
  "total_views": 12850,
  "video_count": 24,
  "method": "api"
}
```

### Test in GitHub Actions

1. Push your changes to GitHub
2. Go to Actions tab
3. Click "Update Community Dashboard" workflow
4. Click "Run workflow" → "Run workflow"
5. Wait for completion
6. Check the logs for "YouTube" section

## Quota and Costs

- **Free Tier**: 10,000 units per day
- **Channel Statistics Query**: ~5 units per call
- **Daily Updates**: ~5 units/day (well within free tier)
- **Monthly Cost**: $0 (free)

Even with hourly updates, you'd only use ~120 units/day, still well within the free tier.

## Troubleshooting

### Error: "The request cannot be completed because you have exceeded your quota"

**Solution**: Your API key has hit the daily quota limit.
- Check if you have other services using the same API key
- Wait 24 hours for quota to reset
- Create a new API key dedicated to this project

### Error: "API key not valid"

**Solution**: 
- Verify the API key is correct in GitHub Secrets
- Make sure you enabled "YouTube Data API v3" in your Google Cloud project
- Check that the API key hasn't been restricted to exclude the YouTube API

### Getting 0 subscribers/views

**Causes**:
1. API key not configured → Falls back to web scraping (unreliable)
2. Wrong channel URL format
3. Channel privacy settings

**Solutions**:
1. Add API key to GitHub Secrets as `YOUTUBE_API_KEY`
2. Use the `@handle` format: `https://www.youtube.com/@yourchannel`
3. Ensure your channel is public

### "Could not find channel via API"

**Solution**:
- Verify the channel URL is correct
- Try using the channel ID format instead of @handle
- Check that the channel is public and not deleted

## Alternative: Web Scraping (Not Recommended)

Without an API key, the system will attempt to scrape YouTube's website. This is:

- ❌ Unreliable (YouTube frequently changes their HTML structure)
- ❌ Often returns zeros or incomplete data
- ❌ Blocked by bot detection
- ❌ May violate YouTube's Terms of Service
- ❌ Requires additional dependencies (BeautifulSoup4)

**We strongly recommend using the YouTube Data API instead.**

## Security Best Practices

1. **Never commit API keys to Git**
   - Use GitHub Secrets for CI/CD
   - Use environment variables for local development
   - Add `config.yaml` to `.gitignore` if it contains keys

2. **Restrict API key usage**
   - Limit to YouTube Data API v3 only
   - Monitor usage in Google Cloud Console
   - Rotate keys periodically

3. **Monitor quota usage**
   - Check Google Cloud Console → APIs & Services → Dashboard
   - Set up quota alerts
   - Review usage patterns

## Additional Resources

- [YouTube Data API Documentation](https://developers.google.com/youtube/v3)
- [YouTube Data API Quota Calculator](https://developers.google.com/youtube/v3/determine_quota_cost)
- [Google Cloud Console](https://console.cloud.google.com/)
- [API Key Best Practices](https://cloud.google.com/docs/authentication/api-keys)

---

**Need Help?** Open an issue in the repository with details about your setup and error messages.
