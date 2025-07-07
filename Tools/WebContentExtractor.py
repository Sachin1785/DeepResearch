"""
Web Content Extractor Module
This module provides functionality to extract and scrape text content from web pages
using Trafilatura library.
"""

import requests
from typing import Optional, Dict, List
import trafilatura
from trafilatura.settings import use_config
from urllib.parse import urljoin, urlparse
import time
import logging


class WebContentExtractor:
    """
    A class to extract content from web pages using Trafilatura
    """
    
    def __init__(self, timeout: int = 30):
        """
        Initialize the WebContentExtractor
        
        Args:
            timeout (int): Request timeout in seconds (default: 30)
        """
        self.timeout = timeout
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Configure trafilatura
        self.config = use_config()
        self.config.set('DEFAULT', 'EXTRACTION_TIMEOUT', str(timeout))
        
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def extract_content(self, url: str, include_comments: bool = False, 
                       include_tables: bool = True, include_images: bool = False) -> Optional[Dict[str, str]]:
        """
        Extract content from a single web page
        
        Args:
            url (str): URL of the web page
            include_comments (bool): Whether to include comments (default: False)
            include_tables (bool): Whether to include tables (default: True)
            include_images (bool): Whether to include image descriptions (default: False)
        
        Returns:
            Optional[Dict[str, str]]: Extracted content with metadata
        """
        try:
            # Download the page
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            # Extract content using trafilatura
            extracted_text = trafilatura.extract(
                response.text,
                include_comments=include_comments,
                include_tables=include_tables,
                include_images=include_images,
                config=self.config
            )
            
            if not extracted_text:
                self.logger.warning(f"No content extracted from {url}")
                return None
            
            # Extract metadata
            metadata = trafilatura.extract_metadata(response.text)
            
            result = {
                'url': url,
                'content': extracted_text,
                'title': metadata.title if metadata else '',
                'author': metadata.author if metadata and metadata.author else '',
                'date': metadata.date if metadata and metadata.date else '',
                'description': metadata.description if metadata and metadata.description else '',
                'sitename': metadata.sitename if metadata and metadata.sitename else '',
                'language': metadata.language if metadata and metadata.language else '',
                'content_length': len(extracted_text)
            }
            
            return result
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching {url}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error extracting content from {url}: {e}")
            return None
    
    def extract_content_batch(self, urls: List[str], delay: float = 1.0, 
                            max_retries: int = 3) -> List[Dict[str, str]]:
        """
        Extract content from multiple URLs with delay between requests
        
        Args:
            urls (List[str]): List of URLs to extract content from
            delay (float): Delay between requests in seconds (default: 1.0)
            max_retries (int): Maximum number of retries per URL (default: 3)
        
        Returns:
            List[Dict[str, str]]: List of extracted content
        """
        results = []
        
        for url in urls:
            self.logger.info(f"Extracting content from: {url}")
            
            # Retry mechanism
            for attempt in range(max_retries):
                content = self.extract_content(url)
                if content:
                    results.append(content)
                    break
                elif attempt < max_retries - 1:
                    self.logger.warning(f"Retry {attempt + 1} for {url}")
                    time.sleep(delay)
                else:
                    self.logger.error(f"Failed to extract content from {url} after {max_retries} attempts")
            
            # Add delay between requests (except for the last one)
            if url != urls[-1]:
                time.sleep(delay)
        
        return results
    
    def extract_with_fallback(self, url: str) -> Optional[Dict[str, str]]:
        """
        Extract content with fallback methods if trafilatura fails
        
        Args:
            url (str): URL to extract content from
        
        Returns:
            Optional[Dict[str, str]]: Extracted content
        """
        # Try trafilatura first
        content = self.extract_content(url)
        if content:
            return content
        
        # Fallback to basic extraction
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            # Use trafilatura's bare extraction
            extracted_text = trafilatura.extract(
                response.text,
                favor_precision=True,
                include_comments=False,
                include_tables=True
            )
            
            if extracted_text:
                return {
                    'url': url,
                    'content': extracted_text,
                    'title': '',
                    'author': '',
                    'date': '',
                    'description': '',
                    'sitename': '',
                    'language': '',
                    'content_length': len(extracted_text),
                    'extraction_method': 'fallback'
                }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Fallback extraction failed for {url}: {e}")
            return None
    
    def extract_text_only(self, url: str) -> Optional[str]:
        """
        Extract only the main text content from a URL
        
        Args:
            url (str): URL to extract text from
        
        Returns:
            Optional[str]: Extracted text content
        """
        content = self.extract_content(url)
        return content['content'] if content else None
    
    def extract_with_links(self, url: str) -> Optional[Dict[str, any]]:
        """
        Extract content along with all links found in the page
        
        Args:
            url (str): URL to extract content from
        
        Returns:
            Optional[Dict[str, any]]: Content with extracted links
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            # Extract main content
            content = trafilatura.extract(response.text, config=self.config)
            if not content:
                return None
            
            # Extract links
            links = trafilatura.extract_links(response.text)
            
            # Extract metadata
            metadata = trafilatura.extract_metadata(response.text)
            
            result = {
                'url': url,
                'content': content,
                'links': links if links else [],
                'title': metadata.title if metadata else '',
                'author': metadata.author if metadata and metadata.author else '',
                'date': metadata.date if metadata and metadata.date else '',
                'description': metadata.description if metadata and metadata.description else '',
                'content_length': len(content)
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error extracting content with links from {url}: {e}")
            return None
    
    def is_valid_url(self, url: str) -> bool:
        """
        Check if a URL is valid and accessible
        
        Args:
            url (str): URL to validate
        
        Returns:
            bool: True if URL is valid and accessible
        """
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return False
            
            response = requests.head(url, headers=self.headers, timeout=10)
            return response.status_code == 200
            
        except Exception:
            return False


# Example usage
if __name__ == "__main__":
    extractor = WebContentExtractor()
    
    # Example URLs
    test_urls = [
        "https://en.wikipedia.org/wiki/Web_scraping",
        "https://realpython.com/beautiful-soup-web-scraper-python/"
    ]
    
    print("Extracting content from URLs:")
    for url in test_urls:
        print(f"\n--- Extracting from: {url} ---")
        content = extractor.extract_content(url)
        if content:
            print(f"Title: {content['title']}")
            print(f"Author: {content['author']}")
            print(f"Date: {content['date']}")
            print(f"Content length: {content['content_length']} characters")
            print(f"Content preview: {content['content'][:200]}...")
        else:
            print("Failed to extract content")
    
    print("\n--- Batch extraction ---")
    batch_results = extractor.extract_content_batch(test_urls, delay=2.0)
    print(f"Successfully extracted content from {len(batch_results)} URLs")
