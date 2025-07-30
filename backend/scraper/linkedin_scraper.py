import requests
import time
import random
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from fake_useragent import UserAgent
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)

class LinkedInScraper:
    def __init__(self, user_agent=None):
        self.ua = UserAgent()
        self.user_agent = user_agent or self.ua.random
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Target areas for Canadian tech professionals
        self.target_areas = [
            'Toronto, Ontario, Canada',
            'Oakville, Ontario, Canada', 
            'Mississauga, Ontario, Canada',
            'Brampton, Ontario, Canada',
            'Vaughan, Ontario, Canada',
            'Markham, Ontario, Canada',
            'Richmond Hill, Ontario, Canada',
            'Burlington, Ontario, Canada',
            'Hamilton, Ontario, Canada',
            'Kitchener, Ontario, Canada',
            'Waterloo, Ontario, Canada',
            'London, Ontario, Canada',
            'Ottawa, Ontario, Canada',
            'Montreal, Quebec, Canada',
            'Vancouver, British Columbia, Canada',
            'Calgary, Alberta, Canada',
            'Edmonton, Alberta, Canada'
        ]
        
        # Big tech companies
        self.big_tech_companies = [
            'Google', 'Apple', 'Microsoft', 'Amazon', 'Meta', 'Netflix', 'Twitter',
            'Uber', 'Airbnb', 'Stripe', 'Square', 'Palantir', 'Databricks',
            'Snowflake', 'MongoDB', 'Atlassian', 'Slack', 'Zoom', 'Salesforce',
            'Adobe', 'Intel', 'NVIDIA', 'AMD', 'Oracle', 'IBM', 'Cisco',
            'Shopify', 'RBC', 'TD Bank', 'Scotiabank', 'BMO', 'CIBC',
            'Bell', 'Rogers', 'Telus', 'Cogeco', 'Shaw', 'Videotron',
            'Hydro One', 'Ontario Power Generation', 'Bruce Power',
            'Canadian Tire', 'Loblaw', 'Sobeys', 'Metro', 'Walmart Canada',
            'Costco Canada', 'Home Depot Canada', 'Canadian National Railway',
            'Canadian Pacific Railway', 'Air Canada', 'WestJet', 'Porter Airlines',
            'Manulife', 'Sun Life', 'Great-West Life', 'Canada Life',
            'Desjardins', 'Co-operators', 'Intact Financial', 'Aviva Canada',
            'Allstate Canada', 'State Farm Canada', 'TD Insurance',
            'RBC Insurance', 'Scotiabank Insurance', 'BMO Insurance',
            'Retool', 'Nextdoor', 'Duolingo', 'Viral Nation', 'Bond Brand Loyalty',
            'StackAdapt', 'Index Exchange', 'OpenText', 'Barnacle Systems Inc.', 'Chime',
            'Boosted.ai', 'Coda', 'Top Hat', 'Hightouch', 'Intelliculture', 'OpsLevel',
            'Otter.ai', 'CircleCI', 'Flywheel Digital', 'NURO', 'Trellis', 'Retailogists',
            'Adaptivist', 'Ledn', 'RouteThis', 'BIMM', 'Ziphq', 'Wish', 'SkipTheDishes',
            'TouchBistro', 'Thoughtworks', 'Etsy', 'Cloudflare', 'Chainalysis', 'Binance',
            'Webtoon Entertainment', 'Wave', 'Loop Financial', 'Prodigy Education',
            'Clearco', 'Archon Systems Inc.', 'Plenty of Fish', 'Venngage', 'Ritual.co',
            'Swoon', 'Zillow', 'Coinbase', 'Wayfair', 'Okta', 'Faire', 'Instacart',
            'Reddit', 'Bluedot', 'Rippling', 'Cohere', 'Clutch', 'Dapper Labs', 
            'Outschool', 'Bolt', 'Upgrade', 'Lyft', 'Lookout', 'ApplyBoard', 'Dialpad',
            'Addepar', 'Hopper', 'Notch', 'VTS', 'Cockroach Labs', 'Hyperscience',
            'Rivian', 'ChargePoint', 'Tonal', 'GlossGenius', 'Square', 'Unether AI',
            'Copado', 'EvenUp', 'Super.com', 'BenchSci', 'Benevity', 'Vena Solutions',
            'Vagaro', 'Fabric.inc', 'Procurify', 'App Annie', 'Tenstorrent',
            'Forethought', 'Course Hero', 'League', 'Chegg', 'AI Redefined', 'Mistplay',
            'Moves Financial', 'Grammarly', 'Replit', 'Replicant', 'Plooto', 'Fullscript',
            'Rose Rocket', 'Validere', 'Certn', 'Coffee Meets Bagel', 'Mattermost',
            'AuditBoard', 'Pachyderm', 'Sanctuary AI', 'Unity', 'GoDaddy',
            'CentralSquare Technologies', 'Yelp', 'NODA', 'CentML', 'Remarcable Inc.',
            'SAGE', 'X', 'Tesla', 'TMX Group', 'Nvidia', 'Arctic Wolf', 'Nokia', 'AMD',
            'Vopemed', 'Flashfood', 'Gusto', 'Epic Games', 'Cribl', 'Slack', 'Indigo',
            'Auvik Networks', 'SOTI', 'KeyDataCyber', 'Opifiny Corp', 'Meta', 'Tomato Pay Inc',
            'Bitsight', 'Spotify', 'EA', 'Workiva', 'The Trade Desk', 'Robinhood',
            'Intelliware', 'Figma', 'Verkada', 'Schonfeld', 'Ecomtent', 'Citrus (Camp Management Software)',
            'TalentMinded', 'Transify', 'Sync.com', 'Questrade', 'Xanadu', 'Demonware',
            'Shyft Labs', 'Wealthsimple', 'Infor', 'Connor, Clark & Lunn Infrastructure',
            'FGS Global', 'Lancey', 'Google', 'Amazon', 'Netflix', 'Snapchat', 'Twilio'
        ]
        
        # Job titles to target
        self.target_job_titles = [
            'Software Engineer', 'Software Developer', 'Full Stack Developer',
            'Frontend Developer', 'Backend Developer', 'DevOps Engineer',
            'Data Scientist', 'Data Engineer', 'Machine Learning Engineer',
            'Product Manager', 'Product Owner', 'Technical Product Manager',
            'Engineering Manager', 'Tech Lead', 'Senior Software Engineer',
            'Principal Engineer', 'Staff Engineer', 'Senior Developer',
            'Lead Developer', 'Architect', 'Solutions Architect',
            'QA Engineer', 'Test Engineer', 'Quality Assurance Engineer',
            'UI/UX Designer', 'UX Designer', 'UI Designer', 'Product Designer',
            'Technical Writer', 'Developer Advocate', 'Site Reliability Engineer',
            'Cloud Engineer', 'Infrastructure Engineer', 'Security Engineer',
            'Mobile Developer', 'iOS Developer', 'Android Developer',
            'React Developer', 'Python Developer', 'Java Developer',
            'Node.js Developer', 'Ruby Developer', 'PHP Developer',
            'C++ Developer', 'C# Developer', '.NET Developer'
        ]
        
        # Top universities for alumni filtering
        self.top_universities = [
            'University of Toronto', 'University of Waterloo', 'University of British Columbia',
            'McGill University', 'University of Alberta', 'University of Ottawa',
            'Western University', 'McMaster University', 'Queen\'s University',
            'University of Calgary', 'University of Victoria', 'Simon Fraser University',
            'Carleton University', 'York University', 'Ryerson University',
            'University of Guelph', 'University of Western Ontario', 'Western Ontario',
            'University of Windsor', 'Brock University', 'Trent University',
            'Wilfrid Laurier University', 'University of Ontario Institute of Technology',
            'OCAD University', 'Ontario College of Art and Design',
            'Sheridan College', 'Seneca College', 'Humber College',
            'George Brown College', 'Centennial College', 'Algonquin College',
            'Conestoga College', 'Mohawk College', 'Fanshawe College',
            'Niagara College', 'Durham College', 'Loyalist College',
            'St. Lawrence College', 'Cambrian College', 'Canadore College',
            'Northern College', 'Sault College', 'Confederation College',
            'Lakehead University', 'Laurentian University', 'Nipissing University',
            'University of Sudbury', 'Algoma University', 'Thorneloe University',
            'Huntington University', 'University of Trinity College',
            'Victoria University', 'St. Michael\'s College', 'University College',
            'New College', 'Innis College', 'Woodsworth College',
            'University of St. Michael\'s College', 'Regis College',
            'Emmanuel College', 'Knox College', 'Wycliffe College',
            'Trinity College', 'Massey College', 'University of Toronto Mississauga',
            'University of Toronto Scarborough', 'University of Waterloo St. Jerome\'s',
            'University of Waterloo Renison', 'University of Waterloo Conrad Grebel',
            'University of Waterloo St. Paul\'s', 'University of Waterloo United College'
        ]

    def setup_driver(self, headless=True):
        """Setup Chrome driver with anti-detection measures"""
        options = Options()
        
        if headless:
            options.add_argument("--headless=new")
        
        # Anti-detection measures
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument(f"user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Additional stealth settings
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-plugins')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-web-security')
        options.add_argument('--allow-running-insecure-content')
        
        # Use ChromeDriverManager
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver

    def search_linkedin_profiles(self, query, filters=None, max_results=100):
        """
        Search LinkedIn profiles with advanced filtering - REAL SCRAPING ONLY
        """
        if filters is None:
            filters = {}
        
        profiles = []
        driver = None
        
        try:
            logger.info(f"Starting LinkedIn profile scraping with query: {query}, filters: {filters}")
            
            # Scrape real profiles
            profiles = self._scrape_real_linkedin_profiles(query, filters, max_results)
            
            if not profiles:
                logger.warning("Real scraping returned no results")
                
            logger.info(f"Successfully scraped {len(profiles)} LinkedIn profiles")
            
        except Exception as e:
            logger.error(f"Error searching LinkedIn profiles: {str(e)}")
        finally:
            if driver:
                driver.quit()
        
        return profiles

    def _scrape_real_linkedin_profiles(self, query, filters, max_results):
        """Scrape real LinkedIn profiles using Selenium"""
        profiles = []
        driver = None
        
        try:
            driver = self.setup_driver(headless=True)
            
            # Build search query
            search_query = self._build_real_search_query(query, filters)
            
            # Search LinkedIn
            search_url = f"https://www.linkedin.com/search/results/people/?keywords={search_query}&origin=GLOBAL_SEARCH_HEADER"
            logger.info(f"Searching LinkedIn URL: {search_url}")
            
            driver.get(search_url)
            time.sleep(5)  # Wait for page to load
            
            # Check if we're blocked or need login
            if "login" in driver.current_url.lower() or "auth" in driver.current_url.lower():
                logger.warning("LinkedIn requires login, cannot scrape real profiles")
                return []
            
            # Look for profile cards - updated selectors
            profile_cards = driver.find_elements(By.CSS_SELECTOR, ".entity-result, .reusable-search__result-container")
            
            if not profile_cards:
                # Try alternative selectors
                profile_cards = driver.find_elements(By.CSS_SELECTOR, ".search-result, .search-results-container li")
            
            logger.info(f"Found {len(profile_cards)} profile cards")
            
            for i, card in enumerate(profile_cards[:max_results]):
                try:
                    profile = self._extract_real_profile_from_card(card, filters)
                    if profile:
                        profiles.append(profile)
                        logger.info(f"Extracted profile {i+1}: {profile['name']} at {profile['company']}")
                except Exception as e:
                    logger.warning(f"Error extracting profile from card {i}: {str(e)}")
                    continue
            
        except Exception as e:
            logger.error(f"Error in LinkedIn scraping: {str(e)}")
        finally:
            if driver:
                driver.quit()
        
        return profiles

    def _build_real_search_query(self, query, filters):
        """Build real LinkedIn search query"""
        search_terms = [query]
        
        # Add location filters
        if filters.get('location'):
            locations = filters['location']
            if isinstance(locations, list):
                search_terms.extend(locations)
            else:
                search_terms.append(locations)
        
        # Add company filters
        if filters.get('company'):
            companies = filters['company']
            if isinstance(companies, list):
                search_terms.extend([f"company:{company}" for company in companies])
            else:
                search_terms.append(f"company:{companies}")
        
        # Add job title filters
        if filters.get('job_title'):
            titles = filters['job_title']
            if isinstance(titles, list):
                search_terms.extend([f"title:{title}" for title in titles])
            else:
                search_terms.append(f"title:{titles}")
        
        return " ".join(search_terms)

    def _extract_real_profile_from_card(self, card, filters):
        """Extract real profile data from LinkedIn search result card"""
        try:
            # EXTRACT NAME FROM ACTUAL PROFILE CARD
            name_selectors = [
                ".entity-result__title-text a",
                ".reusable-search__result-container .entity-result__title-text a",
                ".search-result__info .search-result__result-link",
                "h3 a",
                ".name a",
                "a.app-aware-link span[aria-hidden='true']"
            ]
            
            name = None
            profile_url = None
            
            for selector in name_selectors:
                try:
                    name_element = card.find_element(By.CSS_SELECTOR, selector)
                    name = name_element.text.strip()
                    
                    # Get profile URL from parent link
                    if selector == "a.app-aware-link span[aria-hidden='true']":
                        parent_link = card.find_element(By.CSS_SELECTOR, "a.app-aware-link")
                        profile_url = parent_link.get_attribute("href")
                    else:
                        profile_url = name_element.get_attribute("href")
                    
                    if name and profile_url:
                        break
                except NoSuchElementException:
                    continue
            
            if not name:
                return None
            
            # EXTRACT HEADLINE/TITLE
            title_selectors = [
                ".entity-result__primary-subtitle",
                ".reusable-search__result-container .entity-result__primary-subtitle",
                ".search-result__info .search-result__subtitle",
                ".headline",
                ".title",
                ".entity-result__summary"
            ]
            
            title = "Professional"
            for selector in title_selectors:
                try:
                    title_element = card.find_element(By.CSS_SELECTOR, selector)
                    title = title_element.text.strip()
                    break
                except NoSuchElementException:
                    continue
            
            # EXTRACT LOCATION
            location_selectors = [
                ".entity-result__secondary-subtitle",
                ".reusable-search__result-container .entity-result__secondary-subtitle",
                ".search-result__info .search-result__location",
                ".location",
                ".entity-result__secondary-subtitle t-14"
            ]
            
            location = "Canada"
            for selector in location_selectors:
                try:
                    location_element = card.find_element(By.CSS_SELECTOR, selector)
                    location = location_element.text.strip()
                    break
                except NoSuchElementException:
                    continue
            
            # EXTRACT COMPANY FROM TITLE
            company = "Technology Company"
            if " at " in title:
                parts = title.split(" at ")
                if len(parts) > 1:
                    company = parts[1].split("\n")[0].strip()
            elif " - " in title:
                parts = title.split(" - ")
                company = parts[0].strip()
            
            # EXTRACT PROFILE ID FROM URL
            profile_id = self._extract_profile_id_from_url(profile_url) if profile_url else f"profile_{int(time.time())}_{random.randint(1000,9999)}"
            
            # GENERATE EMAIL
            email = self._generate_email_from_name(name, company) if name and company else None
            
            # DETERMINE IF ALUMNI
            is_alumni = "university" in title.lower() or "alumni" in title.lower()
            
            return {
                'id': profile_id,
                'name': name,
                'title': title,
                'company': company,
                'location': location,
                'profile_url': profile_url,
                'mutual_connections': 0,  
                'response_rate': 0,  # Placeholder
                'is_alumni': is_alumni,
                'email': email,
                'headline': f"{title} at {company}" if company else title,
                'scraped_at': time.time(),
                'source': 'real_linkedin_scraping'
            }
            
        except Exception as e:
            logger.warning(f"Error extracting profile data: {str(e)}")
            return None

    def _extract_profile_id_from_url(self, profile_url):
        """Extract LinkedIn profile ID from URL"""
        if not profile_url:
            return f"profile_{int(time.time())}_{random.randint(1000,9999)}"
        
        try:
            # Handle different LinkedIn URL formats
            if '/in/' in profile_url:
                path = urlparse(profile_url).path
                profile_id = path.split('/in/')[-1].split('/')[0]
                return profile_id
            else:
                return profile_url.split('/')[-1]
        except:
            return f"profile_{int(time.time())}_{random.randint(1000,9999)}"

    def _generate_email_from_name(self, name, company):
        """Generate email address based on name and company"""
        if not name or not company:
            return None
        
        # Clean company name
        company_clean = re.sub(r'[^\w\s]', '', company).strip().lower()
        company_clean = company_clean.replace(' ', '')
        
        # Clean name
        name_parts = name.lower().split()
        if len(name_parts) >= 2:
            first_name = name_parts[0]
            last_name = name_parts[-1]
            
            # Common email patterns
            email_patterns = [
                f"{first_name}.{last_name}@{company_clean}.com",
                f"{first_name}{last_name}@{company_clean}.com",
                f"{first_name[0]}{last_name}@{company_clean}.com",
                f"{first_name}_{last_name}@{company_clean}.com",
                f"{first_name}@{company_clean}.com"
            ]
            
            return random.choice(email_patterns)
        
        return f"contact@{company_clean}.com"

    def scrape_company_employees(self, company_name, location=None, max_results=50):
        """Scrape employees from a specific company"""
        filters = {
            'company': company_name
        }
        
        if location:
            filters['location'] = location
        
        return self.search_linkedin_profiles(
            query=f"employees at {company_name}",
            filters=filters,
            max_results=max_results
        )

    def scrape_location_professionals(self, location, job_titles=None, max_results=100):
        """Scrape professionals from a specific location"""
        filters = {
            'location': location
        }
        
        if job_titles:
            filters['job_title'] = job_titles
        
        return self.search_linkedin_profiles(
            query=f"professionals in {location}",
            filters=filters,
            max_results=max_results
        )

    def scrape_alumni_network(self, university, location=None, max_results=100):
        """Scrape alumni from a specific university"""
        filters = {
            'alumni': True,
            'location': location if location else 'Toronto, Ontario, Canada'
        }
        
        return self.search_linkedin_profiles(
            query=f"alumni from {university}",
            filters=filters,
            max_results=max_results
        )

    def get_recommended_profiles(self, user_profile, max_results=50):
        """Get recommended profiles based on user's profile and preferences"""
        # Extract user's location and interests
        user_location = user_profile.get('location', 'Toronto, Ontario, Canada')
        
        # Focus on experienced professionals
        job_titles = [
            'Senior Software Engineer', 'Lead Developer', 'Engineering Manager',
            'Technical Lead', 'Principal Engineer', 'Architect'
        ]
        
        filters = {
            'location': user_location,
            'job_title': job_titles,
            'company': self.big_tech_companies[:20]  # Top 20 companies
        }
        
        return self.search_linkedin_profiles(
            query="tech professionals",
            filters=filters,
            max_results=max_results
        )