#!/usr/bin/env python3
"""
Dashboard Rendering Script

This script generates the static HTML dashboard from collected metrics data.
It reads the latest metrics and historical CSV data to create visualizations.
"""

import json
import pandas as pd
from datetime import datetime
from pathlib import Path
from jinja2 import Template


class DashboardRenderer:
    def __init__(self):
        """Initialize the dashboard renderer."""
        self.base_dir = Path(__file__).parent.parent
        self.metrics_dir = self.base_dir / "metrics"
        self.dashboard_dir = self.base_dir / "dashboard"
        self.csv_file = self.metrics_dir / "community_metrics.csv"
        self.json_file = self.metrics_dir / "latest.json"
        self.output_file = self.dashboard_dir / "index.html"
        
    def load_latest_metrics(self):
        """Load the latest metrics from JSON file."""
        try:
            with open(self.json_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print("Latest metrics file not found. Using default values.")
            return self.get_default_metrics()
    
    def load_historical_data(self):
        """Load historical data from CSV file."""
        try:
            df = pd.read_csv(self.csv_file)
            # Convert date column to datetime
            df['date'] = pd.to_datetime(df['date'])
            return df
        except FileNotFoundError:
            print("Historical CSV file not found. Using sample data.")
            return self.get_sample_dataframe()
    
    def get_default_metrics(self):
        """Return default metrics structure."""
        return {
            'last_updated': datetime.utcnow().isoformat() + 'Z',
            'github': {
                'stars': 0,
                'forks': 0,
                'contributors': 0,
                'open_issues': 0,
                'open_prs': 0
            },
            'discourse': {
                'total_users': 0,
                'total_posts': 0,
                'active_users_30d': 0
            },
            'slack': {
                'total_members': 0,
                'active_members_30d': 0
            },
            'pypi': {
                'downloads_30d': 0
            }
        }
    
    def get_sample_dataframe(self):
        """Return sample dataframe for testing."""
        data = {
            'date': pd.date_range('2024-01-01', periods=30, freq='D'),
            'github_stars': range(100, 130),
            'github_forks': range(20, 50),
            'github_contributors': [10 + (i // 5) for i in range(30)],
            'pypi_downloads': [1000 + i * 50 for i in range(30)]
        }
        return pd.DataFrame(data)
    
    def prepare_chart_data(self, df):
        """Prepare data for JavaScript charts with historical progression."""
        if df.empty:
            return self._get_default_chart_data()
            
        # Get data for different time periods
        chart_data = {
            # Last 30 days for detailed view
            'dates_30d': df.tail(30)['date'].dt.strftime('%Y-%m-%d').tolist(),
            'total_stars_30d': df.tail(30)['total_stars'].tolist(),
            'total_repositories_30d': df.tail(30)['total_repositories'].tolist(),
            'unique_contributors_30d': df.tail(30)['unique_contributors'].tolist(),
            'scholar_citations_30d': df.tail(30)['scholar_citations'].tolist(),
            
            # Last 90 days for trend analysis
            'dates_90d': df.tail(90)['date'].dt.strftime('%Y-%m-%d').tolist(),
            'total_stars_90d': df.tail(90)['total_stars'].tolist(),
            'scholar_citations_90d': df.tail(90)['scholar_citations'].tolist(),
            
            # All available data
            'dates_all': df['date'].dt.strftime('%Y-%m-%d').tolist(),
            'total_stars_all': df['total_stars'].tolist(),
            'total_repositories_all': df['total_repositories'].tolist(),
            'unique_contributors_all': df['unique_contributors'].tolist(),
            'scholar_citations_all': df['scholar_citations'].tolist(),
            'total_forks_all': df['total_forks'].tolist(),
            
            # Growth calculations
            'data_points': len(df),
            'date_range_days': (df['date'].max() - df['date'].min()).days if len(df) > 1 else 0
        }
        
        return chart_data
    
    def _get_default_chart_data(self):
        """Default chart data when no historical data is available."""
        return {
            'dates_30d': [], 'total_stars_30d': [], 'total_repositories_30d': [],
            'unique_contributors_30d': [], 'scholar_citations_30d': [],
            'dates_90d': [], 'total_stars_90d': [], 'scholar_citations_90d': [],
            'dates_all': [], 'total_stars_all': [], 'total_repositories_all': [],
            'unique_contributors_all': [], 'scholar_citations_all': [], 'total_forks_all': [],
            'data_points': 0, 'date_range_days': 0
        }
    
    def calculate_trends(self, df):
        """Calculate trend indicators."""
        if len(df) < 2:
            return {'all_positive': True, 'trends': {}}
        
        recent = df.tail(7)  # Last 7 days
        older = df.tail(14).head(7)  # Previous 7 days
        
        trends = {}
        
        for column in ['github_stars', 'github_forks', 'github_contributors']:
            if column in df.columns:
                recent_avg = recent[column].mean()
                older_avg = older[column].mean() if len(older) > 0 else recent_avg
                trends[column] = {
                    'direction': 'up' if recent_avg > older_avg else 'down',
                    'change': abs(recent_avg - older_avg)
                }
        
        return {
            'trends': trends,
            'all_positive': all(t['direction'] == 'up' for t in trends.values())
        }
    
    def generate_html_template(self):
        """Generate the HTML template with embedded data."""
        template_str = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Community Metrics Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f7;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            padding: 40px;
        }
        h1 {
            text-align: center;
            color: #1d1d1f;
            margin-bottom: 40px;
            font-size: 2.5em;
        }
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 24px;
            margin-bottom: 50px;
        }
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
            transition: transform 0.3s ease;
        }
        .metric-card:hover {
            transform: translateY(-5px);
        }
        .metric-value {
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 8px;
        }
        .metric-label {
            font-size: 1.1em;
            opacity: 0.9;
        }
        .charts-container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 40px;
            margin-top: 40px;
        }
        .chart-container {
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        }
        .chart-container h3 {
            color: #333;
            margin-bottom: 20px;
            font-size: 1.4em;
        }
        .last-updated {
            text-align: center;
            color: #666;
            font-size: 0.95em;
            margin-top: 40px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
        }
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #28a745;
            margin-right: 8px;
        }
        @media (max-width: 768px) {
            .charts-container {
                grid-template-columns: 1fr;
            }
            .container {
                padding: 20px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌟 Community Metrics Dashboard</h1>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value">{{ metrics.github.stars }}</div>
                <div class="metric-label">⭐ GitHub Stars</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{{ metrics.github.contributors }}</div>
                <div class="metric-label">👥 Contributors</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{{ metrics.github.forks }}</div>
                <div class="metric-label">🍴 Forks</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{{ metrics.pypi.downloads_30d }}</div>
                <div class="metric-label">📦 Downloads (30d)</div>
            </div>
        </div>

        <div class="charts-container">
            <div class="chart-container">
                <h3>📈 GitHub Growth Over Time</h3>
                <canvas id="githubChart" height="300"></canvas>
            </div>
            <div class="chart-container">
                <h3>👥 Community Overview</h3>
                <canvas id="communityChart" height="300"></canvas>
            </div>
        </div>

        <div class="last-updated">
            <span class="status-indicator"></span>
            Last updated: {{ last_updated_formatted }}
            <br>
            <small>Automatically updated daily via GitHub Actions</small>
        </div>
    </div>

    <script>
        // Chart data embedded from Python
        const chartData = {{ chart_data | tojson }};
        const communityData = {
            contributors: {{ metrics.github.contributors }},
            discourse_users: {{ metrics.discourse.total_users }},
            slack_members: {{ metrics.slack.total_members }},
            open_issues: {{ metrics.github.open_issues }}
        };

        // GitHub Growth Chart
        const githubCtx = document.getElementById('githubChart').getContext('2d');
        new Chart(githubCtx, {
            type: 'line',
            data: {
                labels: chartData.dates,
                datasets: [
                    {
                        label: 'Stars',
                        data: chartData.github_stars,
                        borderColor: '#007bff',
                        backgroundColor: 'rgba(0,123,255,0.1)',
                        tension: 0.4,
                        fill: true
                    },
                    {
                        label: 'Forks',
                        data: chartData.github_forks,
                        borderColor: '#28a745',
                        backgroundColor: 'rgba(40,167,69,0.1)',
                        tension: 0.4,
                        fill: true
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: false,
                        grid: {
                            color: 'rgba(0,0,0,0.1)'
                        }
                    },
                    x: {
                        grid: {
                            color: 'rgba(0,0,0,0.1)'
                        }
                    }
                },
                plugins: {
                    legend: {
                        position: 'top'
                    }
                }
            }
        });

        // Community Overview Chart
        const communityCtx = document.getElementById('communityChart').getContext('2d');
        new Chart(communityCtx, {
            type: 'doughnut',
            data: {
                labels: ['Contributors', 'Discourse Users', 'Slack Members', 'Open Issues'],
                datasets: [{
                    data: [
                        communityData.contributors,
                        communityData.discourse_users,
                        communityData.slack_members,
                        communityData.open_issues
                    ],
                    backgroundColor: [
                        '#007bff',
                        '#17a2b8',
                        '#6c757d',
                        '#ffc107'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    </script>
</body>
</html>'''
        return Template(template_str)
    
    def render_dashboard(self):
        """Render the complete dashboard."""
        print("Rendering community dashboard...")
        
        # Load data
        metrics = self.load_latest_metrics()
        df = self.load_historical_data()
        
        # Read the existing HTML file
        with open(self.output_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Extract organization members data
        org_members = metrics.get('github', {}).get('members_details', [])
        members_json = json.dumps(org_members)
        
        # Replace organization members data in JavaScript
        import re
        # Find and replace the organizationMembers array
        pattern = r'let organizationMembers = \[\];'
        replacement = f'let organizationMembers = {members_json};'
        html_content = re.sub(pattern, replacement, html_content)
        
        # Update metric values in the HTML
        # Update stars
        stars = metrics.get('github', {}).get('total_stars', 0)
        html_content = re.sub(r'<div class="metric-value"></div>', 
                             f'<div class="metric-value">{stars}</div>', 
                             html_content, count=1)
        
        # Update contributors  
        contributors = metrics.get('github', {}).get('unique_contributors', 0)
        html_content = re.sub(r'<div class="metric-value"></div>', 
                             f'<div class="metric-value">{contributors}</div>', 
                             html_content, count=1)
        
        # Update forks
        forks = metrics.get('github', {}).get('total_forks', 0)
        html_content = re.sub(r'<div class="metric-value"></div>', 
                             f'<div class="metric-value">{forks}</div>', 
                             html_content, count=1)
        
        # Update last updated time
        try:
            last_updated = datetime.fromisoformat(metrics['last_updated'].replace('Z', '+00:00'))
            last_updated_formatted = last_updated.strftime('%B %d, %Y at %I:%M %p UTC')
        except:
            last_updated_formatted = datetime.utcnow().strftime('%B %d, %Y at %I:%M %p UTC')
            
        pattern = r'Last updated: [^<]+'
        replacement = f'Last updated: {last_updated_formatted}'
        html_content = re.sub(pattern, replacement, html_content)
        
        # Write the updated HTML file
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"Dashboard updated successfully at {self.output_file}")
        print(f"Total GitHub Stars: {metrics.get('github', {}).get('total_stars', 0)}")
        print(f"Organization Members: {len(org_members)}")
        
        return str(self.output_file)


if __name__ == "__main__":
    renderer = DashboardRenderer()
    renderer.render_dashboard()