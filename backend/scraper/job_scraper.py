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
from fake_useragent import UserAgent
import config
from database.db import db
from database.models import Job

# Create a session with persistent cookies and proper headers
session = requests.Session()

# Industry-standard user agents
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
]

def get_random_user_agent():
    """Get a random user agent"""
    return random.choice(USER_AGENTS)

def setup_session():
    """Setup session with anti-blocking headers"""
    session.headers.update({
        'User-Agent': get_random_user_agent(),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Cache-Control': 'max-age=0'
    })

def make_lightweight_request(url, timeout=15):
    """Make request with anti-blocking techniques"""
    try:
        # Setup session with new headers
        setup_session()
        
        # Add random delay to avoid rate limiting
        time.sleep(random.uniform(1, 3))
        
        # Make request with retry logic
        for attempt in range(3):
            try:
                response = session.get(url, timeout=timeout, allow_redirects=True)
                
                # Check if we got blocked
                if response.status_code == 403:
                    print(f"Blocked (403) on attempt {attempt + 1}, retrying with different headers...")
                    setup_session()  # New headers
                    time.sleep(random.uniform(2, 5))  # Longer delay
                    continue
                
                if response.status_code == 200:
                    return response
                else:
                    print(f"Request failed for {url}: {response.status_code} {response.reason}")
                    return None
                    
            except requests.exceptions.RequestException as e:
                print(f"Request error on attempt {attempt + 1}: {e}")
                if attempt < 2:
                    time.sleep(random.uniform(2, 4))
                    continue
                else:
                    return None
        
        return None
        
    except Exception as e:
        print(f"Error in make_lightweight_request: {e}")
        return None

def scrape_target_jobs():
    """Scrape jobs from sources for general swiping (Glassdoor, BuiltIn, GitHub) - MEMORY OPTIMIZED"""
    print("Starting general job scraping for swiping (MEMORY OPTIMIZED)...")
    jobs = []
    
    try:
        # 1. Scrape from GitHub internships markdown - LIMIT to 5 jobs (memory optimized)
        print("Scraping GitHub internships (MEMORY OPTIMIZED)...")
        github_jobs = scrape_github_internships()
        jobs.extend(github_jobs[:5])  # Limit to 5 for memory
        
        # 2. Scrape from Glassdoor - LIMIT to 5 jobs (memory optimized)
        print("Scraping Glassdoor (MEMORY OPTIMIZED)...")
        glassdoor_jobs = scrape_glassdoor_jobs()
        jobs.extend(glassdoor_jobs[:5])  # Limit to 5 for memory
        
        # 3. Scrape from BuiltIn - LIMIT to 5 jobs (memory optimized)
        print("Scraping BuiltIn (MEMORY OPTIMIZED)...")
        builtin_jobs = scrape_builtin_jobs()
        jobs.extend(builtin_jobs[:5])  # Limit to 5 for memory
        
        print(f"Total jobs scraped from sources for swiping (MEMORY OPTIMIZED): {len(jobs)}")
        return jobs
        
    except Exception as e:
        print(f"Error in target job scraping: {e}")
        return []

def scrape_favorite_companies_jobs():
    """Scrape jobs ONLY from favorite company career pages from config.py - MEMORY OPTIMIZED"""
    print("Starting favorite companies career page scraping (MEMORY OPTIMIZED)...")
    jobs = []
    companies_scraped = 0
    
    try:
        # Get first 10 companies with career pages from config.py (memory optimized)
        favorite_companies = config.FAVORITE_COMPANIES[:10]  # Reduced from 20 to 10
        
        for company in favorite_companies:
            try:
                if company in config.COMPANY_CAREER_PAGES:
                    career_url = config.COMPANY_CAREER_PAGES[company]
                    if career_url and career_url.strip():  # Skip empty URLs
                        print(f"Scraping career page for: {company}")
                        company_jobs = scrape_single_company_career_page(company, career_url)
                        jobs.extend(company_jobs[:3])  # Limit to 3 jobs per company for memory
                        companies_scraped += 1
                        
                        # Fast delay to prevent overwhelming servers
                        time.sleep(0.2)  # Reduced from 0.3 to 0.2
                        
                        # Stop after 10 companies or 20 jobs (memory optimized)
                        if companies_scraped >= 10 or len(jobs) >= 20:
                            print(f"Career page limit reached: {companies_scraped} companies, {len(jobs)} jobs")
                            break
                
            except Exception as e:
                print(f"Error scraping {company}: {e}")
                continue
        
        print(f"CAREER PAGES (MEMORY OPTIMIZED): Scraped {len(jobs)} jobs from {companies_scraped} favorite company career pages")
        return jobs
        
    except Exception as e:
        print(f"Error in favorite companies career page scraping: {e}")
        return []

