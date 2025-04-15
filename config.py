# List of websites to scrape
URLS = [
    # Add your website URLs here, for example:
    "https://example1.com",
    "https://example2.com",
    # Add more URLs as needed
]

# Input and output file paths
INPUT_CSV = "agents.csv"
OUTPUT_CSV = "agents_with_contacts.csv"

# Scraping configuration
DELAY_BETWEEN_REQUESTS = 2  # seconds
MAX_RETRIES = 3
TIMEOUT = 30
CONTEXT_WINDOW = 200  # characters to look before and after the name
MAX_DISTANCE = 500    # maximum distance to look for contact info 