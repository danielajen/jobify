import sys
import os
# Add parent directory to Python path to resolve config import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# REMOVE SELENIUM - Use lightweight alternatives
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
from config import config
from database.models import db, Job
from urllib.parse import urljoin
import time
import random
import json
from jobspy import scrape_jobs  # Lightweight job scraping library

# Enhanced headers to mimic a real browser
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Cache-Control': 'max-age=0'
}

def make_lightweight_request(url, timeout=10):
    """Make lightweight HTTP request with retry logic"""
    try:
        response = requests.get(url, headers=HEADERS, timeout=timeout)
        response.raise_for_status()
        return response
    except requests.RequestException as e:
        print(f"Request failed for {url}: {e}")
        return None

def scrape_target_jobs():
    """Lightweight job scraping using jobspy and HTTP requests"""
    print("Starting lightweight job scraping...")
    jobs = []
    
    try:
        # Use jobspy for LinkedIn jobs (lightweight)
        print("Scraping LinkedIn jobs...")
        linkedin_jobs = scrape_jobs(
            site_name="linkedin",
            search_term="intern",
            location="United States",
            results_wanted=50
        )
        
        for job in linkedin_jobs:
            if is_intern_position(job.title):
                jobs.append({
                    'title': job.title,
                    'company': job.company,
                    'location': job.location,
                    'description': job.description,
                    'url': job.url,
                    'source': 'LinkedIn',
                    'posted_date': job.date_posted.isoformat() if job.date_posted else datetime.now().isoformat()
                })
        
        print(f"Scraped {len(jobs)} LinkedIn jobs")
        
        # Lightweight GitHub jobs scraping
        print("Scraping GitHub jobs...")
        github_jobs = scrape_github_jobs_lightweight()
        jobs.extend(github_jobs)
        
        # Lightweight Indeed jobs scraping
        print("Scraping Indeed jobs...")
        indeed_jobs = scrape_indeed_jobs_lightweight()
        jobs.extend(indeed_jobs)
        
        print(f"Total jobs scraped: {len(jobs)}")
        return jobs
        
    except Exception as e:
        print(f"Error in lightweight job scraping: {e}")
        return []

def scrape_github_jobs_lightweight():
    """Lightweight GitHub jobs scraping using HTTP requests"""
    jobs = []
    try:
        # GitHub Jobs API (deprecated but still works for some data)
        url = "https://jobs.github.com/positions.json?description=intern&location=United+States"
        response = make_lightweight_request(url)
        
        if response:
            data = response.json()
            for job in data[:30]:  # Limit to 30 jobs
                if is_intern_position(job.get('title', '')):
                    jobs.append({
                        'title': job.get('title', ''),
                        'company': job.get('company', ''),
                        'location': job.get('location', ''),
                        'description': job.get('description', ''),
                        'url': job.get('url', ''),
                        'source': 'GitHub',
                        'posted_date': job.get('created_at', datetime.now().isoformat())
                    })
        
        print(f"Scraped {len(jobs)} GitHub jobs")
        return jobs
        
    except Exception as e:
        print(f"Error scraping GitHub jobs: {e}")
        return []

def scrape_indeed_jobs_lightweight():
    """Lightweight Indeed jobs scraping using HTTP requests"""
    jobs = []
    try:
        # Use jobspy for Indeed (lightweight)
        indeed_jobs = scrape_jobs(
            site_name="indeed",
            search_term="intern",
            location="United States",
            results_wanted=30
        )
        
        for job in indeed_jobs:
            if is_intern_position(job.title):
                jobs.append({
                    'title': job.title,
                    'company': job.company,
                    'location': job.location,
                    'description': job.description,
                    'url': job.url,
                    'source': 'Indeed',
                    'posted_date': job.date_posted.isoformat() if job.date_posted else datetime.now().isoformat()
                })
        
        print(f"Scraped {len(jobs)} Indeed jobs")
        return jobs
        
    except Exception as e:
        print(f"Error scraping Indeed jobs: {e}")
        return []

def scrape_company_jobs(company):
    """Lightweight company-specific job scraping"""
    jobs = []
    try:
        # Use jobspy for company-specific jobs
        company_jobs = scrape_jobs(
            site_name="linkedin",
            search_term=f"{company} intern",
            location="United States",
            results_wanted=20
        )
        
        for job in company_jobs:
            if is_intern_position(job.title):
                jobs.append({
                    'title': job.title,
                    'company': job.company,
                    'location': job.location,
                    'description': job.description,
                    'url': job.url,
                    'source': f'LinkedIn-{company}',
                    'posted_date': job.date_posted.isoformat() if job.date_posted else datetime.now().isoformat()
                })
        
        print(f"Scraped {len(jobs)} jobs for {company}")
        return jobs
        
    except Exception as e:
        print(f"Error scraping company jobs for {company}: {e}")
        return []

def is_intern_position(title):
    """Check if job title indicates an intern position"""
    intern_keywords = ['intern', 'internship', 'co-op', 'coop', 'student']
    title_lower = title.lower()
    return any(keyword in title_lower for keyword in intern_keywords)

def save_jobs_to_db(jobs):
    """Save jobs to database with memory optimization"""
    try:
        # Process jobs in batches to reduce memory usage
        batch_size = 10
        saved_count = 0
        
        for i in range(0, len(jobs), batch_size):
            batch = jobs[i:i + batch_size]
            
            for job_data in batch:
                try:
                    # Check if job already exists
                    existing_job = Job.query.filter_by(
                        title=job_data['title'],
                        company=job_data['company'],
                        url=job_data['url']
                    ).first()
                    
                    if not existing_job:
                        job = Job(
                            title=job_data['title'],
                            company=job_data['company'],
                            location=job_data['location'],
                            description=job_data['description'],
                            url=job_data['url'],
                            source=job_data['source'],
                            posted_date=datetime.fromisoformat(job_data['posted_date'])
                        )
                        db.session.add(job)
                        saved_count += 1
                        
                except Exception as e:
                    print(f"Error saving job {job_data.get('title', 'Unknown')}: {e}")
                    continue
            
            # Commit batch to reduce memory usage
            db.session.commit()
            print(f"Saved batch of {len(batch)} jobs")
            
            # Small delay to prevent overwhelming the database
            time.sleep(0.1)
        
        print(f"Total jobs saved: {saved_count}")
        return saved_count
        
    except Exception as e:
        print(f"Error in save_jobs_to_db: {e}")
        db.session.rollback()
        return 0