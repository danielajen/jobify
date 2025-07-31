import sys
import os
# Add parent directory to Python path to resolve config import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import requests
from bs4 import BeautifulSoup
import time
import re
from datetime import datetime
from urllib.parse import urljoin
import random
from config import config
from database.db import db
from database.models import Job

# Create multiple sessions with different configurations
sessions = []

# Industry-standard user agents
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0'
]

# Anti-blocking headers configurations
HEADER_CONFIGS = [
    {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Cache-Control': 'max-age=0',
        'DNT': '1'
    },
    {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    },
    {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
]

def create_session():
    """Create a new session with anti-blocking configuration"""
    session = requests.Session()
    config = random.choice(HEADER_CONFIGS)
    session.headers.update(config)
    return session

def get_random_user_agent():
    """Get a random user agent"""
    return random.choice(USER_AGENTS)

def make_lightweight_request(url, timeout=3):
    """Make request with immediate bypass - NO RETRIES - FAST"""
    try:
        # Create new session for each request
        session = create_session()
        
        # Minimal delay for speed
        time.sleep(random.uniform(0.05, 0.1))  # Reduced from 0.1-0.3 to 0.05-0.1
        
        # Single attempt with immediate bypass
        try:
            # Add referer header to look more legitimate
            headers = session.headers.copy()
            headers.update({
                'Referer': 'https://www.google.com/',
                'Sec-Fetch-Site': 'cross-site',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-User': '?1'
            })
            
            response = session.get(url, timeout=timeout, headers=headers, allow_redirects=True)
            
            if response.status_code == 200:
                return response
            elif response.status_code == 403:
                print(f"403 blocked - trying alternative URL immediately")
                return None  # Don't retry, try alternative URL instead
            else:
                print(f"Request failed: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            return None
        
    except Exception as e:
        print(f"An unexpected error occurred in make_lightweight_request: {e}")
        return None

def scrape_target_jobs():
    """Scrape jobs from sources for general swiping (Glassdoor, BuiltIn, GitHub) - FAST 15 JOBS LIMIT"""
    print("Starting FAST general job scraping for swiping (15 JOBS LIMIT)...")
    jobs = []
    
    try:
        # 1. Scrape from GitHub internships markdown - LIMIT to 5 jobs for speed
        print("Scraping GitHub internships (5 jobs limit for speed)...")
        github_jobs = scrape_github_internships()
        jobs.extend(github_jobs[:5])  # Limit to 5 for speed
        
        # 2. Scrape from Glassdoor - LIMIT to 5 jobs for speed
        print("Scraping Glassdoor (5 jobs limit for speed)...")
        glassdoor_jobs = scrape_glassdoor_jobs()
        jobs.extend(glassdoor_jobs[:5])  # Limit to 5 for speed
        
        # 3. Scrape from BuiltIn - LIMIT to 5 jobs for speed
        print("Scraping BuiltIn (5 jobs limit for speed)...")
        builtin_jobs = scrape_builtin_jobs()
        jobs.extend(builtin_jobs[:5])  # Limit to 5 for speed
        
        print(f"Total jobs scraped from sources for swiping (FAST 15 JOBS LIMIT): {len(jobs)}")
        return jobs
        
    except Exception as e:
        print(f"Error in target job scraping: {e}")
        return []

def scrape_favorite_companies_jobs():
    """Fast career page scraping - 20 companies at a time with quick updates"""
    print("Starting FAST career page scraping (20 companies, quick updates)...")
    jobs = []
    companies_scraped = 0
    
    try:
        # Get only first 20 companies for speed
        companies_to_scrape = config.FAVORITE_COMPANIES[:20]
        print(f"Scraping {len(companies_to_scrape)} companies quickly...")
        
        for company in companies_to_scrape:
            try:
                if company in config.COMPANY_CAREER_PAGES:
                    career_url = config.COMPANY_CAREER_PAGES[company]
                    if career_url and career_url.strip():
                        print(f"Quick scrape: {company}")
                        company_jobs = scrape_single_company_career_page(company, career_url)
                        jobs.extend(company_jobs[:1])  # Only 1 job per company for speed
                        companies_scraped += 1
                        
                        # Very fast delay
                        time.sleep(0.05)  # 50ms delay
                
            except Exception as e:
                print(f"Error scraping {company}: {e}")
                continue
        
        print(f"FAST CAREER PAGES: {len(jobs)} jobs from {companies_scraped} companies")
        return jobs
        
    except Exception as e:
        print(f"Error in fast career page scraping: {e}")
        return []

def scrape_github_internships():
    """Scrape from GitHub internships markdown with real anti-blocking"""
    jobs = []
    try:
        print("Scraping GitHub internships (REAL ANTI-BLOCKING)...")
        
        # Try multiple GitHub URLs to bypass blocks
        github_urls = [
            "https://raw.githubusercontent.com/vanshb03/Summer2026-Internships/dev/README.md",
            "https://raw.githubusercontent.com/vanshb03/Summer2026-Internships/main/README.md",
            "https://raw.githubusercontent.com/vanshb03/Summer2026-Internships/master/README.md"
        ]
        
        for url in github_urls:
            try:
                response = make_lightweight_request(url)
                if response and response.status_code == 200:
                    content = response.text
                    
                    # Parse markdown content
                    lines = content.split('\n')
                    current_company = None
                    
                    for line in lines:
                        line = line.strip()
                        
                        # Look for company headers
                        if line.startswith('## ') and not line.startswith('### '):
                            current_company = line.replace('## ', '').strip()
                            continue
                        
                        # Look for job links
                        if line.startswith('- [') and '](' in line and ')' in line:
                            try:
                                # Extract job title and URL
                                title_start = line.find('- [') + 3
                                title_end = line.find('](')
                                url_start = title_end + 2
                                url_end = line.find(')', url_start)
                                
                                if title_start < title_end and url_start < url_end:
                                    title = line[title_start:title_end].strip()
                                    url = line[url_start:url_end].strip()
                                    
                                    # Check if it's an internship
                                    if is_intern_position(title):
                                        jobs.append({
                                            'title': title,
                                            'company': current_company or 'Unknown',
                                            'location': 'Remote',
                                            'description': f'Internship at {current_company or "Unknown"}',
                                            'url': url,
                                            'source': 'GitHub-Internships',
                                            'posted_at': datetime.now().isoformat()
                                        })
                            except Exception as e:
                                print(f"Error parsing GitHub line: {e}")
                                continue
                    
                    if jobs:  # If we found jobs, break
                        break
                        
            except Exception as e:
                print(f"GitHub URL {url} failed: {e}")
                continue
        
        print(f"Scraped {len(jobs)} GitHub internships")
        return jobs
        
    except Exception as e:
        print(f"Error scraping GitHub internships: {e}")
        return []

def scrape_glassdoor_jobs():
    """Scrape from Glassdoor with REAL anti-blocking techniques"""
    jobs = []
    try:
        print("Scraping Glassdoor (REAL ANTI-BLOCKING)...")
        
        # Try multiple Glassdoor URLs with different approaches
        glassdoor_urls = [
            "https://www.glassdoor.com/Job/software-engineer-intern-jobs-SRCH_KO0,24.htm?sortBy=date_desc",
            "https://www.glassdoor.com/Job/internship-jobs-SRCH_KO0,10.htm?sortBy=date_desc",
            "https://www.glassdoor.com/Job/software-intern-jobs-SRCH_KO0,16.htm?sortBy=date_desc",
            "https://www.glassdoor.com/Job/engineering-intern-jobs-SRCH_KO0,18.htm?sortBy=date_desc"
        ]
        
        for url in glassdoor_urls:
            try:
                response = make_lightweight_request(url)
                if response and response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Look for job cards with multiple selectors
                    job_selectors = [
                        'div[data-test="job-card"]',
                        '.job-search-card',
                        '.job-card',
                        '[data-test="job-listing"]',
                        '.job-listing',
                        '.job-item',
                        '[class*="job"]',
                        '[class*="card"]'
                    ]
                    
                    job_cards = []
                    for selector in job_selectors:
                        job_cards = soup.select(selector)
                        if job_cards:
                            print(f"Found {len(job_cards)} job cards with selector: {selector}")
                            break
                    
                    if not job_cards:
                        # Try alternative approach with regex
                        job_cards = soup.find_all('div', class_=re.compile(r'job|card|listing', re.I))
                        print(f"Found {len(job_cards)} job cards with regex")
                    
                    for card in job_cards[:10]:  # Limit to 10 jobs
                        try:
                            # Extract job title with multiple approaches
                            title_elem = (
                                card.find('h3', class_=re.compile(r'title', re.I)) or
                                card.find('h2', class_=re.compile(r'title', re.I)) or
                                card.find('a', class_=re.compile(r'title', re.I)) or
                                card.find('span', class_=re.compile(r'title', re.I)) or
                                card.find('div', class_=re.compile(r'title', re.I)) or
                                card.find('h3') or
                                card.find('h2') or
                                card.find('a')
                            )
                            
                            if title_elem and is_intern_position(title_elem.text.strip()):
                                title = title_elem.text.strip()
                                
                                # Extract company name
                                company_elem = (
                                    card.find('h4', class_=re.compile(r'company|subtitle', re.I)) or
                                    card.find('span', class_=re.compile(r'company', re.I)) or
                                    card.find('div', class_=re.compile(r'company', re.I)) or
                                    card.find('h4') or
                                    card.find('span')
                                )
                                company = company_elem.text.strip() if company_elem else 'Unknown'
                                
                                # Extract location
                                location_elem = (
                                    card.find('span', class_=re.compile(r'location', re.I)) or
                                    card.find('div', class_=re.compile(r'location', re.I)) or
                                    card.find('span')
                                )
                                location = location_elem.text.strip() if location_elem else 'Remote'
                                
                                # Extract URL
                                link_elem = card.find('a', href=True)
                                job_url = f"https://www.glassdoor.com{link_elem['href']}" if link_elem else url
                                
                                jobs.append({
                                    'title': title,
                                    'company': company,
                                    'location': location,
                                    'description': f'Internship at {company}',
                                    'url': job_url,
                                    'source': 'Glassdoor',
                                    'posted_at': datetime.now().isoformat()
                                })
                                print(f"Found job: {title} at {company}")
                                
                        except Exception as e:
                            print(f"Error parsing Glassdoor card: {e}")
                            continue
                    
                    if jobs:  # If we found jobs, break
                        break
                        
            except Exception as e:
                print(f"Glassdoor URL {url} failed: {e}")
                continue
        
        print(f"Scraped {len(jobs)} Glassdoor jobs")
        return jobs
        
    except Exception as e:
        print(f"Error scraping Glassdoor: {e}")
        return []

def scrape_builtin_jobs():
    """Scrape from BuiltIn with REAL anti-blocking techniques"""
    jobs = []
    try:
        print("Scraping BuiltIn (REAL ANTI-BLOCKING)...")
        
        # Try multiple BuiltIn URLs
        builtin_urls = [
            "https://builtintoronto.com/jobs?search=intern&sort=newest",
            "https://builtintoronto.com/jobs?search=software+intern&sort=newest",
            "https://builtintoronto.com/jobs?search=engineering+intern&sort=newest",
            "https://builtintoronto.com/jobs?search=developer+intern&sort=newest"
        ]
        
        for url in builtin_urls:
            try:
                response = make_lightweight_request(url)
                if response and response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Look for job cards with multiple selectors
                    job_selectors = [
                        '.job-card',
                        '.job-listing',
                        '[data-test="job-card"]',
                        '.job-item',
                        '.job-post',
                        '[class*="job"]',
                        '[class*="card"]'
                    ]
                    
                    job_cards = []
                    for selector in job_selectors:
                        job_cards = soup.select(selector)
                        if job_cards:
                            print(f"Found {len(job_cards)} job cards with selector: {selector}")
                            break
                    
                    if not job_cards:
                        # Try alternative approach with regex
                        job_cards = soup.find_all('div', class_=re.compile(r'job|card|listing', re.I))
                        print(f"Found {len(job_cards)} job cards with regex")
                    
                    for card in job_cards[:10]:  # Limit to 10 jobs
                        try:
                            # Extract job title with multiple approaches
                            title_elem = (
                                card.find('h3', class_=re.compile(r'title', re.I)) or
                                card.find('h2', class_=re.compile(r'title', re.I)) or
                                card.find('a', class_=re.compile(r'title', re.I)) or
                                card.find('span', class_=re.compile(r'title', re.I)) or
                                card.find('div', class_=re.compile(r'title', re.I)) or
                                card.find('h3') or
                                card.find('h2') or
                                card.find('a')
                            )
                            
                            if title_elem and is_intern_position(title_elem.text.strip()):
                                title = title_elem.text.strip()
                                
                                # Extract company name
                                company_elem = (
                                    card.find('div', class_=re.compile(r'company', re.I)) or
                                    card.find('span', class_=re.compile(r'company', re.I)) or
                                    card.find('h4', class_=re.compile(r'company', re.I)) or
                                    card.find('h4') or
                                    card.find('span')
                                )
                                company = company_elem.text.strip() if company_elem else 'Unknown'
                                
                                # Extract location
                                location_elem = (
                                    card.find('div', class_=re.compile(r'location', re.I)) or
                                    card.find('span', class_=re.compile(r'location', re.I)) or
                                    card.find('span')
                                )
                                location = location_elem.text.strip() if location_elem else 'Toronto'
                                
                                # Extract URL
                                link_elem = card.find('a', href=True)
                                job_url = f"https://builtintoronto.com{link_elem['href']}" if link_elem else url
                                
                                jobs.append({
                                    'title': title,
                                    'company': company,
                                    'location': location,
                                    'description': f'Internship at {company}',
                                    'url': job_url,
                                    'source': 'BuiltIn',
                                    'posted_at': datetime.now().isoformat()
                                })
                                print(f"Found job: {title} at {company}")
                                
                        except Exception as e:
                            print(f"Error parsing BuiltIn card: {e}")
                            continue
                    
                    if jobs:  # If we found jobs, break
                        break
                        
            except Exception as e:
                print(f"BuiltIn URL {url} failed: {e}")
                continue
        
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
                        # Convert posted_at string to datetime object
                        posted_at = None
                        if job_data.get('posted_at'):
                            try:
                                if isinstance(job_data['posted_at'], str):
                                    posted_at = datetime.fromisoformat(job_data['posted_at'].replace('Z', '+00:00'))
                                else:
                                    posted_at = job_data['posted_at']
                            except:
                                posted_at = datetime.now()
                        
                        job = Job(
                            title=job_data['title'],
                            company=job_data['company'],
                            location=job_data['location'],
                            description=job_data['description'],
                            url=job_data['url'],
                            source=job_data['source'],
                            posted_at=posted_at
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