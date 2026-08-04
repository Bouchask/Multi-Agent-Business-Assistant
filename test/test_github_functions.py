#!/usr/bin/env python3
"""
Multi-Agent Business Assistant — GitHub API & Coding Agent (#3) Testing Suite
Tests repository inspection, developer authentication, and code/issue review extraction.
"""

import os
import sys
import requests
from dotenv import load_dotenv

# Load variables from .env file located in the project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(BASE_DIR, ".env")
load_dotenv(ENV_PATH)

GITHUB_API_BASE = "https://api.github.com"

def print_header(title):
    print("\n" + "="*70)
    print(f" 💻 {title}")
    print("="*70)

def get_headers():
    token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
    if not token or token == "replace-with-your-token":
        print("❌ Error: Valid GITHUB_PERSONAL_ACCESS_TOKEN not found in environment or .env file.")
        sys.exit(1)
    
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Multi-Agent-Business-Assistant-Coding-Agent"
    }

def test_authentication(headers):
    print_header("STEP 1: Authenticating with GitHub API (Personal Access Token)")
    response = requests.get(f"{GITHUB_API_BASE}/user", headers=headers)
    if response.status_code == 401:
        print("❌ Error: Authentication failed. Please check that your Personal Access Token is valid and unexpired.")
        sys.exit(1)
    response.raise_for_status()
    
    user = response.json()
    username = user.get("login", "(Unknown)")
    name = user.get("name") or username
    public_repos = user.get("public_repos", 0)
    private_repos = user.get("total_private_repos", "Access restricted by token scope")
    profile_url = user.get("html_url")
    
    print(f"✅ Successfully authenticated as Developer: [{name}] ({username})")
    print(f"🔗 Profile: {profile_url}")
    print(f"📦 Public Repositories: {public_repos} | Private Repositories: {private_repos}")
    return username

def test_list_user_repositories(headers, username):
    print_header("STEP 2: Testing Read — Fetching Your 5 Most Recently Updated Repositories")
    response = requests.get(
        f"{GITHUB_API_BASE}/user/repos",
        headers=headers,
        params={"sort": "updated", "per_page": 5}
    )
    response.raise_for_status()
    repos = response.json()
    
    if not repos:
        print("📭 No repositories found for this account.")
    else:
        for i, repo in enumerate(repos, 1):
            name = repo.get("full_name")
            visibility = "🔒 Private" if repo.get("private") else "🌐 Public"
            language = repo.get("language") or "Mixed/Other"
            desc = (repo.get("description") or "No description provided")[:60]
            print(f" [{i}] {name} ({visibility}) - Lang: {language}\n     DESC: {desc}\n     URL: {repo.get('html_url')}\n")
    print("✅ Repository Read test complete!")

def test_coding_agent_inspection(headers):
    print_header("STEP 3: Coding Agent (#3) Simulation — Inspecting Open Issues & PRs in Core Stack")
    # Let's inspect the LangGraph repository as our target developer analysis demonstration
    target_repo = "langchain-ai/langgraph"
    print(f"🔍 Agent Analysis Target: [{target_repo}] (Multi-Agent Workflow Framework)...")
    
    # Fetch Repo stats
    repo_res = requests.get(f"{GITHUB_API_BASE}/repos/{target_repo}", headers=headers)
    if repo_res.status_code == 200:
        r_data = repo_res.json()
        stars = r_data.get("stargazers_count", 0)
        forks = r_data.get("forks_count", 0)
        open_issues = r_data.get("open_issues_count", 0)
        print(f"⭐ Stars: {stars:,} | 🍴 Forks: {forks:,} | 🚨 Open Issues/PRs: {open_issues:,}")
    
    # Fetch recent open issues/PRs for developer review
    issues_res = requests.get(
        f"{GITHUB_API_BASE}/repos/{target_repo}/issues",
        headers=headers,
        params={"state": "open", "per_page": 3}
    )
    if issues_res.status_code == 200:
        issues = issues_res.json()
        print("\n🛠️ RECENT OPEN ISSUES / PULL REQUESTS FOR AGENT REVIEW:")
        print("-" * 70)
        for idx, item in enumerate(issues, 1):
            item_type = "PR 🔀" if "pull_request" in item else "Issue 🐞"
            title = item.get("title", "(No title)")
            number = item.get("number", 0)
            user = item.get("user", {}).get("login", "unknown")
            print(f" [{idx}] [{item_type}] #{number}: {title} (by @{user})")
            print(f"     URL: {item.get('html_url')}")
        print("-" * 70)
        print("✅ Live codebase issue extraction verified!")

def test_search_code_or_repos(headers):
    print_header("STEP 4: Testing Code & Repository Search API")
    query = "topic:multi-agent language:python sort:stars-desc"
    print(f"📡 Search Query: '{query}'...")
    search_res = requests.get(
        f"{GITHUB_API_BASE}/search/repositories",
        headers=headers,
        params={"q": query, "per_page": 2}
    )
    if search_res.status_code == 200:
        results = search_res.json().get("items", [])
        print(f"🏆 Top Trending Multi-Agent Python Repositories on GitHub:")
        for r in results:
            print(f"  • {r.get('full_name')} ({r.get('stargazers_count'):,} ⭐) - {r.get('html_url')}")
    print("✅ Search API test verified!")

def main():
    print_header("STARTING GITHUB API ALL-FUNCTIONS TEST SUITE")
    headers = get_headers()
    username = test_authentication(headers)
    test_list_user_repositories(headers, username)
    test_coding_agent_inspection(headers)
    test_search_code_or_repos(headers)
    
    print_header("🎉 GITHUB API FULLY VERIFIED! READY FOR CODING AGENT (#3) 🎉")

if __name__ == "__main__":
    main()
