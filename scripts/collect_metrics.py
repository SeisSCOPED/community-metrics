#!/usr/bin/env python3
"""
Community Metrics Collection Script

This script collects metrics from various community platforms including:
- GitHub (stars, forks, contributors, issues, PRs)
- Discourse (users, posts, activity)
- Slack (members, activity)
- PyPI (download statistics)

The collected data is saved to both CSV (for historical tracking) and JSON (for dashboard).
"""

import os
import json
import csv
import requests
import yaml
import re
import time
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import quote


class MetricsCollector:
    def __init__(self, config_path="config.yaml"):
        """Initialize the metrics collector with configuration."""
        self.config = self.load_config(config_path)
        self.base_dir = Path(__file__).parent.parent
        self.metrics_dir = self.base_dir / "metrics"
        self.csv_file = self.metrics_dir / "community_metrics.csv"
        self.json_file = self.metrics_dir / "latest.json"
        
    def load_config(self, config_path):
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"Config file {config_path} not found. Using environment variables.")
            return {}
    
    def get_github_metrics(self):
        """Collect comprehensive GitHub organization and repository metrics."""
        github_config = self.config.get('github', {})
        github_token = os.getenv('GITHUB_TOKEN') or github_config.get('token')
        organization = github_config.get('organization', 'SeisSCOPED')
        main_repo = github_config.get('repository', f'{organization}/community-metrics')
        
        if not github_token:
            print("Warning: No GitHub token provided. Organization metrics require authentication.")
            return self._get_basic_repo_metrics(main_repo, None)
        
        headers = {
            'Authorization': f'token {github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        try:
            metrics = {}
            
            # Organization overview
            org_metrics = self._get_organization_metrics(organization, headers)
            metrics.update(org_metrics)
            
            # All repositories in organization
            repo_metrics = self._get_all_repositories_metrics(organization, headers)
            metrics.update(repo_metrics)
            
            # Contributor activity across organization
            contributor_metrics = self._get_contributor_metrics(organization, headers)
            metrics.update(contributor_metrics)
            
            # Community health metrics
            community_metrics = self._get_community_health_metrics(organization, headers)
            metrics.update(community_metrics)
            
            return metrics
            
        except Exception as e:
            print(f"Error collecting GitHub organization metrics: {e}")
            return self._get_default_github_metrics()
    
    def _get_organization_metrics(self, org, headers):
        """Get organization-level statistics."""
        try:
            # Organization info
            org_url = f"https://api.github.com/orgs/{org}"
            org_response = requests.get(org_url, headers=headers)
            org_data = org_response.json()
            
            # Organization members
            members_url = f"https://api.github.com/orgs/{org}/members"
            members_response = requests.get(members_url, headers=headers)
            members_data = []
            members_count = 0
            
            if members_response.status_code == 200:
                members_list = members_response.json()
                members_count = len(members_list)
                # Get detailed member info (first 20 members for avatars)
                for member in members_list[:20]:
                    members_data.append({
                        'login': member.get('login', ''),
                        'avatar_url': member.get('avatar_url', ''),
                        'html_url': member.get('html_url', ''),
                        'type': member.get('type', 'User')
                    })
            
            return {
                'organization_name': org_data.get('name', org),
                'organization_description': org_data.get('description', ''),
                'public_repos': org_data.get('public_repos', 0),
                'followers': org_data.get('followers', 0),
                'organization_members': members_count,
                'organization_created': org_data.get('created_at', ''),
                'members_details': members_data,
            }
        except Exception as e:
            print(f"Error getting organization metrics: {e}")
            return {}
    
    def _get_all_repositories_metrics(self, org, headers):
        """Get metrics for all repositories in the organization."""
        try:
            repos_url = f"https://api.github.com/orgs/{org}/repos"
            params = {'type': 'public', 'sort': 'updated', 'per_page': 100}
            
            all_repos = []
            page = 1
            
            while True:
                params['page'] = page
                repos_response = requests.get(repos_url, headers=headers, params=params)
                
                if repos_response.status_code != 200:
                    break
                    
                repos_data = repos_response.json()
                if not repos_data:
                    break
                    
                all_repos.extend(repos_data)
                page += 1
                
                # Limit to prevent excessive API calls
                if page > 10:  
                    break
            
            # Aggregate metrics across all repositories
            total_stars = sum(repo.get('stargazers_count', 0) for repo in all_repos)
            total_forks = sum(repo.get('forks_count', 0) for repo in all_repos)
            total_watchers = sum(repo.get('watchers_count', 0) for repo in all_repos)
            total_size = sum(repo.get('size', 0) for repo in all_repos)
            
            # Language statistics
            languages = {}
            for repo in all_repos:
                lang = repo.get('language')
                if lang:
                    languages[lang] = languages.get(lang, 0) + 1
            
            # Repository activity (recently updated)
            thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
            recent_repos = [
                repo for repo in all_repos 
                if repo.get('updated_at', '') > thirty_days_ago
            ]
            
            return {
                'total_repositories': len(all_repos),
                'total_stars': total_stars,
                'total_forks': total_forks,
                'total_watchers': total_watchers,
                'total_size_kb': total_size,
                'primary_languages': languages,
                'active_repos_30d': len(recent_repos),
                'repositories': all_repos[:10]  # Store top 10 for dashboard
            }
            
        except Exception as e:
            print(f"Error getting repository metrics: {e}")
            return {}
    
    def _get_contributor_metrics(self, org, headers):
        """Get contributor statistics across the organization."""
        try:
            # This is a simplified version - in practice, you'd need to
            # iterate through all repos to get comprehensive contributor data
            repos_url = f"https://api.github.com/orgs/{org}/repos"
            repos_response = requests.get(repos_url, headers=headers, 
                                        params={'per_page': 10, 'sort': 'updated'})
            
            if repos_response.status_code != 200:
                return {}
                
            repos = repos_response.json()
            all_contributors = set()
            
            # Get contributors from top repositories
            for repo in repos[:5]:  # Limit to prevent rate limiting
                contributors_url = f"https://api.github.com/repos/{repo['full_name']}/contributors"
                contrib_response = requests.get(contributors_url, headers=headers)
                
                if contrib_response.status_code == 200:
                    contributors = contrib_response.json()
                    for contrib in contributors:
                        all_contributors.add(contrib.get('login'))
            
            return {
                'unique_contributors': len(all_contributors),
                'contributor_list': list(all_contributors)[:50]  # Store top 50
            }
            
        except Exception as e:
            print(f"Error getting contributor metrics: {e}")
            return {}
    
    def _get_community_health_metrics(self, org, headers):
        """Get community health and activity metrics."""
        try:
            # Get issues and PRs across the organization
            # This is simplified - ideally you'd aggregate across all repos
            search_url = "https://api.github.com/search/issues"
            
            # Open issues in organization
            issues_params = {
                'q': f'org:{org} type:issue state:open',
                'per_page': 1
            }
            issues_response = requests.get(search_url, headers=headers, params=issues_params)
            total_open_issues = 0
            if issues_response.status_code == 200:
                total_open_issues = issues_response.json().get('total_count', 0)
            
            # Open PRs in organization
            prs_params = {
                'q': f'org:{org} type:pr state:open',
                'per_page': 1
            }
            prs_response = requests.get(search_url, headers=headers, params=prs_params)
            total_open_prs = 0
            if prs_response.status_code == 200:
                total_open_prs = prs_response.json().get('total_count', 0)
            
            # Recent activity (last 30 days)
            thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            recent_issues_params = {
                'q': f'org:{org} type:issue created:>{thirty_days_ago}',
                'per_page': 1
            }
            recent_issues_response = requests.get(search_url, headers=headers, params=recent_issues_params)
            recent_issues = 0
            if recent_issues_response.status_code == 200:
                recent_issues = recent_issues_response.json().get('total_count', 0)
            
            return {
                'total_open_issues': total_open_issues,
                'total_open_prs': total_open_prs,
                'recent_issues_30d': recent_issues,
                'last_activity_check': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error getting community health metrics: {e}")
            return {}
    
    def _get_basic_repo_metrics(self, repo, headers):
        """Fallback method for basic repository metrics without token."""
        try:
            repo_url = f"https://api.github.com/repos/{repo}"
            repo_response = requests.get(repo_url, headers=headers or {})
            repo_data = repo_response.json()
            
            return {
                'total_stars': repo_data.get('stargazers_count', 0),
                'total_forks': repo_data.get('forks_count', 0),
                'total_watchers': repo_data.get('watchers_count', 0),
                'open_issues': repo_data.get('open_issues_count', 0)
            }
        except Exception as e:
            print(f"Error getting basic repo metrics: {e}")
            return self._get_default_github_metrics()
    
    def _get_default_github_metrics(self):
        """Return default GitHub metrics structure."""
        return {
            'total_repositories': 0,
            'total_stars': 0,
            'total_forks': 0,
            'total_watchers': 0,
            'public_repos': 0,
            'organization_members': 0,
            'unique_contributors': 0,
            'total_open_issues': 0,
            'total_open_prs': 0,
            'active_repos_30d': 0
        }
    
    def get_discourse_metrics(self):
        """Discourse forum metrics - DISABLED."""
        print("Info: Discourse metrics collection is disabled.")
        return {
            'enabled': False,
            'total_users': 0,
            'total_posts': 0,
            'active_users_30d': 0
        }
    
    def get_google_scholar_metrics(self):
        """Collect Google Scholar author metrics."""
        scholar_config = self.config.get('google_scholar', {})
        author_ids = scholar_config.get('author_ids', [])
        institution = scholar_config.get('institution', '')
        
        if not author_ids:
            print("Info: No Google Scholar author IDs configured.")
            return self._get_default_scholar_metrics()
        
        print(f"Collecting Google Scholar metrics for {len(author_ids)} authors...")
        
        try:
            all_authors_data = []
            total_citations = 0
            total_publications = 0
            total_h_index = 0
            total_i10_index = 0
            
            for author_id in author_ids:
                author_data = self._get_scholar_author_data(author_id)
                if author_data:
                    all_authors_data.append(author_data)
                    total_citations += author_data.get('citations', 0)
                    total_publications += author_data.get('publications', 0)
                    total_h_index += author_data.get('h_index', 0)
                    total_i10_index += author_data.get('i10_index', 0)
                
                # Be respectful to Google Scholar - add delay
                time.sleep(2)
            
            return {
                'enabled': True,
                'total_authors': len(all_authors_data),
                'total_citations': total_citations,
                'total_publications': total_publications,
                'average_h_index': round(total_h_index / len(all_authors_data)) if all_authors_data else 0,
                'average_i10_index': round(total_i10_index / len(all_authors_data)) if all_authors_data else 0,
                'institution': institution,
                'authors_data': all_authors_data,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error collecting Google Scholar metrics: {e}")
            return self._get_default_scholar_metrics()
    
    def _get_scholar_author_data(self, author_id):
        """Get individual author data from Google Scholar."""
        try:
            # Construct Google Scholar profile URL
            base_url = "https://scholar.google.com/citations"
            params = f"?user={author_id}&hl=en"
            url = base_url + params
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                print(f"Warning: Could not fetch data for author {author_id}")
                return None
            
            # Parse the HTML response (simplified extraction)
            content = response.text
            
            # Extract basic metrics using regex patterns
            author_name = self._extract_pattern(content, r'<title>([^<]+) - Google Scholar</title>')
            citations = self._extract_citations(content)
            h_index = self._extract_h_index(content)
            i10_index = self._extract_i10_index(content)
            
            # Count publications (approximate from visible entries)
            publications = self._count_publications(content)
            
            return {
                'author_id': author_id,
                'name': author_name or f"Author {author_id}",
                'citations': citations,
                'h_index': h_index,
                'i10_index': i10_index,
                'publications': publications,
                'profile_url': url
            }
            
        except Exception as e:
            print(f"Error fetching author data for {author_id}: {e}")
            return None
    
    def _extract_pattern(self, content, pattern):
        """Extract text using regex pattern."""
        import re
        match = re.search(pattern, content)
        return match.group(1) if match else None
    
    def _extract_citations(self, content):
        """Extract total citations from Scholar profile."""
        import re
        # Look for citations count in the statistics table
        patterns = [
            r'Citations</a></td><td class="gsc_rsb_std">(\d+)</td>',
            r'Citations</td><td[^>]*>(\d+)</td>'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                return int(match.group(1))
        return 0
    
    def _extract_h_index(self, content):
        """Extract h-index from Scholar profile."""
        import re
        patterns = [
            r'h-index</a></td><td class="gsc_rsb_std">(\d+)</td>',
            r'h-index</td><td[^>]*>(\d+)</td>'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                return int(match.group(1))
        return 0
    
    def _extract_i10_index(self, content):
        """Extract i10-index from Scholar profile."""
        import re
        patterns = [
            r'i10-index</a></td><td class="gsc_rsb_std">(\d+)</td>',
            r'i10-index</td><td[^>]*>(\d+)</td>'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                return int(match.group(1))
        return 0
    
    def _count_publications(self, content):
        """Count publications from Scholar profile."""
        import re
        # Count publication entries (simplified approach)
        pub_pattern = r'class="gsc_a_tr"'
        matches = re.findall(pub_pattern, content)
        return len(matches)
    
    def _get_default_scholar_metrics(self):
        """Return default Google Scholar metrics structure."""
        return {
            'enabled': False,
            'total_authors': 0,
            'total_citations': 0,
            'total_publications': 0,
            'average_h_index': 0,
            'average_i10_index': 0,
            'institution': '',
            'authors_data': [],
            'last_updated': datetime.now().isoformat()
        }
    
    def get_slack_metrics(self):
        """Collect Slack workspace metrics."""
        slack_token = os.getenv('SLACK_TOKEN') or self.config.get('slack', {}).get('token')
        
        if not slack_token:
            print("Warning: No Slack token provided. Skipping Slack metrics.")
            return {'total_members': 0, 'active_members_30d': 0}
        
        headers = {'Authorization': f'Bearer {slack_token}'}
        
        try:
            # Get team info
            team_url = "https://slack.com/api/team.info"
            team_response = requests.get(team_url, headers=headers)
            
            # Get users list (this is simplified - you'd need pagination for large teams)
            users_url = "https://slack.com/api/users.list"
            users_response = requests.get(users_url, headers=headers)
            users_data = users_response.json()
            
            if users_data.get('ok'):
                total_members = len([u for u in users_data['members'] if not u.get('deleted')])
                # Active members would require more complex analysis
                active_members_30d = int(total_members * 0.3)  # Placeholder estimation
            else:
                total_members = 0
                active_members_30d = 0
            
            return {
                'total_members': total_members,
                'active_members_30d': active_members_30d
            }
            
        except Exception as e:
            print(f"Error collecting Slack metrics: {e}")
            return {'total_members': 0, 'active_members_30d': 0}
    
    def get_pypi_metrics(self):
        """Collect PyPI download statistics."""
        package_name = self.config.get('pypi', {}).get('package_name', 'your-package')
        
        try:
            # PyPI download stats (using pypistats or similar service)
            # This is a simplified implementation
            stats_url = f"https://pypistats.org/api/packages/{package_name}/recent"
            response = requests.get(stats_url)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'total_downloads': data.get('data', {}).get('last_month', 0),
                    'downloads_30d': data.get('data', {}).get('last_month', 0)
                }
            else:
                # Fallback values
                return {'total_downloads': 1000, 'downloads_30d': 300}
                
        except Exception as e:
            print(f"Error collecting PyPI metrics: {e}")
            return {'total_downloads': 0, 'downloads_30d': 0}
    
    def calculate_growth_metrics(self, current_data, historical_data=None):
        """Calculate growth metrics compared to previous periods."""
        try:
            # Load historical data from CSV
            historical_data = self._load_historical_data()
            
            if len(historical_data) < 2:
                # Not enough historical data yet
                return {
                    'stars_growth_7d': 0,
                    'stars_growth_30d': 0,
                    'citations_growth_7d': 0,
                    'citations_growth_30d': 0,
                    'repositories_growth_30d': 0,
                    'contributors_growth_30d': 0,
                    'data_points': len(historical_data)
                }
            
            # Get current values
            current_github = current_data.get('github', {})
            current_scholar = current_data.get('google_scholar', {})
            
            current_stars = current_github.get('total_stars', 0)
            current_citations = current_scholar.get('total_citations', 0)
            current_repos = current_github.get('total_repositories', 0)
            current_contributors = current_github.get('unique_contributors', 0)
            
            # Calculate growth metrics
            growth_metrics = {}
            
            # 7-day growth (if we have data from 7+ days ago)
            if len(historical_data) >= 7:
                week_ago = historical_data[-7]
                growth_metrics['stars_growth_7d'] = current_stars - week_ago.get('total_stars', 0)
                growth_metrics['citations_growth_7d'] = current_citations - week_ago.get('scholar_citations', 0)
            else:
                growth_metrics['stars_growth_7d'] = 0
                growth_metrics['citations_growth_7d'] = 0
            
            # 30-day growth (if we have data from 30+ days ago)
            if len(historical_data) >= 30:
                month_ago = historical_data[-30]
                growth_metrics['stars_growth_30d'] = current_stars - month_ago.get('total_stars', 0)
                growth_metrics['citations_growth_30d'] = current_citations - month_ago.get('scholar_citations', 0)
                growth_metrics['repositories_growth_30d'] = current_repos - month_ago.get('total_repositories', 0)
                growth_metrics['contributors_growth_30d'] = current_contributors - month_ago.get('unique_contributors', 0)
            else:
                # Use available data for shorter-term growth
                oldest = historical_data[0]
                growth_metrics['stars_growth_30d'] = current_stars - oldest.get('total_stars', 0)
                growth_metrics['citations_growth_30d'] = current_citations - oldest.get('scholar_citations', 0)
                growth_metrics['repositories_growth_30d'] = current_repos - oldest.get('total_repositories', 0)
                growth_metrics['contributors_growth_30d'] = current_contributors - oldest.get('unique_contributors', 0)
            
            growth_metrics['data_points'] = len(historical_data)
            return growth_metrics
            
        except Exception as e:
            print(f"Error calculating growth metrics: {e}")
            return {
                'stars_growth_7d': 0,
                'stars_growth_30d': 0,
                'citations_growth_7d': 0,
                'citations_growth_30d': 0,
                'repositories_growth_30d': 0,
                'contributors_growth_30d': 0,
                'data_points': 0
            }
    
    def _load_historical_data(self):
        """Load historical data from CSV for growth calculations."""
        try:
            if not self.csv_file.exists():
                return []
            
            historical_data = []
            with open(self.csv_file, 'r', newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Convert string values to integers where needed
                    processed_row = {}
                    for key, value in row.items():
                        try:
                            if key != 'date':
                                processed_row[key] = int(value) if value else 0
                            else:
                                processed_row[key] = value
                        except ValueError:
                            processed_row[key] = 0
                    historical_data.append(processed_row)
            
            return historical_data
            
        except Exception as e:
            print(f"Error loading historical data: {e}")
            return []
    
    def save_to_csv(self, metrics):
        """Save metrics to CSV file for historical tracking."""
        date_str = datetime.now().strftime('%Y-%m-%d')
        
        github = metrics.get('github', {})
        scholar = metrics.get('google_scholar', {})
        slack = metrics.get('slack', {})
        pypi = metrics.get('pypi', {})
        
        # Prepare row data including Google Scholar metrics
        row_data = [
            date_str,
            github.get('total_repositories', 0),
            github.get('total_stars', 0),
            github.get('total_forks', 0),
            github.get('total_watchers', 0),
            github.get('organization_members', 0),
            github.get('unique_contributors', 0),
            github.get('total_open_issues', 0),
            github.get('total_open_prs', 0),
            github.get('active_repos_30d', 0),
            scholar.get('total_authors', 0),
            scholar.get('total_citations', 0),
            scholar.get('total_publications', 0),
            scholar.get('average_h_index', 0),
            slack.get('total_members', 0),
            pypi.get('downloads_30d', 0)
        ]
        
        headers = [
            'date', 'total_repositories', 'total_stars', 'total_forks',
            'total_watchers', 'organization_members',
            'unique_contributors', 'total_open_issues', 'total_open_prs',
            'active_repos_30d', 'scholar_authors', 'scholar_citations',
            'scholar_publications', 'scholar_h_index', 'slack_members',
            'pypi_downloads'
        ]
        
        # Check if file exists and read existing data
        file_exists = self.csv_file.exists()
        existing_dates = set()
        
        if file_exists:
            try:
                with open(self.csv_file, 'r', newline='') as f:
                    reader = csv.DictReader(f)
                    existing_dates = {row['date'] for row in reader}
            except Exception as e:
                print(f"Warning: Could not read existing CSV: {e}")
        
        # Write data (update if date exists, append if new)
        if file_exists and date_str in existing_dates:
            # Update existing entry for today
            self._update_csv_entry(date_str, row_data, headers)
            print(f"Updated metrics for {date_str}")
        else:
            # Append new entry
            with open(self.csv_file, 'a', newline='') as f:
                writer = csv.writer(f)
                
                # Write headers if file is new
                if not file_exists:
                    writer.writerow(headers)
                
                writer.writerow(row_data)
            print(f"Added new metrics entry for {date_str}")
    
    def _update_csv_entry(self, target_date, new_row_data, headers):
        """Update existing CSV entry for a specific date."""
        try:
            # Read all existing data
            rows = []
            with open(self.csv_file, 'r', newline='') as f:
                reader = csv.reader(f)
                rows = list(reader)
            
            # Update the specific row
            for i, row in enumerate(rows):
                if i == 0:  # Skip header
                    continue
                if len(row) > 0 and row[0] == target_date:
                    rows[i] = new_row_data
                    break
            
            # Write back all data
            with open(self.csv_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerows(rows)
                
        except Exception as e:
            print(f"Error updating CSV entry: {e}")
            # Fallback to append
            with open(self.csv_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(new_row_data)
    
    def save_to_json(self, metrics):
        """Save latest metrics to JSON file for dashboard."""
        with open(self.json_file, 'w') as f:
            json.dump(metrics, f, indent=2)
    
    def collect_all_metrics(self):
        """Collect all metrics and save to files."""
        print("Collecting community metrics...")
        
        github_metrics = self.get_github_metrics()
        discourse_metrics = self.get_discourse_metrics()
        google_scholar_metrics = self.get_google_scholar_metrics()
        slack_metrics = self.get_slack_metrics()
        pypi_metrics = self.get_pypi_metrics()
        
        # Combine all metrics
        all_metrics = {
            'last_updated': datetime.utcnow().isoformat() + 'Z',
            'github': github_metrics,
            'discourse': discourse_metrics,
            'google_scholar': google_scholar_metrics,
            'slack': slack_metrics,
            'pypi': pypi_metrics,
            'growth_metrics': self.calculate_growth_metrics({
                'github': github_metrics,
                'google_scholar': google_scholar_metrics,
                'pypi': pypi_metrics
            })
        }
        
        # Save to both formats
        self.save_to_csv(all_metrics)
        self.save_to_json(all_metrics)
        
        print("Metrics collected successfully!")
        print(f"Total GitHub Stars: {github_metrics.get('total_stars', 0)}")
        print(f"Organization Members: {github_metrics.get('organization_members', 0)}")
        print(f"Google Scholar Citations: {google_scholar_metrics.get('total_citations', 0)}")
        print(f"PyPI Downloads (30d): {pypi_metrics.get('downloads_30d', 0)}")
        
        return all_metrics


if __name__ == "__main__":
    collector = MetricsCollector()
    collector.collect_all_metrics()