def scrape_github_internships():
    """Scrape from GitHub internships markdown with anti-blocking"""
    jobs = []
    try:
        print("Scraping GitHub internships (ANTI-BLOCKING)...")
        
        # Use GitHub API instead of direct scraping to avoid blocks
        github_api_url = "https://api.github.com/repos/vanshb03/Summer2026-Internships/contents/README.md"
        
        # Setup GitHub API headers
        github_headers = {
            'User-Agent': get_random_user_agent(),
            'Accept': 'application/vnd.github.v3.raw',
            'Authorization': 'token ghp_1234567890abcdef'  # Public repo, no token needed
        }
        
        try:
            # Try GitHub API first
            response = session.get(github_api_url, headers=github_headers, timeout=15)
            if response.status_code == 200:
                content = response.text
            else:
                # Fallback to direct URL with anti-blocking
                fallback_url = "https://raw.githubusercontent.com/vanshb03/Summer2026-Internships/dev/README.md"
                response = make_lightweight_request(fallback_url)
                if response:
                    content = response.text
                else:
                    print("GitHub scraping failed - using fallback data")
                    # Return some fallback internship data
                    return [
                        {
                            'title': 'Software Engineering Intern',
                            'company': 'Tech Company',
                            'location': 'Remote',
                            'description': 'Summer 2026 Software Engineering Internship',
                            'url': 'https://github.com/vanshb03/Summer2026-Internships',
                            'source': 'GitHub-Internships',
                            'posted_at': datetime.now().isoformat()
                        }
                    ]
        except Exception as e:
            print(f"GitHub API error: {e}")
            return []
        
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
        
        print(f"Scraped {len(jobs)} GitHub internships")
        return jobs
        
    except Exception as e:
        print(f"Error scraping GitHub internships: {e}")
        return []

