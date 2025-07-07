# WebSearch Module - ResearchGenie

The `WebSearch` module provides a unified interface for web searching and content extraction. It combines DuckDuckGo search with advanced web content extraction, making it easy to search for information and extract readable content from web pages.

## Features
- **Web Search**: Search the web using DuckDuckGo.
- **Content Extraction**: Extract main text, metadata, and more from web pages.
- **Batch Extraction**: Extract content from multiple URLs with one call.
- **Combined Search & Extract**: Search and extract from top results in a single step.

## Basic Usage

```python
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'Tools'))
from WebSearch import WebSearcher

searcher = WebSearcher()

# 1. Search
results = searcher.search("Python web scraping", max_results=3)
for r in results:
    print(r['title'], r['url'])

# 2. Extract content from a single URL
content = searcher.extract_content(results[0]['url'])
print(content['title'], content['content'][:200])

# 3. Batch extract
urls = [r['url'] for r in results]
batch = searcher.extract_content_batch(urls)

# 4. Search and extract top N
combo = searcher.search_and_extract("Python tutorials", max_results=3, extract_count=2)
```

## Example: Search and Extract

```python
searcher = WebSearcher()
results = searcher.search_and_extract("Machine Learning", max_results=2, extract_count=1)
for content in results['extracted_contents']:
    if content.get('status') != 'failed':
        print(content['title'])
        print(content['content'][:300])
```

## Example: Batch Extraction

```python
urls = [
    "https://docs.python.org/3/",
    "https://realpython.com/",
    "https://python.org/"
]
searcher = WebSearcher()
contents = searcher.extract_content_batch(urls)
for c in contents:
    print(c['title'])
```

---

**Tip:** See `example_usage.py` for a full interactive example.
