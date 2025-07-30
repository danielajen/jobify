import sys
import os
# Add parent directory to Python path to resolve config import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re
from config import config  # Now correctly imported
from database.models import db, Job
from urllib.parse import urljoin
import time
import random

# Common headers to mimic a browser
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}

# Glassdoor cookies - REPLACE THESE WITH YOUR ACTUAL COOKIES
COOKIE_CF_CLEARANCE = "your_cf_clearance_cookie_here"
COOKIE_GSESSIONID = "your_gsessionid_cookie_here"
COOKIE_JSESSIONID = "your_jsessionid_cookie_here"

def scrape_target_jobs():
    """Scrape jobs from general job boards"""
    jobs = []
    try:
        # Scrape GitHub internships
        github_jobs = scrape_github_jobs(config.SOURCES['github'])
        jobs.extend(github_jobs)
        print(f"Scraped {len(github_jobs)} jobs from GitHub")
        
        # Scrape BuiltIn
        builtin_jobs = scrape_builtin_jobs(config.SOURCES['builtin'])
        jobs.extend(builtin_jobs)
        print(f"Scraped {len(builtin_jobs)} jobs from BuiltIn")
        
        # Scrape Glassdoor
        glassdoor_jobs = scrape_glassdoor_jobs(config.SOURCES['glassdoor'])
        jobs.extend(glassdoor_jobs)
        print(f"Scraped {len(glassdoor_jobs)} jobs from Glassdoor")
        
        # Scrape Indeed
        indeed_jobs = scrape_indeed_jobs(config.SOURCES['indeed'])
        jobs.extend(indeed_jobs)
        print(f"Scraped {len(indeed_jobs)} jobs from Indeed")
        
    except Exception as e:
        print(f"General scraping error: {e}")
    
    return jobs

def scrape_github_jobs(url):
    """Scrape jobs from GitHub markdown repository"""
    jobs = []
    try:
        # Fetch raw markdown content
        response = requests.get(url, headers=HEADERS)
        
        if response.status_code == 200:
            # Parse markdown table directly
            lines = response.text.split('\n')
            table_started = False
            table_header_passed = False
            
            for line in lines:
                # Detect start of table
                if line.startswith('| ---'):
                    table_started = True
                    continue
                
                if table_started and line.startswith('|'):
                    # Skip header row
                    if not table_header_passed:
                        table_header_passed = True
                        continue
                    
                    # Split table row into columns
                    cols = [col.strip() for col in line.split('|')[1:-1]]
                    if len(cols) < 4:
                        continue
                    
                    try:
                        # Extract company name (handle markdown links)
                        company = cols[0]
                        if '[' in company and ']' in company:
                            company = company.split('[')[1].split(']')[0]
                        
                        # Extract position (handle markdown links)
                        position = cols[1]
                        if '[' in position and ']' in position:
                            position = position.split('[')[1].split(']')[0]
                        
                        # Location is third column
                        location = cols[2]
                        
                        # Extract application URL from fourth column
                        apply_url = None
                        url_cell = cols[3]
                        # Find first valid URL in the cell
                        url_match = re.search(r'https?://[^\s)\]]+', url_cell)
                        if url_match:
                            apply_url = url_match.group(0)
                        
                        # Only process intern positions
                        if apply_url and is_intern_position(position):
                            job = {
                                'title': position,
                                'company': company,
                                'location': location,
                                'url': apply_url,
                                'source': 'github',
                                'description': '',
                                'posted_at': datetime.utcnow(),
                                'keywords': 'intern,2026'
                            }
                            jobs.append(job)
                    except Exception as e:
                        print(f"Error parsing GitHub job row: {e}")
    except Exception as e:
        print(f"GitHub scraping error: {e}")
    
    return jobs

