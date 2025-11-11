# SCOPED Community Metrics Dashboard 📊

An automated dashboard for tracking open-source community health and growth metrics across multiple platforms including GitHub, Discourse forums, Slack workspaces, and PyPI downloads.

## 🌟 Features

- **Automated Data Collection**: Daily collection of metrics from multiple platforms
- **Beautiful Dashboard**: Clean, responsive web interface with interactive charts
- **GitHub Pages Integration**: Automatically deploys and updates via GitHub Actions
- **Historical Tracking**: CSV-based storage for long-term trend analysis
- **Multiple Data Sources**: GitHub, Discourse, Slack, PyPI, and more

## 📈 Metrics Tracked

### GitHub Organization Metrics
- 📁 Total repositories in the organization
- ⭐ Aggregate stars and forks across all repos
- 👥 Organization members and unique contributors
- 🐛 Open issues and pull requests organization-wide
- 📊 Repository activity and language statistics
- � Active repositories in the last 30 days

### Academic Impact & Community Engagement
- 📚 Google Scholar author profiles and citation metrics
- 📄 Publication counts, citations, and h-index tracking
- � YouTube channel metrics (subscribers, views, videos)
- �💼 Slack workspace members and activity (optional)
- 📦 PyPI package download statistics (optional)
- 📈 Growth trends and analytics

## 🚀 Quick Start

### 1. Repository Setup

1. **Fork or clone this repository**

2. **Edit `config.yaml`** to configure your data sources (without any API keys/tokens):
   ```yaml
   github:
     organization: "SeisSCOPED"  # Your GitHub organization name
     repository: "SeisSCOPED/community-metrics"  # Main repository
   
   youtube:
     channel_url: "https://www.youtube.com/@scoped6259"  # Your YouTube channel URL
   
   google_scholar:
     author_ids:  # Google Scholar author IDs to track
       - "GR8BOxsAAAAJ"  # Get from Scholar profile URL
     institution: "University of Washington"  # Optional
   
   pypi:
     package_name: "your-package-name"  # Optional: your PyPI package
   ```
   
   **⚠️ Important**: Do NOT add API keys or tokens to this file! Use GitHub Secrets instead (see next step).

### 2. Add API Keys as GitHub Secrets (Secure Method)

**Required for automated collection**. Add secrets to your repository:

1. Go to your GitHub repository **Settings**
2. Navigate to **Secrets and variables** → **Actions**
3. Click **New repository secret** for each of the following:

#### Required Secret:
- **Name**: `GH_PAT`
  - **Value**: Personal access token with `repo`, `read:org`, and `workflow` permissions
  - **How to create**: 
    1. Go to https://github.com/settings/tokens
    2. Click "Generate new token (classic)"
    3. Give it a name (e.g., "community-metrics")
    4. Select scopes: ✅ `repo`, ✅ `read:org`, ✅ `read:user`, ✅ `workflow`
    5. Click "Generate token" at the bottom
    6. Copy the token (starts with `ghp_...`) - you won't see it again!
    7. Add to GitHub Secrets as `GH_PAT`

#### Recommended Secrets:
- **Name**: `YOUTUBE_API_KEY`
  - **Value**: YouTube Data API v3 key
  - **Why**: Web scraping is unreliable; API provides accurate metrics
  - **How to create**: See section below

#### Optional Secrets:
- **Name**: `SLACK_TOKEN`
  - **Value**: Slack bot token (if tracking Slack metrics)

**Note**: Google Scholar requires no API key (uses web scraping).

#### How to Get a YouTube API Key

YouTube web scraping is unreliable. For accurate metrics, use the YouTube Data API (free):

**Step-by-step**:
1. Go to https://console.cloud.google.com/
2. Click **"Select a project"** → **"New Project"**
3. Enter project name (e.g., "youtube-metrics") → Click **"Create"**
4. Use the search bar to find **"YouTube Data API v3"** → Click it
5. Click the blue **"ENABLE"** button
6. Click **"Credentials"** in the left sidebar
7. Click **"+ CREATE CREDENTIALS"** → Select **"API key"**
8. **Copy the API key** that appears
9. Add to GitHub Secrets as `YOUTUBE_API_KEY` (see step 2 above)

**Cost**: Free forever (10,000 quota units/day, channel stats use ~5 units)

**Note**: No credit card or VM required - just enable the API and create a key!

### 3. Enable GitHub Pages

1. Go to repository Settings → Pages
2. Set source to "Deploy from a branch"
3. Select `gh-pages` branch
4. Your dashboard will be available at `https://your-username.github.io/your-repo-name`

### 4. Manual Testing (Optional)

**For local testing only** - use environment variables (never commit keys!):

