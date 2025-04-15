import csv
import logging
import re
import time
import argparse
from typing import List, Dict, Optional, Tuple
import requests
from bs4 import BeautifulSoup, NavigableString, Tag
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse
import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)

# Configuration
DELAY_BETWEEN_REQUESTS = 2  # seconds
MAX_RETRIES = 3
TIMEOUT = 30

# Regular expressions for contact information
EMAIL_PATTERN = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
PHONE_PATTERN = r'(?:\+\d{1,3}[-. ]?)?\(?\d{3}\)?[-. ]?\d{3}[-. ]?\d{4}'

class AgentScraper:
    def __init__(self, input_csv: str, urls: List[str], output_csv: str):
        self.input_csv = input_csv
        self.urls = urls
        self.output_csv = output_csv
        self.agents = []
        self.contact_info = {}
        self.setup_selenium()
        # Use configuration values
        self.CONTEXT_WINDOW = config.CONTEXT_WINDOW
        self.MAX_DISTANCE = config.MAX_DISTANCE

    def setup_selenium(self):
        """Initialize Selenium WebDriver with appropriate options."""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(options=chrome_options)

    def read_agents(self) -> List[Dict]:
        """Read agent information from the input CSV file."""
        try:
            with open(self.input_csv, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                return list(reader)
        except Exception as e:
            logging.error(f"Error reading input CSV: {e}")
            raise

    def find_contact_info_near_text(self, text: str, name: str) -> Tuple[Optional[str], Optional[str]]:
        """Find contact information near a specific text in a string."""
        name_index = text.lower().find(name.lower())
        if name_index == -1:
            return None, None

        # Define the context window around the name
        start_idx = max(0, name_index - self.CONTEXT_WINDOW)
        end_idx = min(len(text), name_index + len(name) + self.CONTEXT_WINDOW)
        context = text[start_idx:end_idx]

        # Look for emails and phones in the context
        emails = re.findall(EMAIL_PATTERN, context)
        phones = re.findall(PHONE_PATTERN, context)

        return (emails[0] if emails else None, phones[0] if phones else None)

    def get_text_with_structure(self, soup: BeautifulSoup) -> List[Tuple[str, str]]:
        """Extract text from HTML while preserving some structure information."""
        text_with_structure = []
        
        def process_node(node):
            if isinstance(node, NavigableString):
                text = node.strip()
                if text:
                    # Get the parent tag name if it exists
                    parent_tag = node.parent.name if node.parent else 'text'
                    text_with_structure.append((text, parent_tag))
            elif isinstance(node, Tag):
                # Process child nodes
                for child in node.children:
                    process_node(child)

        process_node(soup)
        return text_with_structure

    def scrape_url(self, url: str) -> Tuple[List[Tuple[str, str, str]], List[Tuple[str, str, str]]]:
        """Scrape a single URL for email addresses and phone numbers with context."""
        contact_info = []
        
        try:
            # Try with requests first
            response = requests.get(url, timeout=TIMEOUT)
            response.raise_for_status()
            content = response.text
            
            # If JavaScript is required, use Selenium
            if 'javascript' in response.headers.get('content-type', '').lower():
                self.driver.get(url)
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                content = self.driver.page_source

            # Parse HTML with BeautifulSoup
            soup = BeautifulSoup(content, 'html.parser')
            text_with_structure = self.get_text_with_structure(soup)
            
            # Combine text with structure information
            full_text = ' '.join(text for text, _ in text_with_structure)
            
            # Extract all emails and phones with their context
            for email in re.finditer(EMAIL_PATTERN, full_text):
                start, end = email.span()
                context_start = max(0, start - self.CONTEXT_WINDOW)
                context_end = min(len(full_text), end + self.CONTEXT_WINDOW)
                context = full_text[context_start:context_end]
                contact_info.append(('email', email.group(), context))

            for phone in re.finditer(PHONE_PATTERN, full_text):
                start, end = phone.span()
                context_start = max(0, start - self.CONTEXT_WINDOW)
                context_end = min(len(full_text), end + self.CONTEXT_WINDOW)
                context = full_text[context_start:context_end]
                contact_info.append(('phone', phone.group(), context))
            
            return contact_info
            
        except Exception as e:
            logging.error(f"Error scraping {url}: {e}")
            return []

    def match_agent_contacts(self, agent_name: str, contact_info: List[Tuple[str, str, str]]) -> Tuple[Optional[str], Optional[str]]:
        """Match contact information to an agent based on name proximity and context."""
        best_email = None
        best_phone = None
        best_email_distance = float('inf')
        best_phone_distance = float('inf')

        # Split agent name into parts for more flexible matching
        name_parts = agent_name.lower().split()
        
        for contact_type, value, context in contact_info:
            # Check if any part of the agent's name appears in the context
            context_lower = context.lower()
            name_found = any(part in context_lower for part in name_parts)
            
            if name_found:
                # Calculate distance to the name in the context
                distance = len(context) // 2  # Approximate distance to name
                
                if contact_type == 'email' and distance < best_email_distance:
                    best_email = value
                    best_email_distance = distance
                elif contact_type == 'phone' and distance < best_phone_distance:
                    best_phone = value
                    best_phone_distance = distance

        return best_email, best_phone

    def process_websites(self):
        """Process all websites and collect contact information."""
        for url in self.urls:
            logging.info(f"Processing website: {url}")
            contact_info = self.scrape_url(url)
            
            for agent in self.agents:
                agent_name = agent['Name']
                email, phone = self.match_agent_contacts(agent_name, contact_info)
                
                if email or phone:
                    self.contact_info[agent_name] = {
                        'email': email,
                        'phone': phone
                    }
            
            time.sleep(DELAY_BETWEEN_REQUESTS)

    def write_output(self):
        """Write results to the output CSV file."""
        try:
            with open(self.output_csv, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Name', 'Email', 'Phone'])
                
                for agent in self.agents:
                    agent_name = agent['Name']
                    contact = self.contact_info.get(agent_name, {})
                    writer.writerow([
                        agent_name,
                        contact.get('email', ''),
                        contact.get('phone', '')
                    ])
        except Exception as e:
            logging.error(f"Error writing output CSV: {e}")
            raise

    def run(self):
        """Main execution method."""
        try:
            self.agents = self.read_agents()
            self.process_websites()
            self.write_output()
            logging.info("Scraping completed successfully!")
        except Exception as e:
            logging.error(f"Error during execution: {e}")
        finally:
            self.driver.quit()

def main():
    parser = argparse.ArgumentParser(description='Scrape agent contact information from websites')
    parser.add_argument('--input', default=config.INPUT_CSV, help='Input CSV file with agent names')
    parser.add_argument('--output', default=config.OUTPUT_CSV, help='Output CSV file for results')
    parser.add_argument('--urls', nargs='+', help='List of URLs to scrape (overrides config.py)')
    args = parser.parse_args()

    # Use command line arguments or fall back to config values
    urls = args.urls if args.urls else config.URLS
    
    if not urls:
        logging.error("No URLs provided. Please add URLs to config.py or provide them as command line arguments.")
        return

    logging.info(f"Starting scraper with {len(urls)} URLs")
    logging.info(f"Input file: {args.input}")
    logging.info(f"Output file: {args.output}")
    
    scraper = AgentScraper(args.input, urls, args.output)
    scraper.run()

if __name__ == "__main__":
    main() 