def scrape_builtin_jobs(url):
    """Scrape jobs from BuiltIn using Selenium"""
    jobs = []
    
    # Chrome options
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--headless=new")  # Run in headless mode

    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        print(f"Navigating to BuiltIn URL: {url}")
        driver.get(url)
        time.sleep(3 + random.uniform(1, 3))  # Random delay to mimic human
        
        # Get page source and parse
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Find job cards - updated selectors
        job_cards = soup.select('.job-item')
        if not job_cards:
            job_cards = soup.select('.job-row')
        print(f"Number of job cards found on BuiltIn: {len(job_cards)}")
            
        for i, card in enumerate(job_cards):
            try:
                # Create job object
                job = {
                    'title': "Unknown Position",
                    'company': "Unknown Company",
                    'location': "Remote",
                    'url': url,
                    'source': 'builtin',
                    'description': '',
                    'posted_at': datetime.utcnow(),
                    'keywords': 'intern,2026'
                }
                
                # Extract title
                title_elem = card.select_one('.title')
                if title_elem:
                    job['title'] = title_elem.text.strip()
                
                # Extract company name
                company_elem = card.select_one('.company .name')
                if company_elem:
                    job['company'] = company_elem.text.strip()
                
                # Extract location
                location_elem = card.select_one('.location')
                if location_elem:
                    job['location'] = location_elem.text.strip()
                
                # Extract URL
                url_elem = card.select_one('a.job-row-anchor')
                if not url_elem:
                    url_elem = card.select_one('a[href*="/job/"]')
                if url_elem:
                    job['url'] = urljoin(url, url_elem['href'])
                
                # Only process intern positions
                if is_intern_position(job['title']):
                    jobs.append(job)
                    print(f"Added BuiltIn job #{i+1}: {job['title']}")
            except Exception as e:
                print(f"Error parsing BuiltIn job card: {e}")
    except Exception as e:
        print(f"BuiltIn scraping error: {e}")
    finally:
        if 'driver' in locals():
            driver.quit()
    
    return jobs

def scrape_glassdoor_jobs(url):
    """Scrape jobs from Glassdoor using cookies to bypass protection"""
    jobs = []
    
    # Chrome options
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--headless=new")  # Run in headless mode

    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        
        # First visit the domain to set cookies context
        driver.get("https://www.glassdoor.ca")
        
        # Add cookies to bypass protection
        driver.add_cookie({
            'name': 'cf_clearance',
            'value': COOKIE_CF_CLEARANCE,
            'domain': '.glassdoor.ca',
            'path': '/',
            'secure': True
        })
        driver.add_cookie({
            'name': 'GSESSIONID',
            'value': COOKIE_GSESSIONID,
            'domain': '.glassdoor.ca',
            'path': '/',
            'secure': True
        })
        driver.add_cookie({
            'name': 'JSESSIONID',
            'value': COOKIE_JSESSIONID,
            'domain': '.glassdoor.ca',
            'path': '/',
            'secure': True
        })
        
        print("Navigating to Glassdoor URL with cookies...")
        driver.get(url)
        time.sleep(5)
        
        # Check for Cloudflare challenge
        if "Just a moment" in driver.title or "Cloudflare" in driver.page_source:
            print("⚠️ Cloudflare challenge detected! Update your cookies")
            return jobs

        # Get page source and parse
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        job_cards = soup.select('.react-job-listing, .jobCard, li.react-job-listing, div[data-test="jobListing"]')
        print(f"Number of job_cards found: {len(job_cards)}")

        # Process all job cards
        for i, card in enumerate(job_cards):
            try:
                # Create job object
                job = {
                    'title': "Unknown Position",
                    'company': "Unknown Company",
                    'location': "Remote",
                    'url': url,
                    'source': 'glassdoor',
                    'description': '',
                    'posted_at': datetime.utcnow(),
                    'keywords': 'intern,2026'
                }
                
                # Extract title
                title_elem = card.select_one('a, h2, h3, [data-test*="job"], .job-title, .jobTitle')
                if title_elem:
                    job['title'] = title_elem.text.strip()
                
                # Extract company name
                company_elem = card.select_one('[data-test*="company"], .employer, .company-name, .employerName')
                if company_elem:
                    job['company'] = company_elem.text.strip()
                
                # Extract location
                location_elem = card.select_one('[data-test*="location"], .location, .job-location')
                if location_elem:
                    job['location'] = location_elem.text.strip()
                
                # Extract URL
                url_elem = card.select_one('a[href]')
                if url_elem:
                    job['url'] = urljoin(url, url_elem['href'])
                
                # Only process intern positions
                if is_intern_position(job['title']):
                    jobs.append(job)
                    print(f"Added Glassdoor job #{i+1}: {job['title']}")
                
            except Exception as parse_err:
                print(f"⚠️ Error parsing Glassdoor job card: {parse_err}")
    except Exception as driver_err:
        print(f"❌ Error loading Glassdoor page: {driver_err}")
    finally:
        if 'driver' in locals():
            driver.quit()

    return jobs

