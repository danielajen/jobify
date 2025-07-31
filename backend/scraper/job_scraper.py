import sys
import os
# Add parent directory to Python path to resolve config import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
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

def get_enhanced_chrome_options():
    """Get enhanced Chrome options with anti-detection measures"""
    options = Options()
    
    # Basic options
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-plugins")
    options.add_argument("--disable-images")  # Faster loading
    options.add_argument("--disable-javascript")  # For basic scraping
    
    # Anti-detection measures
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # Enhanced user agent
    options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    # Window size to mimic real browser
    options.add_argument("--window-size=1920,1080")
    
    # Additional preferences
    prefs = {
        "profile.default_content_setting_values": {
            "notifications": 2,
            "geolocation": 2,
            "media_stream": 2
        },
        "profile.managed_default_content_settings": {
            "images": 2
        }
    }
    options.add_experimental_option("prefs", prefs)
    
    # Headless mode for production
    if os.environ.get('DATABASE_URL'):  # Heroku environment
        options.add_argument("--headless=new")
    
    return options

def get_enhanced_chrome_options_with_js():
    """Get Chrome options that allow JavaScript for dynamic content"""
    options = get_enhanced_chrome_options()
    options.add_argument("--enable-javascript")
    return options

def setup_driver_with_cookies(driver, cookies_dict, domain):
    """Setup driver with cookies for bypassing protection"""
    try:
        # First visit the domain to set cookies context
        driver.get(f"https://{domain}")
        time.sleep(2)
        
        # Add cookies
        for cookie_name, cookie_value in cookies_dict.items():
            if cookie_value and cookie_value != "your_cookie_here":
                try:
                    driver.add_cookie({
                        'name': cookie_name,
                        'value': cookie_value,
                        'domain': domain
                    })
                except Exception as e:
                    print(f"Error adding cookie {cookie_name}: {e}")
        
        # Refresh page to apply cookies
        driver.refresh()
        time.sleep(3)
        
    except Exception as e:
        print(f"Error setting up cookies: {e}")

def human_like_scroll(driver):
    """Perform human-like scrolling"""
    try:
        # Scroll down gradually
        for i in range(3):
            driver.execute_script(f"window.scrollTo(0, {1000 * (i + 1)});")
            time.sleep(random.uniform(1, 3))
        
        # Scroll back up
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(random.uniform(1, 2))
        
    except Exception as e:
        print(f"Error during human-like scroll: {e}")

def wait_for_element(driver, selector, timeout=10):
    """Wait for element to be present"""
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
        )
        return element
    except Exception:
        return None

def scrape_target_jobs():
    """Scrape jobs from general job boards"""
    jobs = []
    try:
        # Scrape GitHub internships
        github_jobs = scrape_github_jobs(config.SOURCES['github'])
        jobs.extend(github_jobs)
        print(f"Scraped {len(github_jobs)} jobs from GitHub")
        
        # Scrape BuiltIn with enhanced setup
        builtin_jobs = scrape_builtin_jobs(config.SOURCES['builtin'])
        jobs.extend(builtin_jobs)
        print(f"Scraped {len(builtin_jobs)} jobs from BuiltIn")
        
        # Scrape Glassdoor with enhanced setup
        glassdoor_jobs = scrape_glassdoor_jobs(config.SOURCES['glassdoor'])
        jobs.extend(glassdoor_jobs)
        print(f"Scraped {len(glassdoor_jobs)} jobs from Glassdoor")
        
        # Scrape Indeed with enhanced setup
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
        # Fetch raw markdown content with enhanced headers
        response = requests.get(url, headers=HEADERS, timeout=30)
        
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
                        
                        # Extract location
                        location = cols[2] if len(cols) > 2 else "Remote"
                        
                        # Extract URL - improved parsing
                        url_col = cols[3] if len(cols) > 3 else ""
                        job_url = ""
                        
                        # Handle different URL formats
                        if '[' in url_col and '](' in url_col:
                            # Markdown link format: [text](url)
                            job_url = url_col.split('](')[1].split(')')[0]
                        elif url_col.startswith('http'):
                            # Direct URL
                            job_url = url_col
                        elif 'http' in url_col:
                            # URL somewhere in the text
                            import re
                            url_match = re.search(r'https?://[^\s)\]]+', url_col)
                            if url_match:
                                job_url = url_match.group(0)
                        
                        # Create job object only if we have required fields
                        if position and company and job_url:
                            job = {
                                'title': position,
                                'company': company,
                                'location': location,
                                'url': job_url,
                                'source': 'github',
                                'description': '',
                                'posted_at': datetime.utcnow(),
                                'keywords': 'intern,2026'
                            }
                            
                            # Only process intern positions
                            if is_intern_position(job['title']):
                                jobs.append(job)
                                print(f"Added GitHub job: {job['title']} at {job['company']}")
                            
                    except Exception as e:
                        print(f"Error parsing GitHub job row: {e}")
                        continue
                        
        else:
            print(f"GitHub scraping failed with status code: {response.status_code}")
            
    except Exception as e:
        print(f"GitHub scraping error: {e}")
    
    return jobs