```bash
# Install dependencies
pip install -r requirements.txt

# Set API keys as environment variables (temporary, for this terminal session)
export GITHUB_TOKEN="ghp_your_token_here"
export YOUTUBE_API_KEY="AIza_your_key_here"

# Test metrics collection
python scripts/collect_metrics.py

# Test dashboard generation
python scripts/render_dashboard.py

# View the generated dashboard
open dashboard/index.html
```

**Security reminder**: Never add API keys to `config.yaml` or commit them to git!

## 🔧 Configuration

### Data Sources Configuration

The `config.yaml` file controls which metrics are collected:

```yaml
# GitHub Organization Configuration
github:
  organization: "SeisSCOPED"
  repository: "SeisSCOPED/community-metrics"
  token: "your_github_token"  # Required for organization metrics
  collect_org_metrics: true
  
  # Comprehensive metrics collected:
  # - Organization overview (repos, members, followers)
  # - All repository statistics (stars, forks, watchers)
  # - Contributor activity across all repositories
  # - Issue and PR activity organization-wide
  # - Language distribution and activity trends

# Google Scholar Configuration
google_scholar:
  author_ids:  # List of Google Scholar author IDs to track
    - "ABC123DEF"  # Extract from Scholar profile URL
    - "XYZ789GHI"  # https://scholar.google.com/citations?user=ABC123DEF
  institution: "University Name"  # Optional: institution filter
  
  # Metrics collected:
  # - Total citations for each author
  # - h-index and i10-index
  # - Recent publication counts
  # - Citation growth trends
  # - Aggregate metrics across all tracked authors

# YouTube Configuration
youtube:
  channel_url: "https://www.youtube.com/@yourchannel"  # Your YouTube channel URL
  api_key: "AIzaSy..."  # Optional: YouTube Data API key (recommended)
  
  # Metrics collected:
  # - Subscriber count
  # - Total video views
  # - Number of videos
  # - Channel growth trends
  # 
  # Note: Web scraping fallback available but less reliable
  # Get API key: https://console.cloud.google.com/apis/credentials

# Optional integrations
slack:
  token: "xoxb-your-slack-token"  # Slack workspace metrics

pypi:
  package_name: "your-package-name"  # PyPI download statistics
```

### GitHub Actions Workflow

The dashboard updates automatically via GitHub Actions:

- **Schedule**: Daily at 6 AM UTC
- **Manual trigger**: Available via "Actions" tab
- **Workflow file**: `.github/workflows/update_dashboard.yml`

## 📁 Project Structure

```
community-dashboard/
│
├── .github/workflows/
│   └── update_dashboard.yml     # GitHub Actions workflow
│
├── metrics/                     # Raw metrics storage
│   ├── community_metrics.csv    # Historical data
│   └── latest.json             # Current metrics
│
├── dashboard/                   # Generated static site
│   └── index.html              # Main dashboard page
│
├── scripts/                     # Data processing scripts
│   ├── collect_metrics.py      # Metrics collection
│   └── render_dashboard.py     # Dashboard generation
│
├── config.yaml                 # Configuration file
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
```

## 🛠️ Customization

### Adding New Metrics

1. **Extend the collector** in `scripts/collect_metrics.py`:
   ```python
   def get_custom_metrics(self):
       # Your custom metrics collection logic
       return {'custom_metric': value}
   ```

2. **Update the dashboard** in `scripts/render_dashboard.py`:
   ```python
   # Add custom metric to template
   ```

3. **Modify the HTML template** to display your new metrics

### Styling the Dashboard

Edit the CSS in `scripts/render_dashboard.py` template section or create a separate CSS file.

### Changing Update Frequency

Modify the cron schedule in `.github/workflows/update_dashboard.yml`:

```yaml
on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours
    # - cron: '0 6 * * 1'   # Weekly on Monday
```

## 🔍 Troubleshooting

### Common Issues

1. **GitHub API Rate Limiting**
   - Add a GitHub token to increase rate limits
   - Check the Actions logs for rate limit errors

2. **Missing Data**
   - Verify API keys are correctly set in GitHub Secrets
   - Check the Actions workflow logs for collection errors

3. **Dashboard Not Updating**
   - Ensure GitHub Pages is enabled
   - Check that the `gh-pages` branch exists
   - Verify the workflow has write permissions

### Debug Locally

```bash
# Test individual components
python scripts/collect_metrics.py
python scripts/render_dashboard.py

# Check generated files
cat metrics/latest.json
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/your-org/community-metrics.git
cd community-metrics

# Install development dependencies
pip install -r requirements.txt

# Run tests (if implemented)
python -m pytest tests/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Chart.js](https://www.chartjs.org/) for beautiful charts
- [GitHub Actions](https://github.com/features/actions) for automation
- [GitHub Pages](https://pages.github.com/) for free hosting

---

**Made with ❤️ for the open-source community**

> 💡 **Tip**: Star this repository to show your support and help others discover this tool!