def scrape_indeed_jobs(url):
    """Scrape jobs from Indeed using Selenium"""
    jobs = []
    
    # Chrome options
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--headless=new")  # Run in headless mode

    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        print(f"Navigating to Indeed URL: {url}")
        driver.get(url)
        time.sleep(3 + random.uniform(1, 3))  # Random delay to mimic human
        
        # Get page source and parse
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        job_cards = soup.select('.jobsearch-SerpJobCard, .cardOutline')
        print(f"Number of job cards found on Indeed: {len(job_cards)}")
        
        for i, job_card in enumerate(job_cards):
            try:
                # Create job object
                job = {
                    'title': "Unknown Position",
                    'company': "Unknown Company",
                    'location': "Remote",
                    'url': url,
                    'source': 'indeed',
                    'description': '',
                    'posted_at': datetime.utcnow(),
                    'keywords': 'intern,2026'
                }
                
                # Extract elements
                title_elem = job_card.select_one('.jobtitle, .jobTitle')
                company_elem = job_card.select_one('.company, .companyName')
                location_elem = job_card.select_one('.location, .companyLocation')
                
                # Extract URL element
                url_elem = title_elem if title_elem and title_elem.get('href') else job_card.select_one('a.jobtitle, a.jobTitle')
                
                if title_elem:
                    job['title'] = title_elem.text.strip()
                if company_elem:
                    job['company'] = company_elem.text.strip()
                if location_elem:
                    job['location'] = location_elem.text.strip()
                if url_elem:
                    if url_elem['href'].startswith('/'):
                        job['url'] = "https://indeed.com" + url_elem['href']
                    else:
                        job['url'] = url_elem['href']
                
                # Only process intern positions
                if is_intern_position(job['title']):
                    jobs.append(job)
                    print(f"Added Indeed job #{i+1}: {job['title']}")
            except Exception as e:
                print(f"Error parsing Indeed job card: {e}")
    except Exception as e:
        print(f"Indeed scraping error: {e}")
    finally:
        if 'driver' in locals():
            driver.quit()
    
    return jobs

def scrape_company_jobs(company):
    """
    Scrape jobs from a specific company's career page
    """
    jobs = []
    try:
        # Get the company's career page URL from config
        career_url = config.COMPANY_CAREER_PAGES.get(company)
        if not career_url:
            print(f"No career page found for {company}")
            return jobs
        
        response = requests.get(career_url, headers=HEADERS)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for job listings - try multiple selectors
        job_cards = soup.select('.job-listing, .job, .job-item, .posting, .job-card, .job-list-item, .opening')
        if not job_cards:
            job_cards = soup.select('a[href*="job"], a[href*="careers"], li.job')
        
        for card in job_cards:
            try:
                # Extract title - try multiple selectors
                title_elem = card.select_one('h2, h3, .job-title, .title, .job-name, .job__title, .posting-title')
                if not title_elem:
                    continue
                title = title_elem.text.strip()
                
                # Extract location - try multiple selectors
                location_elem = card.select_one('.location, .job-location, .job__location, .job-card__location, .posting-categories')
                location = location_elem.text.strip() if location_elem else "Remote"
                
                # Extract URL
                url = card.get('href')
                if not url:
                    # Try to find URL in a child element
                    link_elem = card.select_one('a')
                    if link_elem and link_elem.get('href'):
                        url = link_elem['href']
                    else:
                        continue
                    
                # Make sure URL is absolute
                if not url.startswith('http'):
                    url = urljoin(career_url, url)
                
                # Check if it's an intern position
                if is_intern_position(title):
                    job = {
                        'title': title,
                        'company': company,
                        'location': location,
                        'url': url,
                        'source': 'favorite_companies',
                        'description': '',
                        'posted_at': datetime.utcnow(),
                        'keywords': 'intern,2026'
                    }
                    jobs.append(job)
            except Exception as e:
                print(f"Error parsing job for {company}: {e}")
        
        # If no jobs found, try alternative approach
        if not jobs:
            jobs = scrape_company_jobs_fallback(company, career_url)
        
    except Exception as e:
        print(f"Error scraping {company}: {e}")
    
    return jobs