def scrape_builtin_jobs(url):
    """Scrape jobs from BuiltIn using enhanced Selenium setup"""
    jobs = []
    driver = None
    
    try:
        # Use enhanced Chrome options
        options = get_enhanced_chrome_options_with_js()
        
        # Setup Chrome driver
        if os.environ.get('DATABASE_URL'):  # Heroku environment
            # Use Chrome for Testing on Heroku
            driver = webdriver.Chrome(options=options)
        else:
            # Use ChromeDriverManager locally
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        
        print(f"Navigating to BuiltIn URL: {url}")
        driver.get(url)
        
        # Human-like behavior
        time.sleep(random.uniform(3, 5))
        human_like_scroll(driver)
        
        # Wait for content to load
        wait_for_element(driver, '.job-item, .job-row', timeout=15)
        
        # Get page source and parse
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Find job cards - updated selectors
        job_cards = soup.select('.job-item')
        if not job_cards:
            job_cards = soup.select('.job-row')
        if not job_cards:
            job_cards = soup.select('[class*="job"]')  # Fallback selector
            
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
                
                # Extract title with multiple selectors
                title_selectors = ['.title', '.job-title', 'h3', 'h4', '[class*="title"]']
                for selector in title_selectors:
                    title_elem = card.select_one(selector)
                    if title_elem and title_elem.text.strip():
                        job['title'] = title_elem.text.strip()
                        break
                
                # Extract company name with multiple selectors
                company_selectors = ['.company .name', '.company', '[class*="company"]']
                for selector in company_selectors:
                    company_elem = card.select_one(selector)
                    if company_elem and company_elem.text.strip():
                        job['company'] = company_elem.text.strip()
                        break
                
                # Extract location with multiple selectors
                location_selectors = ['.location', '[class*="location"]']
                for selector in location_selectors:
                    location_elem = card.select_one(selector)
                    if location_elem and location_elem.text.strip():
                        job['location'] = location_elem.text.strip()
                        break
                
                # Extract URL with multiple selectors
                url_selectors = ['a.job-row-anchor', 'a[href*="/job/"]', 'a[href*="careers"]', 'a']
                for selector in url_selectors:
                    url_elem = card.select_one(selector)
                    if url_elem and url_elem.get('href'):
                        job['url'] = urljoin(url, url_elem['href'])
                        break
                
                # Only process intern positions and ensure we have required fields
                if is_intern_position(job['title']) and job['title'] != "Unknown Position" and job['company'] != "Unknown Company":
                    jobs.append(job)
                    print(f"Added BuiltIn job #{i+1}: {job['title']}")
                    
            except Exception as e:
                print(f"Error parsing BuiltIn job card: {e}")
                
    except Exception as e:
        print(f"BuiltIn scraping error: {e}")
    finally:
        if driver:
            driver.quit()
    
    return jobs

def scrape_glassdoor_jobs(url):
    """Scrape jobs from Glassdoor using enhanced setup with cookies"""
    jobs = []
    driver = None
    
    try:
        # Use enhanced Chrome options
        options = get_enhanced_chrome_options_with_js()
        
        # Setup Chrome driver
        if os.environ.get('DATABASE_URL'):  # Heroku environment
            driver = webdriver.Chrome(options=options)
        else:
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        
        # Setup cookies for Glassdoor
        cookies = {
            'cf_clearance': os.environ.get('GLASSDOOR_CF_CLEARANCE', ''),
            'gsessionid': os.environ.get('GLASSDOOR_GSESSIONID', ''),
            'jsessionid': os.environ.get('GLASSDOOR_JSESSIONID', '')
        }
        
        # Setup cookies if available
        if any(cookies.values()):
            setup_driver_with_cookies(driver, cookies, 'glassdoor.ca')
        
        print(f"Navigating to Glassdoor URL: {url}")
        driver.get(url)
        
        # Human-like behavior
        time.sleep(random.uniform(3, 5))
        human_like_scroll(driver)
        
        # Wait for content to load
        wait_for_element(driver, '.job-search-key-l2wjgv', timeout=15)
        
        # Get page source and parse
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Find job cards - updated selectors for Glassdoor
        job_cards = soup.select('.job-search-key-l2wjgv')
        if not job_cards:
            job_cards = soup.select('[class*="job"]')
            
        print(f"Number of job cards found on Glassdoor: {len(job_cards)}")
            
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
                
                # Extract title with multiple selectors
                title_selectors = ['a[data-test="job-link"]', 'h2', 'h3', '[class*="title"]', 'a']
                for selector in title_selectors:
                    title_elem = card.select_one(selector)
                    if title_elem and title_elem.text.strip():
                        job['title'] = title_elem.text.strip()
                        break
                
                # Extract company name with multiple selectors
                company_selectors = ['[data-test="employer-name"]', '[class*="company"]', '[class*="employer"]']
                for selector in company_selectors:
                    company_elem = card.select_one(selector)
                    if company_elem and company_elem.text.strip():
                        job['company'] = company_elem.text.strip()
                        break
                
                # Extract location with multiple selectors
                location_selectors = ['[data-test="location"]', '[class*="location"]']
                for selector in location_selectors:
                    location_elem = card.select_one(selector)
                    if location_elem and location_elem.text.strip():
                        job['location'] = location_elem.text.strip()
                        break
                
                # Extract URL with multiple selectors
                url_selectors = ['a[data-test="job-link"]', 'a[href*="/job/"]', 'a']
                for selector in url_selectors:
                    url_elem = card.select_one(selector)
                    if url_elem and url_elem.get('href'):
                        job['url'] = urljoin(url, url_elem['href'])
                        break
                
                # Only process intern positions and ensure we have required fields
                if is_intern_position(job['title']) and job['title'] != "Unknown Position" and job['company'] != "Unknown Company":
                    jobs.append(job)
                    print(f"Added Glassdoor job #{i+1}: {job['title']}")
                    
            except Exception as e:
                print(f"Error parsing Glassdoor job card: {e}")
                
    except Exception as e:
        print(f"Glassdoor scraping error: {e}")
    finally:
        if driver:
            driver.quit()
    
    return jobs

