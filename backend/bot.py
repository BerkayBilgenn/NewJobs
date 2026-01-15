"""
LinkedIn Job Scraper - Browserless Version
Uses HTTP requests instead of Selenium - NO BROWSER VISIBLE!

This scrapes LinkedIn's public job listings page which doesn't require login.
"""

import requests
from bs4 import BeautifulSoup
from typing import Optional
import urllib.parse
import time
import random


class LinkedInBot:
    """
    LinkedIn Job Scraper using HTTP requests.
    
    Features:
    - NO browser window - completely invisible
    - Fast - direct HTTP requests
    - No login required - uses public job search
    - Extracts job title, company, link, and image
    """
    
    def __init__(self, headless: bool = True):
        """
        Initialize the scraper.
        
        Args:
            headless: Ignored - always headless since no browser is used
        """
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def login(self) -> bool:
        """No login needed for public job search."""
        return True
    
    def search_jobs(self, role: str, location: str = "Istanbul", max_jobs: int = 10) -> list[dict]:
        """
        Search for jobs on LinkedIn's public job board.
        
        Args:
            role: Job title/role to search for (e.g., "Software Engineer")
            location: Job location (default: Istanbul)
            max_jobs: Maximum number of jobs to scrape (default: 10)
        
        Returns:
            List of job dictionaries with title, company, link, image_url
        """
        print(f"🔍 Searching: {role} in {location}")
        
        # Build search URL - LinkedIn public jobs page
        encoded_role = urllib.parse.quote(role)
        encoded_location = urllib.parse.quote(location)
        
        jobs = []
        
        # Fetch multiple pages to get more jobs (up to 200)
        page_starts = list(range(0, 200, 25))  # [0, 25, 50, 75, 100, 125, 150, 175]
        for page_start in page_starts:
            if len(jobs) >= max_jobs:
                break
                
            search_url = f"https://www.linkedin.com/jobs/search?keywords={encoded_role}&location={encoded_location}&start={page_start}"
            
            try:
                # Make request to LinkedIn
                print(f"📡 Fetching page {page_start // 25 + 1}...")
                response = self.session.get(search_url, timeout=15)
                response.raise_for_status()
                
                # Parse HTML
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find job cards - try multiple selectors
                job_cards = soup.find_all('div', class_='base-card')
                
                if not job_cards:
                    job_cards = soup.find_all('li', class_='jobs-search-results__list-item')
                
                if not job_cards:
                    job_cards = soup.find_all('div', {'class': lambda x: x and 'job-search-card' in x})
                
                # Also try to find by data attributes
                if not job_cards:
                    job_cards = soup.find_all('div', {'data-entity-urn': True})
                
                print(f"📋 Found {len(job_cards)} job cards on page {page_start // 25 + 1}")
                
                for card in job_cards:
                    if len(jobs) >= max_jobs:
                        break
                    try:
                        job_data = self._extract_job_data(card)
                        if job_data and job_data.get('title'):
                            title = job_data['title']
                            company = job_data['company']
                            
                            # If title is obfuscated (has asterisks), use the search role instead
                            if '*' in title:
                                job_data['title'] = role  # Use the searched role as title
                                title = role
                            
                            # If company is obfuscated, just say "Şirket"
                            if '*' in company:
                                job_data['company'] = "Şirket"
                                company = "Şirket"
                            
                            if len(title) < 3 or title.count(' ') > 10:
                                continue
                            # Check for duplicates
                            if any(j['title'] == title and j['company'] == company for j in jobs):
                                continue
                            jobs.append(job_data)
                            print(f"  ✓ {job_data['title']} at {job_data['company']}")
                    except Exception as e:
                        continue
                
                # Small delay between pages
                time.sleep(random.uniform(0.3, 0.5))
                
            except requests.RequestException as e:
                print(f"❌ Page {page_start // 25 + 1} failed: {e}")
                continue
        
        # Fetch job descriptions for each job
        print("📝 Fetching job descriptions...")
        for i, job in enumerate(jobs):
            if job.get('link') and job['link'] != '#':
                desc = self._fetch_job_description(job['link'])
                if desc:
                    job['description'] = desc
                    print(f"  ✓ Got description for job {i+1}")
                else:
                    print(f"  ⏭️ No description for job {i+1}")
                # Small delay between requests
                time.sleep(random.uniform(0.2, 0.4))
        
        print(f"✅ Successfully scraped {len(jobs)} jobs")
        return jobs
    
    def _fetch_job_description(self, job_url: str) -> str:
        """
        Fetch the full job description from a job detail page.
        
        Args:
            job_url: LinkedIn job URL
        
        Returns:
            Job description text or empty string
        """
        try:
            response = self.session.get(job_url, timeout=10)
            if response.status_code != 200:
                return ""
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Try multiple selectors for job description
            description_selectors = [
                ('div', 'description__text'),
                ('div', 'show-more-less-html__markup'),
                ('div', 'job-description'),
                ('section', 'description'),
            ]
            
            for tag, class_name in description_selectors:
                elem = soup.find(tag, class_=lambda x: x and class_name in str(x))
                if elem:
                    text = elem.get_text(strip=True, separator=' ')
                    if len(text) > 50:  # Valid description
                        return text[:2000]  # Limit length
            
            # Fallback: find any large text block
            for div in soup.find_all('div', class_=True):
                text = div.get_text(strip=True)
                if 100 < len(text) < 5000 and 'description' in str(div.get('class', [])).lower():
                    return text[:2000]
            
            return ""
            
        except Exception as e:
            print(f"  ⚠️ Description fetch error: {e}")
            return ""
    
    def _search_jobs_alternative(self, role: str, location: str, max_jobs: int) -> list[dict]:
        """Alternative scraping method using different LinkedIn URL structure."""
        print("🔄 Trying alternative search method...")
        
        encoded_role = urllib.parse.quote(role)
        encoded_location = urllib.parse.quote(location)
        
        # Alternative URL format
        alt_url = f"https://www.linkedin.com/jobs/search/?keywords={encoded_role}&location={encoded_location}"
        
        jobs = []
        
        try:
            response = self.session.get(alt_url, timeout=15)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Try to find any job-related elements
            job_elements = soup.find_all(['div', 'li', 'article'], class_=lambda x: x and ('job' in str(x).lower() or 'card' in str(x).lower()))
            
            for elem in job_elements[:max_jobs]:
                # Extract title
                title_elem = elem.find(['h3', 'h4', 'a'], class_=lambda x: x and 'title' in str(x).lower())
                company_elem = elem.find(['h4', 'span', 'a'], class_=lambda x: x and ('company' in str(x).lower() or 'subtitle' in str(x).lower()))
                link_elem = elem.find('a', href=True)
                img_elem = elem.find('img', src=True)
                
                if title_elem:
                    jobs.append({
                        'title': title_elem.get_text(strip=True),
                        'company': company_elem.get_text(strip=True) if company_elem else 'Unknown',
                        'link': link_elem['href'] if link_elem else '#',
                        'image_url': img_elem['src'] if img_elem else None,
                        'description': ''
                    })
                    
        except Exception as e:
            print(f"❌ Alternative method also failed: {e}")
        
        return jobs
    
    def _extract_job_data(self, card) -> Optional[dict]:
        """
        Extract job information from a job card element.
        
        Args:
            card: BeautifulSoup element representing a job card
        
        Returns:
            Dictionary with job data or None if extraction failed
        """
        try:
            # Try multiple selectors for title
            title = None
            title_selectors = [
                ('h3', 'base-search-card__title'),
                ('h3', 'job-card-list__title'),
                ('a', 'base-card__full-link'),
                ('span', 'sr-only'),
            ]
            
            for tag, class_name in title_selectors:
                elem = card.find(tag, class_=lambda x: x and class_name in str(x))
                if elem:
                    title = elem.get_text(strip=True)
                    if title and len(title) > 5:
                        break
            
            if not title:
                # Fallback: get any h3 or link text
                h3 = card.find('h3')
                if h3:
                    title = h3.get_text(strip=True)
            
            if not title:
                return None
            
            # Extract company name
            company = "Unknown"
            company_selectors = [
                ('h4', 'base-search-card__subtitle'),
                ('a', 'hidden-nested-link'),
                ('span', 'job-card-container__company-name'),
            ]
            
            for tag, class_name in company_selectors:
                elem = card.find(tag, class_=lambda x: x and class_name in str(x))
                if elem:
                    company = elem.get_text(strip=True)
                    if company:
                        break
            
            if company == "Unknown":
                h4 = card.find('h4')
                if h4:
                    company = h4.get_text(strip=True)
            
            # Extract link
            link = "#"
            link_elem = card.find('a', href=True)
            if link_elem:
                href = link_elem.get('href', '')
                if href.startswith('/'):
                    link = f"https://www.linkedin.com{href}"
                elif href.startswith('http'):
                    link = href
            
            # Extract image
            image_url = None
            img = card.find('img', src=True)
            if img:
                image_url = img.get('src') or img.get('data-delayed-url')
            
            return {
                'title': title,
                'company': company,
                'link': link,
                'image_url': image_url,
                'description': ''
            }
            
        except Exception as e:
            print(f"Extraction error: {e}")
            return None
    
    def close(self):
        """Close the session."""
        self.session.close()
        print("🔒 Scraper closed")


# For testing
if __name__ == "__main__":
    bot = LinkedInBot()
    try:
        jobs = bot.search_jobs("Python Developer", "Istanbul", max_jobs=5)
        print("\n--- RESULTS ---")
        for job in jobs:
            print(f"• {job['title']} @ {job['company']}")
            print(f"  Link: {job['link']}\n")
    finally:
        bot.close()
