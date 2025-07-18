"""
DuckDuckGo Web Search Module
This module provides functionality to search the web using DuckDuckGo's free API
and retrieve search result links.
"""

import requests
from typing import List, Dict, Optional
import json
import time
from urllib.parse import quote_plus


class DuckDuckGoSearcher:
    """
    A class to perform web searches using DuckDuckGo's instant answer API
    """
    
    def __init__(self):
        self.base_url = "https://api.duckduckgo.com/"
        self.search_url = "https://html.duckduckgo.com/html/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def search(self, query: str, max_results: int = 10, safe_search: str = "moderate") -> List[Dict[str, str]]:
        """
        Search DuckDuckGo for the given query and return a list of results
        
        Args:
            query (str): The search query
            max_results (int): Maximum number of results to return (default: 10)
            safe_search (str): Safe search setting - "strict", "moderate", or "off" (default: "moderate")
        
        Returns:
            List[Dict[str, str]]: List of search results with title, url, and snippet
        """
        try:
            # Use the HTML search endpoint for better results
            encoded_query = quote_plus(query)
            search_url = f"{self.search_url}?q={encoded_query}"
            
            response = requests.get(search_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            # Parse the HTML response to extract search results
            results = self._parse_html_results(response.text, max_results)
            
            return results
            
        except requests.exceptions.RequestException as e:
            print(f"Error performing search: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error: {e}")
            return []
    
    def _parse_html_results(self, html_content: str, max_results: int) -> List[Dict[str, str]]:
        """
        Parse HTML content to extract search results
        
        Args:
            html_content (str): HTML content from DuckDuckGo
            max_results (int): Maximum number of results to extract
        
        Returns:
            List[Dict[str, str]]: Parsed search results
        """
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(html_content, 'html.parser')
        results = []
        
        # Find all result containers - try multiple class patterns
        result_containers = soup.find_all('div', class_='result')
        if not result_containers:
            result_containers = soup.find_all('div', class_='web-result')
        
        for container in result_containers[:max_results]:
            try:
                # Extract title and URL
                title_element = container.find('a', class_='result__a')
                if title_element:
                    title = title_element.get_text(strip=True)
                    url = title_element.get('href', '')
                    
                    # Extract snippet - updated to get text content instead of href
                    snippet_element = container.find('a', class_='result__snippet')
                    snippet = ""
                    if snippet_element:
                        snippet = snippet_element.get_text(strip=True)
                    
                    # Clean up the snippet by removing HTML tags
                    if snippet:
                        # Remove <b> tags and other HTML formatting
                        snippet = snippet.replace('<b>', '').replace('</b>', '')
                    
                    if title and url and url.startswith('http'):
                        results.append({
                            'title': title,
                            'url': url,
                            'snippet': snippet
                        })
            except Exception as e:
                print(f"Error parsing result: {e}")
                continue
        
        return results
    
    def instant_answer(self, query: str) -> Optional[Dict]:
        """
        Get instant answer from DuckDuckGo API
        
        Args:
            query (str): The search query
        
        Returns:
            Optional[Dict]: Instant answer data if available
        """
        try:
            params = {
                'q': query,
                'format': 'json',
                'no_html': '1',
                'skip_disambig': '1'
            }
            
            response = requests.get(self.base_url, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('AbstractText') or data.get('Answer'):
                return {
                    'abstract': data.get('AbstractText', ''),
                    'answer': data.get('Answer', ''),
                    'source': data.get('AbstractSource', ''),
                    'url': data.get('AbstractURL', '')
                }
            
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"Error getting instant answer: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            return None
    
    def search_with_delay(self, queries: List[str], delay: float = 1.0, max_results: int = 10) -> Dict[str, List[Dict[str, str]]]:
        """
        Perform multiple searches with delay between requests
        
        Args:
            queries (List[str]): List of search queries
            delay (float): Delay between requests in seconds (default: 1.0)
            max_results (int): Maximum results per query (default: 10)
        
        Returns:
            Dict[str, List[Dict[str, str]]]: Dictionary with query as key and results as value
        """
        all_results = {}
        
        for query in queries:
            print(f"Searching for: {query}")
            results = self.search(query, max_results)
            all_results[query] = results
            
            if query != queries[-1]:  # Don't delay after the last query
                time.sleep(delay)
        
        return all_results


# Example usage
if __name__ == "__main__":
    searcher = DuckDuckGoSearcher()
    
    # Example search
    query = "Python web scraping"
    results = searcher.search(query, max_results=5)
    
    print(f"Search results for '{query}':")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['title']}")
        print(f"   URL: {result['url']}")
        print(f"   Snippet: {result['snippet']}")
        print()
    
    # Example instant answer
    instant = searcher.instant_answer("What is Python?")
    if instant:
        print("Instant Answer:")
        print(f"Answer: {instant['answer']}")
        print(f"Abstract: {instant['abstract']}")
        print(f"Source: {instant['source']}")