def scrape_indeed_jobs(url):
    """Scrape jobs from Indeed using enhanced setup"""
    jobs = []
    driver = None
    
    try:
        # Use enhanced Chrome options
        options = get_enhanced_chrome_options_with_js()
        
        # Setup Chrome driver
        if os.environ.get('DATABASE_URL'):  # Heroku environment
            driver = webdriver.Chrome(options=options)
        else:
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        
        print(f"Navigating to Indeed URL: {url}")
        driver.get(url)
        
        # Human-like behavior
        time.sleep(random.uniform(3, 5))
        human_like_scroll(driver)
        
        # Wait for content to load
        wait_for_element(driver, '.job_seen_beacon', timeout=15)
        
        # Get page source and parse
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Find job cards - updated selectors for Indeed
        job_cards = soup.select('.job_seen_beacon')
        if not job_cards:
            job_cards = soup.select('[class*="job"]')
            
        print(f"Number of job cards found on Indeed: {len(job_cards)}")
            
        for i, card in enumerate(job_cards):
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
                
                # Extract title with multiple selectors
                title_selectors = ['h2 a', 'h3 a', '[class*="title"]', 'a']
                for selector in title_selectors:
                    title_elem = card.select_one(selector)
                    if title_elem and title_elem.text.strip():
                        job['title'] = title_elem.text.strip()
                        break
                
                # Extract company name with multiple selectors
                company_selectors = ['[data-testid="company-name"]', '[class*="company"]']
                for selector in company_selectors:
                    company_elem = card.select_one(selector)
                    if company_elem and company_elem.text.strip():
                        job['company'] = company_elem.text.strip()
                        break
                
                # Extract location with multiple selectors
                location_selectors = ['[data-testid="location"]', '[class*="location"]']
                for selector in location_selectors:
                    location_elem = card.select_one(selector)
                    if location_elem and location_elem.text.strip():
                        job['location'] = location_elem.text.strip()
                        break
                
                # Extract URL with multiple selectors
                url_selectors = ['h2 a', 'h3 a', 'a[href*="/job/"]', 'a']
                for selector in url_selectors:
                    url_elem = card.select_one(selector)
                    if url_elem and url_elem.get('href'):
                        job['url'] = urljoin(url, url_elem['href'])
                        break
                
                # Only process intern positions and ensure we have required fields
                if is_intern_position(job['title']) and job['title'] != "Unknown Position" and job['company'] != "Unknown Company":
                    jobs.append(job)
                    print(f"Added Indeed job #{i+1}: {job['title']}")
                    
            except Exception as e:
                print(f"Error parsing Indeed job card: {e}")
                
    except Exception as e:
        print(f"Indeed scraping error: {e}")
    finally:
        if driver:
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
            if not job_data.get('title') or not job_data.get('company'):
                print(f"Skipping job {total_processed}: Missing title or company")
                continue
            
            # Generate a URL if missing (for GitHub jobs that might not have direct URLs)
            if not job_data.get('url'):
                job_data['url'] = f"https://github.com/jobs/{job_data['company'].lower().replace(' ', '-')}-{job_data['title'].lower().replace(' ', '-')}"
                print(f"Generated URL for job {total_processed}: {job_data['url']}")
            
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
                new_count += 1
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