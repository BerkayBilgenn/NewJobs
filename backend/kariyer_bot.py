"""
Kariyer.net Job Scraper
Uses HTTP requests to scrape public job listings.
"""

import requests
from bs4 import BeautifulSoup
from typing import Optional
import urllib.parse
import time
import random


class KariyerNetBot:
    """
    Kariyer.net Job Scraper using HTTP requests.
    
    Features:
    - NO browser window - completely invisible
    - Fast - direct HTTP requests
    - Extracts job title, company, link, and description
    """
    
    def __init__(self):
        """Initialize the scraper with proper headers."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
        })
    
    def search_jobs(self, role: str, location: str = "istanbul", max_jobs: int = 50) -> list[dict]:
        """
        Search for jobs on Kariyer.net.
        
        Args:
            role: Job title/role to search for
            location: Job location (default: istanbul)
            max_jobs: Maximum number of jobs to scrape
        
        Returns:
            List of job dictionaries
        """
        print(f"🔍 Kariyer.net'te aranıyor: {role} - {location}")
        
        jobs = []
        
        # Kariyer.net URL format
        # https://www.kariyer.net/is-ilanlari?kw=python&loc=istanbul
        encoded_role = urllib.parse.quote(role.lower())
        encoded_location = urllib.parse.quote(location.lower())
        
        # Fetch multiple pages
        for page in range(1, 9):  # Up to 8 pages
            if len(jobs) >= max_jobs:
                break
            
            search_url = f"https://www.kariyer.net/is-ilanlari?kw={encoded_role}&loc={encoded_location}&cp={page}"
            
            try:
                print(f"📡 Sayfa {page} getiriliyor...")
                response = self.session.get(search_url, timeout=15)
                
                if response.status_code != 200:
                    print(f"⚠️ Sayfa {page} - HTTP {response.status_code}")
                    continue
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find job cards - Kariyer.net structure
                job_cards = soup.find_all('div', class_='list-items')
                
                if not job_cards:
                    job_cards = soup.find_all('div', {'class': lambda x: x and 'job-item' in str(x)})
                
                if not job_cards:
                    # Try to find job listings in any list structure
                    job_cards = soup.find_all('a', {'class': lambda x: x and 'k-ad-card' in str(x)})
                
                if not job_cards:
                    job_cards = soup.select('.listing-list .list-items, .job-list-item, .job-card')
                
                print(f"📋 Sayfa {page}'de {len(job_cards)} ilan bulundu")
                
                for card in job_cards:
                    if len(jobs) >= max_jobs:
                        break
                    
                    job_data = self._extract_job_data(card, role)
                    if job_data:
                        # Check for duplicates
                        if not any(j['title'] == job_data['title'] and j['company'] == job_data['company'] for j in jobs):
                            jobs.append(job_data)
                            print(f"  ✓ {job_data['title']} - {job_data['company']}")
                
                # Small delay between pages
                time.sleep(random.uniform(0.3, 0.6))
                
            except Exception as e:
                print(f"❌ Sayfa {page} hatası: {e}")
                continue
        
        print(f"✅ Kariyer.net'ten {len(jobs)} ilan çekildi")
        return jobs
    
    def _extract_job_data(self, card, search_role: str) -> Optional[dict]:
        """Extract job data from a card element."""
        try:
            # Find title
            title = None
            title_elem = card.find(['h2', 'h3', 'a'], class_=lambda x: x and 'title' in str(x).lower())
            if title_elem:
                title = title_elem.get_text(strip=True)
            
            if not title:
                a_tag = card.find('a', href=True)
                if a_tag:
                    title = a_tag.get_text(strip=True)
            
            if not title or len(title) < 3 or '*' in title:
                title = search_role
            
            # Find company
            company = "Şirket"
            company_elem = card.find(['span', 'div', 'a'], class_=lambda x: x and 'company' in str(x).lower())
            if company_elem:
                company = company_elem.get_text(strip=True)
            
            if not company or '*' in company:
                company = "Şirket"
            
            # Find link
            link = "#"
            link_elem = card.find('a', href=True)
            if link_elem:
                href = link_elem.get('href', '')
                if href.startswith('/'):
                    link = f"https://www.kariyer.net{href}"
                elif href.startswith('http'):
                    link = href
            
            # Find location
            location = ""
            loc_elem = card.find(['span', 'div'], class_=lambda x: x and 'location' in str(x).lower())
            if loc_elem:
                location = loc_elem.get_text(strip=True)
            
            return {
                'title': title,
                'company': company,
                'link': link,
                'image_url': None,
                'description': location,  # Use location as initial description
            }
            
        except Exception as e:
            return None
    
    def close(self):
        """Close the session."""
        self.session.close()
        print("🔒 Kariyer.net scraper kapatıldı")


# For testing
if __name__ == "__main__":
    bot = KariyerNetBot()
    try:
        jobs = bot.search_jobs("Python Developer", "istanbul", max_jobs=10)
        print("\n--- SONUÇLAR ---")
        for job in jobs:
            print(f"• {job['title']} @ {job['company']}")
            print(f"  Link: {job['link']}\n")
    finally:
        bot.close()
