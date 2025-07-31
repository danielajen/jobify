import sys
import os
# Add parent directory to Python path to resolve config import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
from config import config
from database.models import db, Job
from urllib.parse import urljoin, urlparse
import time
import random
import json

# Enhanced headers to mimic a real browser
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
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
    """Scrape jobs from sources for general swiping (Glassdoor, BuiltIn, GitHub)"""
    print("Starting general job scraping for swiping (Glassdoor, BuiltIn, GitHub)...")
    jobs = []
    
    try:
        # 1. Scrape from GitHub internships markdown - LIMIT to 15 jobs
        print("Scraping GitHub internships (LIMITED)...")
        github_jobs = scrape_github_internships()
        jobs.extend(github_jobs[:15])  # Limit to 15
        
        # 2. Scrape from Glassdoor - LIMIT to 15 jobs
        print("Scraping Glassdoor (LIMITED)...")
        glassdoor_jobs = scrape_glassdoor_jobs()
        jobs.extend(glassdoor_jobs[:15])  # Limit to 15
        
        # 3. Scrape from BuiltIn - LIMIT to 15 jobs
        print("Scraping BuiltIn (LIMITED)...")
        builtin_jobs = scrape_builtin_jobs()
        jobs.extend(builtin_jobs[:15])  # Limit to 15
        
        print(f"Total jobs scraped from sources for swiping: {len(jobs)}")
        return jobs
        
    except Exception as e:
        print(f"Error in target job scraping: {e}")
        return []

def scrape_favorite_companies_jobs():
    """Scrape jobs ONLY from favorite company career pages from config.py"""
    print("Starting favorite companies career page scraping (CAREER PAGES ONLY)...")
    jobs = []
    companies_scraped = 0
    
    try:
        # Get first 20 companies with career pages from config.py
        favorite_companies = config.FAVORITE_COMPANIES[:20]
        
        for company in favorite_companies:
            try:
                if company in config.COMPANY_CAREER_PAGES:
                    career_url = config.COMPANY_CAREER_PAGES[company]
                    if career_url and career_url.strip():  # Skip empty URLs
                        print(f"Scraping career page for: {company}")
                        company_jobs = scrape_single_company_career_page(company, career_url)
                        jobs.extend(company_jobs)
                        companies_scraped += 1
                        
                        # Fast delay to prevent overwhelming servers
                        time.sleep(0.3)
                        
                        # Stop after 20 companies or 40 jobs (keep under 715MB)
                        if companies_scraped >= 20 or len(jobs) >= 40:
                            print(f"Career page limit reached: {companies_scraped} companies, {len(jobs)} jobs")
                            break
                
            except Exception as e:
                print(f"Error scraping {company}: {e}")
                continue
        
        print(f"CAREER PAGES: Scraped {len(jobs)} jobs from {companies_scraped} favorite company career pages")
        return jobs
        
    except Exception as e:
        print(f"Error in favorite companies career page scraping: {e}")
        return []

def scrape_github_internships():
    """Scrape from GitHub internships markdown"""
    jobs = []
    try:
        url = config.SOURCES["github"]
        response = make_lightweight_request(url)
        
        if response:
            content = response.text
            # Parse markdown content for company names and links
            lines = content.split('\n')
            current_company = None
            
            for line in lines:
                # Look for company headers
                if line.startswith('## ') and '|' in line:
                    company_match = re.search(r'\|\s*\[([^\]]+)\]', line)
                    if company_match:
                        current_company = company_match.group(1).strip()
                
                # Look for job links
                elif line.startswith('- ') and '[' in line and '](' in line:
                    if current_company:
                        link_match = re.search(r'\[([^\]]+)\]\(([^)]+)\)', line)
                        if link_match:
                            title = link_match.group(1).strip()
                            url = link_match.group(2).strip()
                            
                            if is_intern_position(title):
                                jobs.append({
                                    'title': title,
                                    'company': current_company,
                                    'location': 'United States',
                                    'description': '',
                                    'url': url,
                                    'source': 'GitHub-Internships',
                                    'posted_at': datetime.now().isoformat()
                                })
        
        print(f"Scraped {len(jobs)} GitHub internships")
        return jobs
        
    except Exception as e:
        print(f"Error scraping GitHub internships: {e}")
        return []

def scrape_glassdoor_jobs():
    """Scrape from Glassdoor"""
    jobs = []
    try:
        url = config.SOURCES["glassdoor"]
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
                        'company': company_elem.text.strip() if company_elem else 'Unknown',
                        'location': location_elem.text.strip() if location_elem else 'United States',
                        'description': '',
                        'url': f"https://www.glassdoor.com{card.find('a')['href']}" if card.find('a') else '',
                        'source': 'Glassdoor',
                        'posted_at': datetime.now().isoformat()
                    })
        
        print(f"Scraped {len(jobs)} Glassdoor jobs")
        return jobs
        
    except Exception as e:
        print(f"Error scraping Glassdoor: {e}")
        return []

