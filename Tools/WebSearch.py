"""
Web Search Module
This module combines web search functionality with content extraction capabilities.
It provides a unified interface for searching the web and extracting content from results.
"""

import sys
import os
import json
import time
from typing import List, Dict, Optional, Union
from datetime import datetime
from urllib.parse import urljoin, urlparse

# Add the Tools directory to the path
sys.path.append(os.path.dirname(__file__))

from DuckDuckGoSearch import DuckDuckGoSearcher
from WebContentExtractor import WebContentExtractor


class WebSearcher:
    """
    A unified web search and content extraction class that combines
    DuckDuckGo search with web content extraction capabilities.
    """
    
    def __init__(self, timeout: int = 30):
        """
        Initialize the WebSearcher
        
        Args:
            timeout (int): Request timeout in seconds (default: 30)
        """
        self.searcher = DuckDuckGoSearcher()
        self.extractor = WebContentExtractor(timeout=timeout)
        self.timeout = timeout
    
    def search(self, query: str, max_results: int = 10, safe_search: str = "moderate") -> List[Dict[str, str]]:
        """
        Search for a query using DuckDuckGo
        
        Args:
            query (str): The search query
            max_results (int): Maximum number of results to return (default: 10)
            safe_search (str): Safe search setting - "strict", "moderate", or "off"
        
        Returns:
            List[Dict[str, str]]: List of search results with title, url, and snippet
        """
        return self.searcher.search(query, max_results, safe_search)
    
    def extract_content(self, url: str, include_comments: bool = False, 
                       include_tables: bool = True, include_images: bool = False) -> Optional[Dict[str, str]]:
        """
        Extract content from a single URL
        
        Args:
            url (str): URL of the web page
            include_comments (bool): Whether to include comments (default: False)
            include_tables (bool): Whether to include tables (default: True)
            include_images (bool): Whether to include image descriptions (default: False)
        
        Returns:
            Optional[Dict[str, str]]: Extracted content with metadata
        """
        return self.extractor.extract_content(url, include_comments, include_tables, include_images)
    
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
        return self.extractor.extract_content_batch(urls, delay, max_retries)
    
    def search_and_extract(self, query: str, max_results: int = 5, 
                          extract_count: int = 3, delay: float = 1.0,
                          include_comments: bool = False, include_tables: bool = True,
                          include_images: bool = False) -> Dict[str, List[Dict]]:
        """
        Search for a query and extract content from the top results
        
        Args:
            query (str): The search query
            max_results (int): Maximum number of search results to get (default: 5)
            extract_count (int): Number of top results to extract content from (default: 3)
            delay (float): Delay between extraction requests in seconds (default: 1.0)
            include_comments (bool): Whether to include comments in extraction (default: False)
            include_tables (bool): Whether to include tables in extraction (default: True)
            include_images (bool): Whether to include image descriptions (default: False)
        
        Returns:
            Dict[str, List[Dict]]: Dictionary containing 'search_results' and 'extracted_contents'
        """
        # Perform the search
        search_results = self.search(query, max_results)
        
        if not search_results:
            return {
                'search_results': [],
                'extracted_contents': []
            }
        
        # Extract URLs for content extraction
        urls_to_extract = [result['url'] for result in search_results[:extract_count]]
        
        # Extract content from URLs
        extracted_contents = []
        for i, url in enumerate(urls_to_extract):
            content = self.extract_content(url, include_comments, include_tables, include_images)
            
            if content:
                # Add metadata
                content['source_url'] = url
                content['extraction_order'] = i + 1
                content['extraction_timestamp'] = datetime.now().isoformat()
                content['search_query'] = query
                extracted_contents.append(content)
            else:
                # Add failed extraction record
                failed_content = {
                    'source_url': url,
                    'extraction_order': i + 1,
                    'extraction_timestamp': datetime.now().isoformat(),
                    'search_query': query,
                    'status': 'failed',
                    'error': 'Failed to extract content from URL',
                    'title': None,
                    'author': None,
                    'date': None,
                    'content': None,
                    'content_length': 0,
                    'language': None,
                    'sitename': None
                }
                extracted_contents.append(failed_content)
            
            # Add delay between requests (except for the last one)
            if i < len(urls_to_extract) - 1:
                time.sleep(delay)
        
        return {
            'search_results': search_results,
            'extracted_contents': extracted_contents
        }
    
    def search_and_extract_batch(self, query: str, max_results: int = 5, 
                               extract_count: int = 3, delay: float = 1.0,
                               max_retries: int = 3) -> Dict[str, List[Dict]]:
        """
        Search for a query and extract content using batch processing
        
        Args:
            query (str): The search query
            max_results (int): Maximum number of search results to get (default: 5)
            extract_count (int): Number of top results to extract content from (default: 3)
            delay (float): Delay between extraction requests in seconds (default: 1.0)
            max_retries (int): Maximum number of retries per URL (default: 3)
        
        Returns:
            Dict[str, List[Dict]]: Dictionary containing 'search_results' and 'extracted_contents'
        """
        # Perform the search
        search_results = self.search(query, max_results)
        
        if not search_results:
            return {
                'search_results': [],
                'extracted_contents': []
            }
        
        # Extract URLs for content extraction
        urls_to_extract = [result['url'] for result in search_results[:extract_count]]
        
        # Use batch extraction
        extracted_contents = self.extract_content_batch(urls_to_extract, delay, max_retries)
        
        # Add metadata to extracted contents
        for i, content in enumerate(extracted_contents):
            if content:
                content['source_url'] = urls_to_extract[i] if i < len(urls_to_extract) else None
                content['extraction_order'] = i + 1
                content['extraction_timestamp'] = datetime.now().isoformat()
                content['search_query'] = query
        
        return {
            'search_results': search_results,
            'extracted_contents': extracted_contents
        }
    
    def extract_from_search_results(self, search_results: List[Dict], 
                                  extract_count: int = None,
                                  method: str = "sequential") -> List[Dict]:
        """
        Extract content from existing search results
        
        Args:
            search_results (List[Dict]): List of search results with URLs
            extract_count (int): Number of results to extract from (default: all)
            method (str): Extraction method - "sequential" or "batch" (default: "sequential")
        
        Returns:
            List[Dict]: List of extracted content
        """
        if not search_results:
            return []
        
        # Determine how many results to extract
        if extract_count is None:
            extract_count = len(search_results)
        else:
            extract_count = min(extract_count, len(search_results))
        
        # Extract URLs
        urls = [result['url'] for result in search_results[:extract_count]]
        
        # Choose extraction method
        if method == "batch":
            return self.extract_content_batch(urls)
        else:
            # Sequential extraction
            extracted_contents = []
            for i, url in enumerate(urls):
                content = self.extract_content(url)
                if content:
                    content['source_url'] = url
                    content['extraction_order'] = i + 1
                    content['extraction_timestamp'] = datetime.now().isoformat()
                    extracted_contents.append(content)
                
                # Add delay between requests (except for the last one)
                if i < len(urls) - 1:
                    time.sleep(1.0)
            
            return extracted_contents
    
    def quick_search(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Quick search without content extraction
        
        Args:
            query (str): The search query
            max_results (int): Maximum number of results (default: 10)
        
        Returns:
            List[Dict]: Search results
        """
        return self.search(query, max_results)
    
    def smart_extract(self, url_or_urls: Union[str, List[str]], 
                     method: str = "auto") -> Union[Dict, List[Dict]]:
        """
        Smart extraction that automatically chooses between single and batch extraction
        
        Args:
            url_or_urls (Union[str, List[str]]): Single URL or list of URLs
            method (str): Extraction method - "auto", "single", or "batch" (default: "auto")
        
        Returns:
            Union[Dict, List[Dict]]: Extracted content
        """
        if isinstance(url_or_urls, str):
            # Single URL
            return self.extract_content(url_or_urls)
        elif isinstance(url_or_urls, list):
            # Multiple URLs
            if method == "auto":
                # Use batch if more than 3 URLs, otherwise sequential
                if len(url_or_urls) > 3:
                    return self.extract_content_batch(url_or_urls)
                else:
                    return [self.extract_content(url) for url in url_or_urls if self.extract_content(url)]
            elif method == "batch":
                return self.extract_content_batch(url_or_urls)
            else:
                return [self.extract_content(url) for url in url_or_urls if self.extract_content(url)]
        else:
            raise ValueError("url_or_urls must be a string or list of strings")


# Convenience functions for backward compatibility
def search_and_extract(query: str, max_results: int = 5, extract_count: int = 3) -> Dict[str, List[Dict]]:
    """
    Convenience function for search and extract
    """
    searcher = WebSearcher()
    return searcher.search_and_extract(query, max_results, extract_count)


def quick_search(query: str, max_results: int = 10) -> List[Dict]:
    """
    Convenience function for quick search
    """
    searcher = WebSearcher()
    return searcher.quick_search(query, max_results)


def extract_content(url: str) -> Optional[Dict[str, str]]:
    """
    Convenience function for single content extraction
    """
    searcher = WebSearcher()
    return searcher.extract_content(url)


def extract_content_batch(urls: List[str], delay: float = 1.0) -> List[Dict[str, str]]:
    """
    Convenience function for batch content extraction
    """
    searcher = WebSearcher()
    return searcher.extract_content_batch(urls, delay)


# Example usage
if __name__ == "__main__":
    # Example usage of the WebSearcher class
    searcher = WebSearcher()
    
    # Test search
    print("🔍 Testing search functionality...")
    results = searcher.search("Python web scraping", max_results=5)
    print(f"Found {len(results)} results")
    
    # Test search and extract
    print("\n🌐 Testing search and extract functionality...")
    combined_results = searcher.search_and_extract("Python web scraping", max_results=5, extract_count=2)
    print(f"Search results: {len(combined_results['search_results'])}")
    print(f"Extracted contents: {len(combined_results['extracted_contents'])}")
    
    # Test batch extraction
    if results:
        print("\n📄 Testing batch extraction...")
        urls = [result['url'] for result in results[:2]]
        batch_results = searcher.extract_content_batch(urls, delay=1.0)
        print(f"Batch extracted: {len(batch_results)} contents")