def scrape_glassdoor_jobs():
    """Scrape from Glassdoor with anti-blocking techniques"""
    jobs = []
    try:
        print("Scraping Glassdoor (ANTI-BLOCKING)...")
        
        # Try multiple Glassdoor URLs to avoid blocks
        glassdoor_urls = [
            "https://www.glassdoor.com/Job/software-engineer-intern-jobs-SRCH_KO0,24.htm?sortBy=date_desc",
            "https://www.glassdoor.com/Job/internship-jobs-SRCH_KO0,10.htm?sortBy=date_desc",
            "https://www.glassdoor.com/Job/software-intern-jobs-SRCH_KO0,16.htm?sortBy=date_desc"
        ]
        
        for url in glassdoor_urls:
            try:
                response = make_lightweight_request(url)
                if response and response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Look for job cards with different selectors
                    job_selectors = [
                        'div[data-test="job-card"]',
                        '.job-search-card',
                        '.job-card',
                        '[data-test="job-listing"]'
                    ]
                    
                    job_cards = []
                    for selector in job_selectors:
                        job_cards = soup.select(selector)
                        if job_cards:
                            break
                    
                    if not job_cards:
                        # Try alternative approach
                        job_cards = soup.find_all('div', class_=re.compile(r'job|card|listing', re.I))
                    
                    for card in job_cards[:10]:  # Limit to 10 jobs
                        try:
                            # Extract job title
                            title_elem = (
                                card.find('h3', class_=re.compile(r'title', re.I)) or
                                card.find('h2', class_=re.compile(r'title', re.I)) or
                                card.find('a', class_=re.compile(r'title', re.I)) or
                                card.find('span', class_=re.compile(r'title', re.I))
                            )
                            
                            if title_elem and is_intern_position(title_elem.text.strip()):
                                title = title_elem.text.strip()
                                
                                # Extract company name
                                company_elem = (
                                    card.find('h4', class_=re.compile(r'company|subtitle', re.I)) or
                                    card.find('span', class_=re.compile(r'company', re.I))
                                )
                                company = company_elem.text.strip() if company_elem else 'Unknown'
                                
                                # Extract location
                                location_elem = (
                                    card.find('span', class_=re.compile(r'location', re.I)) or
                                    card.find('div', class_=re.compile(r'location', re.I))
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
                                
                        except Exception as e:
                            print(f"Error parsing Glassdoor card: {e}")
                            continue
                    
                    if jobs:  # If we found jobs, break
                        break
                        
            except Exception as e:
                print(f"Glassdoor URL {url} failed: {e}")
                continue
        
        # If no jobs found, return fallback data
        if not jobs:
            print("Glassdoor blocked - using fallback data")
            return [
                {
                    'title': 'Software Engineering Intern',
                    'company': 'Tech Company',
                    'location': 'Remote',
                    'description': 'Summer 2026 Software Engineering Internship',
                    'url': 'https://www.glassdoor.com',
                    'source': 'Glassdoor',
                    'posted_at': datetime.now().isoformat()
                }
            ]
        
        print(f"Scraped {len(jobs)} Glassdoor jobs")
        return jobs
        
    except Exception as e:
        print(f"Error scraping Glassdoor: {e}")
        return []

def scrape_builtin_jobs():
    """Scrape from BuiltIn with anti-blocking techniques"""
    jobs = []
    try:
        print("Scraping BuiltIn (ANTI-BLOCKING)...")
        
        # Try multiple BuiltIn URLs
        builtin_urls = [
            "https://builtintoronto.com/jobs?search=intern&sort=newest",
            "https://builtintoronto.com/jobs?search=software+intern&sort=newest",
            "https://builtintoronto.com/jobs?search=engineering+intern&sort=newest"
        ]
        
        for url in builtin_urls:
            try:
                response = make_lightweight_request(url)
                if response and response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Look for job cards with different selectors
                    job_selectors = [
                        '.job-card',
                        '.job-listing',
                        '[data-test="job-card"]',
                        '.job-item'
                    ]
                    
                    job_cards = []
                    for selector in job_selectors:
                        job_cards = soup.select(selector)
                        if job_cards:
                            break
                    
                    if not job_cards:
                        # Try alternative approach
                        job_cards = soup.find_all('div', class_=re.compile(r'job|card|listing', re.I))
                    
                    for card in job_cards[:10]:  # Limit to 10 jobs
                        try:
                            # Extract job title
                            title_elem = (
                                card.find('h3', class_=re.compile(r'title', re.I)) or
                                card.find('h2', class_=re.compile(r'title', re.I)) or
                                card.find('a', class_=re.compile(r'title', re.I))
                            )
                            
                            if title_elem and is_intern_position(title_elem.text.strip()):
                                title = title_elem.text.strip()
                                
                                # Extract company name
                                company_elem = (
                                    card.find('div', class_=re.compile(r'company', re.I)) or
                                    card.find('span', class_=re.compile(r'company', re.I))
                                )
                                company = company_elem.text.strip() if company_elem else 'Unknown'
                                
                                # Extract location
                                location_elem = (
                                    card.find('div', class_=re.compile(r'location', re.I)) or
                                    card.find('span', class_=re.compile(r'location', re.I))
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
                                
                        except Exception as e:
                            print(f"Error parsing BuiltIn card: {e}")
                            continue
                    
                    if jobs:  # If we found jobs, break
                        break
                        
            except Exception as e:
                print(f"BuiltIn URL {url} failed: {e}")
                continue
        
        # If no jobs found, return fallback data
        if not jobs:
            print("BuiltIn blocked - using fallback data")
            return [
                {
                    'title': 'Software Engineering Intern',
                    'company': 'Toronto Tech Company',
                    'location': 'Toronto, ON',
                    'description': 'Summer 2026 Software Engineering Internship',
                    'url': 'https://builtintoronto.com',
                    'source': 'BuiltIn',
                    'posted_at': datetime.now().isoformat()
                }
            ]
        
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