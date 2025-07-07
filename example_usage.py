"""
Example usage of DuckDuckGo Search and Web Content Extractor
This script demonstrates how to use both modules together to:
1. Search for information using DuckDuckGo
2. Extract content from the search results
"""

import sys
import os
import json
from datetime import datetime
sys.path.append(os.path.join(os.path.dirname(__file__), 'Tools'))

from WebSearch import WebSearcher

# All functionality is now available through the WebSearcher class:
# - searcher.search() - Basic search functionality
# - searcher.extract_content() - Extract content from a single URL
# - searcher.extract_content_batch() - Extract content from multiple URLs with batch processing
# - searcher.search_and_extract() - Combined search and extraction
# - searcher.quick_search() - Quick search with default settings


def save_results(query: str, search_results: list, extracted_contents: list, 
                output_dir: str = "searches") -> str:
    """
    Save search results and extracted content to a JSON file
    
    Args:
        query (str): The search query used
        search_results (list): List of search results
        extracted_contents (list): List of extracted content
        output_dir (str): Directory to save results (default: "searches")
    
    Returns:
        str: Path to the saved file or None if failed
    """
    # Create timestamp for filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"search_{timestamp}.json"
    
    # Create output directory if it doesn't exist
    if not os.path.isabs(output_dir):
        output_dir = os.path.join(os.path.dirname(__file__), output_dir)
    
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)
    
    # Prepare data structure
    data = {
        "metadata": {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "total_search_results": len(search_results),
            "total_extracted_contents": len(extracted_contents),
            "search_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        },
        "search_results": search_results,
        "extracted_contents": extracted_contents
    }
    
    # Save to JSON file
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"💾 Search results saved to: {filename}")
        return filepath
    except Exception as e:
        print(f"❌ Error saving search results: {str(e)}")
        return None


def display_results(query: str, search_results: list, extracted_contents: list, max_content_length: int = 500):
    """
    Display search results and extracted content in a formatted way
    
    Args:
        query (str): The search query used
        search_results (list): List of search results
        extracted_contents (list): List of extracted content
        max_content_length (int): Maximum content length to display
    """
    if not search_results:
        print("❌ No search results found.")
        return
    
    print(f"📋 Found {len(search_results)} search results:")
    for i, result in enumerate(search_results, 1):
        print(f"{i}. {result['title']}")
        print(f"   URL: {result['url']}")
        print(f"   Snippet: {result['snippet'][:100]}...")
        print()
    
    # Display extracted content
    print(f"\n📄 Extracted content from top {len(extracted_contents)} results...")
    print("=" * 50)
    
    for i, content in enumerate(extracted_contents, 1):
        print(f"\n🌐 Content from result #{i}:")
        if content.get('status') == 'failed':
            print(f"URL: {content['source_url']}")
            print("❌ Failed to extract content from this URL")
        else:
            print(f"URL: {content['source_url']}")
            print(f"✅ Successfully extracted content:")
            print(f"   Title: {content['title']}")
            print(f"   Author: {content['author']}")
            print(f"   Date: {content['date']}")
            print(f"   Content Length: {content['content_length']} characters")
            print(f"   Language: {content['language']}")
            print(f"   Site: {content['sitename']}")
            
            # Show content preview
            content_preview = content['content'][:max_content_length]
            if len(content['content']) > max_content_length:
                content_preview += "..."
            
            print(f"\n📝 Content Preview:")
            print("-" * 40)
            print(content_preview)
            print("-" * 40)
        
        print("\n" + "="*50)





if __name__ == "__main__":
    # Interactive example usage
    print("🚀 ResearchGenie - Web Search and Content Extraction")
    print("=" * 60)
    
    # Initialize the web searcher
    searcher = WebSearcher()
    
    try:
        # Get search query from user
        query = input("\n🔍 Enter your search query: ").strip()
        
        if not query:
            print("❌ No query provided. Exiting...")
            sys.exit(1)
        
        # Get number of results (optional)
        try:
            max_results_input = input("📊 How many results to search? (default: 5): ").strip()
            max_results = int(max_results_input) if max_results_input else 5
        except ValueError:
            max_results = 5
        
        # Get how many URLs to scrape (optional)
        try:
            scrape_count_input = input("🌐 How many top results to scrape? (default: 3): ").strip()
            scrape_count = int(scrape_count_input) if scrape_count_input else 3
        except ValueError:
            scrape_count = 3
        
        print(f"\n🚀 Starting search and extraction process...")
        print("=" * 60)
        print(f"🔍 Searching for: '{query}'")
        print("=" * 50)
        
        # Use WebSearcher directly - no more wrapper function needed!
        results = searcher.search_and_extract(query, max_results, scrape_count)
        search_results = results['search_results']
        extracted_contents = results['extracted_contents']
        
        # Display results using our display helper function
        display_results(query, search_results, extracted_contents, max_content_length=500)
        
        # Save results
        if search_results:
            print(f"\n💾 Saving search results to JSON file...")
            save_results(query, search_results, extracted_contents)
        
        # Display summary
        if search_results:
            successful_extractions = len([content for content in extracted_contents if content.get('status') != 'failed'])
            print(f"\n📊 Summary:")
            print(f"   🔍 Search Results: {len(search_results)}")
            print(f"   ✅ Successful Extractions: {successful_extractions}")
            print(f"   ❌ Failed Extractions: {len(extracted_contents) - successful_extractions}")
            print(f"   💾 Data saved to JSON file in 'searches' folder")
        
        # Ask if user wants to perform another search
        while True:
            another_search = input("\n🔄 Would you like to perform another search? (y/n): ").strip().lower()
            if another_search in ['y', 'yes']:
                new_query = input("\n🔍 Enter your new search query: ").strip()
                if new_query:
                    print(f"\n🔍 Searching for: '{new_query}'")
                    print("=" * 50)
                    
                    results = searcher.search_and_extract(new_query, max_results, scrape_count)
                    search_results = results['search_results']
                    extracted_contents = results['extracted_contents']
                    
                    display_results(new_query, search_results, extracted_contents, max_content_length=500)
                    
                    if search_results:
                        print(f"\n💾 Saving search results to JSON file...")
                        save_results(new_query, search_results, extracted_contents)
                        
                        successful_extractions = len([content for content in extracted_contents if content.get('status') != 'failed'])
                        print(f"\n📊 Summary:")
                        print(f"   🔍 Search Results: {len(search_results)}")
                        print(f"   ✅ Successful Extractions: {successful_extractions}")
                        print(f"   ❌ Failed Extractions: {len(extracted_contents) - successful_extractions}")
                        print(f"   💾 Data saved to JSON file in 'searches' folder")
                else:
                    print("❌ No query provided.")
            elif another_search in ['n', 'no']:
                print("\n👋 Thank you for using ResearchGenie!")
                break
            else:
                print("Please enter 'y' for yes or 'n' for no.")
    
    except KeyboardInterrupt:
        print("\n\n👋 Search interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n❌ An error occurred: {str(e)}")
        print("Please try again.")
