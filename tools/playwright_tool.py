import logging
import re
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def scrape_page_structure(url: str) -> dict:
    """Scrapes a URL using playwright or falls back to urllib/BeautifulSoup if playwright fails or is not installed.
    Extracts high-level page info, visual elements, form fields, and buttons.
    """
    logging.info(f"Initiating DOM structure analysis for URL: {url}")
    result = {
        "title": "Unknown Title",
        "url": url,
        "forms": [],
        "inputs": [],
        "buttons": [],
        "links": [],
        "raw_text_summary": "",
        "success": False,
        "error": None
    }
    
    # Try using Playwright for rich, single-page application dynamic DOM scraping
    try:
        from playwright.sync_api import sync_playwright
        
        logging.info("Attempting Playwright DOM scraping...")
        with sync_playwright() as p:
            # Launch headless browser
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # Wait for content to render (up to 10 seconds)
            response = page.goto(url, wait_until="networkidle", timeout=10000)
            
            result["title"] = page.title()
            html = page.content()
            
            # Extract inputs and forms using Playwright queries
            inputs = page.query_selector_all("input, select, textarea")
            for inp in inputs:
                inp_type = inp.get_attribute("type") or "text"
                inp_name = inp.get_attribute("name") or inp.get_attribute("id") or ""
                inp_placeholder = inp.get_attribute("placeholder") or ""
                result["inputs"].append({
                    "tag": inp.evaluate("el => el.tagName.toLowerCase()"),
                    "type": inp_type,
                    "name": inp_name,
                    "placeholder": inp_placeholder
                })
                
            buttons = page.query_selector_all("button, input[type='submit']")
            for btn in buttons:
                btn_text = btn.text_content() or btn.get_attribute("value") or "Submit"
                btn_type = btn.get_attribute("type") or "button"
                result["buttons"].append({
                    "text": btn_text.strip(),
                    "type": btn_type
                })
                
            # Extract forms
            forms = page.query_selector_all("form")
            for form in forms:
                form_action = form.get_attribute("action") or ""
                form_method = form.get_attribute("method") or "get"
                result["forms"].append({
                    "action": form_action,
                    "method": form_method
                })
                
            # Extract links
            links = page.query_selector_all("a")
            for link in links:
                href = link.get_attribute("href") or ""
                text = link.text_content() or ""
                if href and not href.startswith("#") and not href.startswith("javascript:"):
                    result["links"].append({
                        "href": href,
                        "text": text.strip()
                    })

            # Get a simple raw text summary of the page for contextual understanding
            body_text = page.locator("body").text_content()
            # Clean up white space
            body_text = re.sub(r'\s+', ' ', body_text).strip()
            result["raw_text_summary"] = body_text[:1200]  # Limit context window size
            
            browser.close()
            result["success"] = True
            logging.info(f"Playwright successfully scraped '{result['title']}' with {len(result['inputs'])} inputs.")
            return result
            
    except Exception as pw_err:
        logging.warning(f"Playwright scraping failed or not installed: {str(pw_err)}. Falling back to urllib + BeautifulSoup...")
        result["error"] = f"Playwright failed: {str(pw_err)}"

    # Fallback: Simple BeautifulSoup scraper using urllib
    try:
        import urllib.request
        from urllib.parse import urljoin
        
        # Configure headers to look like a standard web browser
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )
        
        with urllib.request.urlopen(req, timeout=5000) as response:
            html = response.read()
            
        soup = BeautifulSoup(html, 'html.parser')
        
        result["title"] = soup.title.string.strip() if soup.title else "Untitled Page"
        
        # Forms
        for form in soup.find_all('form'):
            result["forms"].append({
                "action": form.get('action', ''),
                "method": form.get('method', 'get').lower()
            })
            
        # Inputs
        for inp in soup.find_all(['input', 'select', 'textarea']):
            inp_type = inp.get('type', 'text') if inp.name == 'input' else inp.name
            inp_name = inp.get('name', '') or inp.get('id', '')
            inp_placeholder = inp.get('placeholder', '')
            result["inputs"].append({
                "tag": inp.name,
                "type": inp_type,
                "name": inp_name,
                "placeholder": inp_placeholder
            })
            
        # Buttons
        for btn in soup.find_all(['button', 'input']):
            if btn.name == 'input' and btn.get('type') not in ['submit', 'button']:
                continue
            btn_text = btn.text.strip() if btn.name == 'button' else btn.get('value', 'Submit')
            btn_type = btn.get('type', 'submit')
            result["buttons"].append({
                "text": btn_text,
                "type": btn_type
            })
            
        # Links
        for link in soup.find_all('a'):
            href = link.get('href', '')
            text = link.text.strip()
            if href and not href.startswith('#') and not href.startswith('javascript:'):
                result["links"].append({
                    "href": urljoin(url, href),
                    "text": text
                })
                
        # Raw text
        body = soup.find('body')
        if body:
            body_text = re.sub(r'\s+', ' ', body.get_text()).strip()
            result["raw_text_summary"] = body_text[:1200]
            
        result["success"] = True
        logging.info(f"BS4 Scraper completed successfully. Found {len(result['inputs'])} inputs.")
        
    except Exception as bs_err:
        logging.error(f"Fallback scraper also failed: {str(bs_err)}")
        result["error"] = f"Playwright and BeautifulSoup failed. Errors: [PW: {result['error']}], [BS4: {str(bs_err)}]"
        result["success"] = False
        
    return result

if __name__ == "__main__":
    # Self-test code
    print(scrape_page_structure("https://example.com"))