def scrape_company_jobs_fallback(company, career_url):
    """Fallback method for scraping company jobs"""
    jobs = []
    try:
        # Try searching for intern positions
        search_url = f"{career_url}?q=intern"
        response = requests.get(search_url, headers=HEADERS)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        job_cards = soup.select('.job-listing, .job, .job-item, .posting, .job-card, .job-list-item, .opening')
        if not job_cards:
            job_cards = soup.select('a[href*="job"], a[href*="careers"], li.job')
        
        for card in job_cards:
            try:
                title_elem = card.select_one('h2, h3, .job-title, .title, .job-name, .job__title, .posting-title')
                if not title_elem:
                    continue
                title = title_elem.text.strip()
                
                location_elem = card.select_one('.location, .job-location, .job__location, .job-card__location, .posting-categories')
                location = location_elem.text.strip() if location_elem else "Remote"
                
                url = card.get('href')
                if not url:
                    link_elem = card.select_one('a')
                    if link_elem and link_elem.get('href'):
                        url = link_elem['href']
                    else:
                        continue
                
                if url and not url.startswith('http'):
                    url = urljoin(career_url, url)
                
                if is_intern_position(title):
                    job = {
                        'title': title,
                        'company': company,
                        'location': location,
                        'url': url,
                        'source': 'favorite_companies',
                        'description': '',
                        'posted_at': datetime.utcnow(),
                        'keywords': 'intern,2026'
                    }
                    jobs.append(job)
            except Exception as e:
                print(f"Error parsing fallback job for {company}: {e}")
    except Exception as e:
        print(f"Fallback scraping failed for {company}: {e}")
    
    return jobs

def is_intern_position(title):
    """Check if job title indicates an intern position"""
    title_lower = title.lower()
    return any(kw in title_lower for kw in ['intern', 'internship', 'co-op', 'coop'])

def save_jobs_to_db(jobs):
    """Save scraped jobs to database, avoiding duplicates"""
    new_count = 0
    total_processed = 0
    
    try:
        print(f"Attempting to save {len(jobs)} jobs to database...")
        
        for job_data in jobs:
            total_processed += 1
            
            # Skip jobs with missing required fields
            if not job_data.get('title') or not job_data.get('company') or not job_data.get('url'):
                print(f"Skipping job {total_processed}: Missing required fields")
                continue
            
            # Check if job already exists by URL
            existing = Job.query.filter_by(url=job_data['url']).first()
            if existing:
                print(f"Job already exists: {job_data['title']} at {job_data['company']}")
                continue
            
            # Create new job
            try:
                job = Job(
                    title=job_data['title'],
                    company=job_data['company'],
                    location=job_data.get('location', 'Remote'),
                    description=job_data.get('description', ''),
                    url=job_data['url'],
                    posted_at=job_data.get('posted_at', datetime.utcnow()),
                    source=job_data.get('source', 'general')
                )
                db.session.add(job)
                new_count +=1
                print(f"Added job {new_count}: {job_data['title']} at {job_data['company']}")
                
            except Exception as e:
                print(f"Error creating job object: {e}")
                continue
        
        # Commit all changes
        db.session.commit()
        print(f"Successfully saved {new_count} new jobs out of {total_processed} processed")
        
    except Exception as e:
        db.session.rollback()
        print(f"Error saving jobs to DB: {e}")
        import traceback
        traceback.print_exc()
    
    return new_count