def scrape_builtin_jobs():
    """Scrape from BuiltIn"""
    jobs = []
    try:
        url = config.SOURCES["builtin"]
        response = make_lightweight_request(url)
        
        if response:
            soup = BeautifulSoup(response.content, 'html.parser')
            job_cards = soup.find_all('div', class_='job-card')
            
            for card in job_cards[:30]:  # Limit to 30 jobs
                title_elem = card.find('h3', class_='job-title')
                company_elem = card.find('div', class_='company-name')
                location_elem = card.find('div', class_='location')
                
                if title_elem and is_intern_position(title_elem.text.strip()):
                    jobs.append({
                        'title': title_elem.text.strip(),
                        'company': company_elem.text.strip() if company_elem else 'Unknown',
                        'location': location_elem.text.strip() if location_elem else 'United States',
                        'description': '',
                        'url': f"https://builtintoronto.com{card.find('a')['href']}" if card.find('a') else '',
                        'source': 'BuiltIn',
                        'posted_at': datetime.now().isoformat()
                    })
        
        print(f"Scraped {len(jobs)} BuiltIn jobs")
        return jobs
        
    except Exception as e:
        print(f"Error scraping BuiltIn: {e}")
        return []

def scrape_single_company_career_page(company, career_url):
    """Scrape jobs from a single company career page - IMPROVED with keywords"""
    jobs = []
    try:
        print(f"Scraping career page for: {company} at {career_url}")
        response = make_lightweight_request(career_url, timeout=15)
        
        if response:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # IMPROVED: Look for job links with keywords in href or text
            job_keywords = ['intern', 'internship', 'co-op', 'student', 'new grad', 'entry level', 'software', 'developer', 'engineer', '2026', '2027']
            
            # Method 1: Find all links that contain job keywords
            job_links = []
            for link in soup.find_all('a', href=True):
                href = link.get('href', '').lower()
                text = link.get_text(strip=True).lower()
                
                # Check if link contains job keywords
                for keyword in job_keywords:
                    if keyword in href or keyword in text:
                        job_links.append(link)
                        break
            
            # Method 2: Look for job cards/divs with keywords
            job_cards = []
            for div in soup.find_all(['div', 'article', 'section']):
                div_text = div.get_text(strip=True).lower()
                for keyword in job_keywords:
                    if keyword in div_text:
                        job_cards.append(div)
                        break
            
            # Method 3: Look for specific job-related classes
            job_selectors = [
                '.job-card', '.job-listing', '.career-opportunity', '.position',
                '.job-item', '.career-item', '.open-position', '.job-opening',
                '[class*="job"]', '[class*="career"]', '[class*="position"]',
                '[class*="intern"]', '[class*="internship"]'
            ]
            
            for selector in job_selectors:
                found_cards = soup.select(selector)
                if found_cards:
                    job_cards.extend(found_cards)
                    break
            
            # Process found job links
            for link in job_links[:10]:  # Limit to 10 jobs per company
                title = link.get_text(strip=True)
                if title and len(title) > 5:  # Valid title
                    job_url = urljoin(career_url, link.get('href', ''))
                    jobs.append({
                        'title': title,
                        'company': company,
                        'location': 'United States',
                        'description': f'Job at {company} - {title}',
                        'url': job_url,
                                                    'source': f'Career-{company}',
                            'posted_at': datetime.now().isoformat()
                    })
            
            # Process found job cards
            for card in job_cards[:10]:  # Limit to 10 jobs per company
                # Try to find title in card
                title_elem = card.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']) or card.find(['span', 'div'], class_=re.compile(r'title|name|position', re.I))
                
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    if title and len(title) > 5:  # Valid title
                        # Try to find job URL
                        job_link = card.find('a') or title_elem.find('a')
                        job_url = urljoin(career_url, job_link.get('href', '')) if job_link else career_url
                        
                        jobs.append({
                            'title': title,
                            'company': company,
                            'location': 'United States',
                            'description': f'Job at {company} - {title}',
                            'url': job_url,
                            'source': f'Career-{company}',
                            'posted_at': datetime.now().isoformat()
                        })
            
            # Method 4: Search for job keywords in page text and create jobs
            page_text = soup.get_text().lower()
            for keyword in job_keywords:
                if keyword in page_text:
                    # Create a generic job entry if we found keywords but no specific jobs
                    if len(jobs) == 0:
                        jobs.append({
                            'title': f'{keyword.title()} Position at {company}',
                            'company': company,
                            'location': 'United States',
                            'description': f'Career opportunity at {company} - {keyword}',
                            'url': career_url,
                            'source': f'Career-{company}',
                            'posted_at': datetime.now().isoformat()
                        })
                    break
        
        print(f"Found {len(jobs)} jobs from {company} career page")
        return jobs
        
    except Exception as e:
        print(f"Error scraping {company} career page: {e}")
        return []

def is_intern_position(title):
    """Check if job title indicates an intern position"""
    intern_keywords = ['intern', 'internship', 'co-op', 'coop', 'student', 'new grad', 'entry level']
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
                            posted_at=datetime.fromisoformat(job_data['posted_at'])
                        )
                        db.session.add(job)
                        saved_count += 1
                        
                except Exception as e:
                    print(f"Error saving job {job_data.get('title', 'Unknown')}: {e}")
                    continue
            
            # Commit batch to reduce memory usage
            db.session.commit()
            
            # Small delay to prevent overwhelming the database
            time.sleep(0.1)
        
        print(f"Total jobs saved: {saved_count}")
        return saved_count
        
    except Exception as e:
        print(f"Error in save_jobs_to_db: {e}")
        db.session.rollback()
        return 0