import sys
import os
# Add parent directory to Python path to resolve config import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# REMOVE SELENIUM AND JOBSPY - Use lightweight HTTP requests only
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
    """Ultra-lightweight job scraping using only HTTP requests"""
    print("Starting ultra-lightweight job scraping...")
    jobs = []
    
    try:
        # Lightweight GitHub jobs scraping
        print("Scraping GitHub jobs...")
        github_jobs = scrape_github_jobs_lightweight()
        jobs.extend(github_jobs)
        
        # Lightweight Indeed jobs scraping (using API)
        print("Scraping Indeed jobs...")
        indeed_jobs = scrape_indeed_jobs_lightweight()
        jobs.extend(indeed_jobs)
        
        # Lightweight LinkedIn jobs scraping (using API)
        print("Scraping LinkedIn jobs...")
        linkedin_jobs = scrape_linkedin_jobs_lightweight()
        jobs.extend(linkedin_jobs)
        
        print(f"Total jobs scraped: {len(jobs)}")
        return jobs
        
    except Exception as e:
        print(f"Error in ultra-lightweight job scraping: {e}")
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
        # Use Indeed's RSS feed for lightweight scraping
        url = "https://www.indeed.com/rss?q=intern&l=United+States"
        response = make_lightweight_request(url)
        
        if response:
            soup = BeautifulSoup(response.content, 'xml')
            items = soup.find_all('item')
            
            for item in items[:30]:  # Limit to 30 jobs
                title = item.find('title')
                if title and is_intern_position(title.text):
                    jobs.append({
                        'title': title.text,
                        'company': 'Various Companies',  # RSS doesn't always have company
                        'location': 'United States',
                        'description': item.find('description').text if item.find('description') else '',
                        'url': item.find('link').text if item.find('link') else '',
                        'source': 'Indeed',
                        'posted_date': item.find('pubDate').text if item.find('pubDate') else datetime.now().isoformat()
                    })
        
        print(f"Scraped {len(jobs)} Indeed jobs")
        return jobs
        
    except Exception as e:
        print(f"Error scraping Indeed jobs: {e}")
        return []

def scrape_linkedin_jobs_lightweight():
    """Lightweight LinkedIn jobs scraping using HTTP requests"""
    jobs = []
    try:
        # Use LinkedIn's job search page (basic scraping)
        url = "https://www.linkedin.com/jobs/search/?keywords=intern&location=United%20States"
        response = make_lightweight_request(url)
        
        if response:
            soup = BeautifulSoup(response.content, 'html.parser')
            job_cards = soup.find_all('div', class_='job-search-card')
            
            for card in job_cards[:30]:  # Limit to 30 jobs
                title_elem = card.find('h3', class_='job-search-card__title')
                company_elem = card.find('h4', class_='job-search-card__subtitle')
                location_elem = card.find('span', class_='job-search-card__location')
                
                if title_elem and is_intern_position(title_elem.text.strip()):
                    jobs.append({
                        'title': title_elem.text.strip(),
                        'company': company_elem.text.strip() if company_elem else 'Unknown Company',
                        'location': location_elem.text.strip() if location_elem else 'United States',
                        'description': '',
                        'url': f"https://www.linkedin.com{card.find('a')['href']}" if card.find('a') else '',
                        'source': 'LinkedIn',
                        'posted_date': datetime.now().isoformat()
                    })
        
        print(f"Scraped {len(jobs)} LinkedIn jobs")
        return jobs
        
    except Exception as e:
        print(f"Error scraping LinkedIn jobs: {e}")
        return []

def scrape_company_jobs(company):
    """Lightweight company-specific job scraping"""
    jobs = []
    try:
        # Simple company job search using HTTP requests
        search_url = f"https://www.linkedin.com/jobs/search/?keywords={company}%20intern&location=United%20States"
        response = make_lightweight_request(search_url)
        
        if response:
            soup = BeautifulSoup(response.content, 'html.parser')
            job_cards = soup.find_all('div', class_='job-search-card')
            
            for card in job_cards[:20]:  # Limit to 20 jobs
                title_elem = card.find('h3', class_='job-search-card__title')
                company_elem = card.find('h4', class_='job-search-card__subtitle')
                location_elem = card.find('span', class_='job-search-card__location')
                
                if title_elem and is_intern_position(title_elem.text.strip()):
                    jobs.append({
                        'title': title_elem.text.strip(),
                        'company': company_elem.text.strip() if company_elem else company,
                        'location': location_elem.text.strip() if location_elem else 'United States',
                        'description': '',
                        'url': f"https://www.linkedin.com{card.find('a')['href']}" if card.find('a') else '',
                        'source': f'LinkedIn-{company}',
                        'posted_date': datetime.now().isoformat()
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