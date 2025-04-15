# LMU Alumni Network

A web application that allows searching through Loyola Marymount University alumni profiles to find information about their current roles, companies, and industries.

## Features

- Search alumni by name, role, company, or industry
- Modern, responsive UI
- Real-time search results
- Automated data collection from public LinkedIn profiles
- SQLite database for storing alumni information

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd lmu-alumni-network
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Initialize the database:
```bash
python app.py
```

5. Run the application:
```bash
flask run
```

The application will be available at `http://localhost:5000`

## Usage

1. Open your web browser and navigate to `http://localhost:5000`
2. Use the search bar to look up alumni by:
   - Name
   - Current role
   - Company
   - Industry

## Important Notes

- This application respects LinkedIn's terms of service and implements appropriate rate limiting
- The scraper uses a headless browser to collect publicly available information
- Make sure to comply with privacy regulations and data protection laws
- The application includes appropriate delays between requests to avoid overwhelming LinkedIn's servers

## Technical Details

- Backend: Python Flask
- Frontend: HTML, JavaScript, Tailwind CSS
- Database: SQLite with SQLAlchemy
- Web Scraping: Selenium with Chrome WebDriver
- Additional libraries: BeautifulSoup4, Requests

## Legal Disclaimer

This tool is intended for educational purposes only. Users are responsible for ensuring their use of this tool complies with LinkedIn's terms of service and applicable laws regarding data collection and privacy. 