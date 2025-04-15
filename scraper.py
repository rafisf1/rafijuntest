from bs4 import BeautifulSoup
import requests
import time
import random
from datetime import datetime
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from linkedin_v2 import linkedin
import os
from dotenv import load_dotenv
from models import db, Alumni

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class LinkedInScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.setup_driver()

    def setup_driver(self):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

    def random_delay(self):
        time.sleep(random.uniform(2, 5))

    def scrape_profile(self, profile_url):
        """
        Scrape a single LinkedIn profile
        """
        try:
            self.driver.get(profile_url)
            self.random_delay()
            
            # Wait for the main content to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "pv-top-card"))
            )

            # Extract basic information
            name = self.driver.find_element(By.CLASS_NAME, "pv-top-card--name").text
            headline = self.driver.find_element(By.CLASS_NAME, "pv-top-card--headline").text
            
            # Extract experience
            experiences = []
            experience_section = self.driver.find_element(By.ID, "experience-section")
            experience_items = experience_section.find_elements(By.CLASS_NAME, "pv-entity__position-group")
            
            for item in experience_items:
                company = item.find_element(By.CLASS_NAME, "pv-entity__company-summary-info").text
                role = item.find_element(By.CLASS_NAME, "pv-entity__summary-info").text
                experiences.append({
                    'company': company,
                    'role': role
                })

            return {
                'name': name,
                'current_role': headline,
                'experiences': experiences,
                'profile_url': profile_url,
                'last_updated': datetime.utcnow()
            }

        except Exception as e:
            logger.error(f"Error scraping profile {profile_url}: {str(e)}")
            return None

    def search_lmu_alumni(self, page=1):
        """
        Search for LMU alumni on LinkedIn
        """
        base_url = "https://www.linkedin.com/school/loyola-marymount-university/people/"
        try:
            self.driver.get(f"{base_url}?page={page}")
            self.random_delay()

            # Wait for alumni cards to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "org-people-profile-card"))
            )

            # Extract alumni cards
            alumni_cards = self.driver.find_elements(By.CLASS_NAME, "org-people-profile-card")
            
            alumni_data = []
            for card in alumni_cards:
                try:
                    name = card.find_element(By.CLASS_NAME, "org-people-profile-card__profile-title").text
                    role = card.find_element(By.CLASS_NAME, "org-people-profile-card__profile-position").text
                    profile_url = card.find_element(By.CLASS_NAME, "org-people-profile-card__profile-link").get_attribute("href")
                    
                    alumni_data.append({
                        'name': name,
                        'current_role': role,
                        'profile_url': profile_url
                    })
                except Exception as e:
                    logger.error(f"Error extracting card data: {str(e)}")
                    continue

            return alumni_data

        except Exception as e:
            logger.error(f"Error searching alumni page {page}: {str(e)}")
            return []

    def close(self):
        """
        Close the browser
        """
        if self.driver:
            self.driver.quit()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

class LinkedInAPI:
    def __init__(self):
        self.client_id = os.getenv('LINKEDIN_CLIENT_ID')
        self.client_secret = os.getenv('LINKEDIN_CLIENT_SECRET')
        self.redirect_uri = os.getenv('LINKEDIN_REDIRECT_URI')
        
        if not all([self.client_id, self.client_secret, self.redirect_uri]):
            raise ValueError("LinkedIn API credentials not properly configured")
        
        self.application = None
        
    def authenticate(self, authorization_code=None):
        """
        Authenticate with LinkedIn. If authorization_code is provided,
        exchange it for an access token. Otherwise, return the authorization URL.
        """
        if authorization_code:
            self.application = linkedin.LinkedInApplication(
                authentication={
                    'client_id': self.client_id,
                    'client_secret': self.client_secret,
                    'redirect_uri': self.redirect_uri,
                    'authorization_code': authorization_code
                }
            )
            return True
        return False
    
    def is_authenticated(self):
        """Check if the API is authenticated"""
        return self.application is not None
    
    def search_lmu_alumni(self, start=0, count=100):
        """
        Search for LMU alumni on LinkedIn
        """
        if not self.is_authenticated():
            raise Exception("Not authenticated with LinkedIn")
        
        try:
            selectors = ['id', 'first-name', 'last-name', 'headline', 'industry', 'positions', 'public-profile-url']
            params = {
                'keywords': 'Loyola Marymount University',
                'start': start,
                'count': count
            }
            
            results = self.application.search_profile(selectors=selectors, params=params)
            return self._process_search_results(results)
            
        except Exception as e:
            logger.error(f"Error searching LinkedIn: {str(e)}")
            raise
    
    def _process_search_results(self, results):
        """
        Process LinkedIn search results and save to database
        """
        processed_results = []
        
        for profile in results.get('values', []):
            try:
                name = f"{profile.get('firstName', '')} {profile.get('lastName', '')}".strip()
                positions = profile.get('positions', {}).get('values', [])
                current_position = positions[0] if positions else {}
                
                alumni = Alumni.query.filter_by(linkedin_url=profile.get('publicProfileUrl')).first()
                if not alumni:
                    alumni = Alumni(
                        name=name,
                        linkedin_url=profile.get('publicProfileUrl'),
                        current_position=current_position.get('title'),
                        current_company=current_position.get('company', {}).get('name'),
                    )
                    db.session.add(alumni)
                else:
                    alumni.name = name
                    alumni.current_position = current_position.get('title')
                    alumni.current_company = current_position.get('company', {}).get('name')
                
                processed_results.append(alumni)
                
            except Exception as e:
                logger.error(f"Error processing profile {profile.get('id')}: {str(e)}")
                continue
        
        try:
            db.session.commit()
        except Exception as e:
            logger.error(f"Error saving to database: {str(e)}")
            db.session.rollback()
            raise
        
        return processed_results
    
    def get_auth_url(self):
        """
        Get the LinkedIn authorization URL
        """
        return linkedin.LinkedInAuthentication(
            self.client_id,
            self.client_secret,
            self.redirect_uri,
            ['r_liteprofile', 'r_emailaddress']
        ).authorization_url 