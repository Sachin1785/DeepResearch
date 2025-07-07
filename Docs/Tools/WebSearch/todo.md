## ✅ Extracting Links and Images with `trafilatura`

Yes — ✅ you can extract links and images with `trafilatura` by enabling its **advanced output format**.

---

### 🔍 How to Extract Links and Images with `trafilatura`

#### ✅ Step 1: Use `extract(..., output_format='xml')`

This gives you a **structured XML/HTML-like** output that includes:

- `<a href="...">` links
- `<img src="...">` images
- `<p>`, `<h1>`, etc., structured tags

---

### 🔏 Example

```python
import trafilatura

url = "https://example.com"
downloaded = trafilatura.fetch_url(url)

if downloaded:
    xml_result = trafilatura.extract(
        downloaded,
        output_format='xml',
        include_links=True,
        include_images=True
    )
    print(xml_result)
```

---

### 📟 Sample Output

```xml
<article>
  <p>This is a paragraph with a <a href="https://some.link">link</a>.</p>
  <img src="https://example.com/image.jpg" />
</article>
```

---

### 🧰 Extracting Just the Links or Images from That Output

You can then parse the XML using `BeautifulSoup`:

```python
from bs4 import BeautifulSoup

soup = BeautifulSoup(xml_result, "lxml")

# Extract all image URLs
images = [img['src'] for img in soup.find_all('img')]

# Extract all anchor links
links = [a['href'] for a in soup.find_all('a')]
```

---

### 🧪 Optional: Extracting Metadata

You can also get:

- Canonical URL
- Publication date
- Author name
- Tags

Using:

```python
from trafilatura.metadata import extract_metadata

metadata = extract_metadata(downloaded)
print(metadata)
```

