# Community Metrics Dashboard 📊

An automated dashboard for tracking open-source community health and growth metrics across multiple platforms including GitHub, Discourse forums, Slack workspaces, and PyPI downloads.

## 🌟 Features

- **Automated Data Collection**: Daily collection of metrics from multiple platforms
- **Beautiful Dashboard**: Clean, responsive web interface with interactive charts
- **GitHub Pages Integration**: Automatically deploys and updates via GitHub Actions
- **Historical Tracking**: CSV-based storage for long-term trend analysis
- **Multiple Data Sources**: GitHub, Discourse, Slack, PyPI, and more

## 📈 Metrics Tracked

### GitHub Repository Metrics
- ⭐ Stars and forks
- 👥 Contributors count
- 🐛 Open issues and pull requests
- 📊 Commit activity

### Community Engagement
- 💬 Discourse forum users and posts
- 💼 Slack workspace members and activity
- 📦 PyPI package download statistics
- 📈 Growth trends and analytics

## 🚀 Quick Start

### 1. Repository Setup

1. **Fork or clone this repository**
2. **Copy configuration template**:
   ```bash
   cp config.yaml.example config.yaml
   ```

3. **Configure your data sources** in `config.yaml`:
   ```yaml
   github:
     repository: "your-org/your-repo"
     token: "ghp_your_token_here"
   
   discourse:
     base_url: "https://your-forum.discourse.group"
     api_key: "your_api_key"
   
   pypi:
     package_name: "your-package-name"
   ```

### 2. GitHub Secrets Configuration

Add the following secrets to your GitHub repository (Settings → Secrets and variables → Actions):

- `GITHUB_TOKEN`: Personal access token with repo permissions
- `DISCOURSE_API_KEY`: Discourse API key (if using Discourse)
- `SLACK_TOKEN`: Slack bot token (if using Slack)

### 3. Enable GitHub Pages

1. Go to repository Settings → Pages
2. Set source to "Deploy from a branch"
3. Select `gh-pages` branch
4. Your dashboard will be available at `https://your-username.github.io/your-repo-name`

### 4. Manual Testing (Optional)

```bash
# Install dependencies
pip install -r requirements.txt

# Test metrics collection
python scripts/collect_metrics.py

# Test dashboard generation
python scripts/render_dashboard.py

# View the generated dashboard
open dashboard/index.html
```

## 🔧 Configuration

### Data Sources Configuration

The `config.yaml` file controls which metrics are collected:

```yaml
# GitHub Configuration
github:
  repository: "owner/repo-name"
  token: "your_github_token"  # Optional but recommended

# Discourse Forum
discourse:
  base_url: "https://discourse.example.com"
  api_key: "your_discourse_api_key"

# Slack Workspace
slack:
  token: "xoxb-your-slack-token"

# PyPI Package
pypi:
  package_name: "your-package-name"
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