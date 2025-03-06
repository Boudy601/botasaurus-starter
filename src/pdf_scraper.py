import time
import json
import psutil
from lxml import html
from botasaurus.browser import browser, Driver
from botasaurus.task import task
from botasaurus.cache import Cache  

# # Load the listing of book language URLs
# """ please chagne the file path with your path before running the code"""
# with open("C:\\scraping projecs\\pdf_scraper\\book_language_urls.json", "r", encoding="utf-8") as f:
#     data = json.load(f)
#     book_language_urls = data["book_language_urls"]

############################################################
# 1. A function that only scrapes and caches the HTML
############################################################
@browser(
    parallel=5,
    max_retry=10,
    block_images_and_css=True,
    tiny_profile=True,
    profile="",
    cache=True,  # Cache the HTML result for each book link
    output=False
)
def scrape_book_html(driver: Driver, book_link: str):
    """
    Given a book detail page URL, this function:
      - Opens the URL in a new tab,
      - Waits for the page to load,
      - Grabs the HTML,
      - Closes the detail tab and
      - Switches back to the main (listing) tab.
    The HTML result is cached.
    """
    # Open the book detail page in a new tab
    driver.open_link_in_new_tab(book_link)
    time.sleep(1)  # Allow time for the page to load
    html_content = driver.page_html
    # Close the current (detail) tab
    driver._tab.close()
    # Switch back to the main tab (the listing page)
    driver.switch_to_tab(driver._browser.tabs[0])
    return html_content

############################################################
# 2. A function that extracts data from the HTML and caches the result
############################################################
def extract_book_details(html_content: str, book_link):
    """
    Given the HTML content of a book detail page, extract:
      - Full Book Name,
      - Author Name, and
      - Edition Language.
    """
    parsed_html = html.fromstring(html_content)
    # Extract the Full Book Name
    book_name = parsed_html.xpath("//li[strong[text()='Full Book Name:']]/text()")
    book_name = book_name[0].strip() if book_name else "Unknown Book Name"

    # Extract the Author Name
    author_name = parsed_html.xpath("//li[strong[text()='Author Name:']]/text()")
    author_name = author_name[0].strip() if author_name else "Unknown Author"

    # Extract the Edition Language
    edition_language = parsed_html.xpath("//li[strong[text()='Edition Language:']]//span/text()")
    edition_language = edition_language[0].strip() if edition_language else "Unknown Language"
    
    
    return {
        'Book_name': book_name,
        'Author_name': author_name,
        'Edition_Language': edition_language,
        'Book_link': book_link  
    }

@task(
        cache=True
)
def scrape_book_data(book_link: str):
    """
    Given a book detail URL, this function first gets the cached HTML
    via `scrape_book_html()` and then extracts and caches the book data.
    """
    html_content = scrape_book_html(book_link)
    return extract_book_details(html_content, book_link)

def update_or_get_cached_book_data(book_link: str):
    """
    Checks if cached data exists for the given book_link.
    If the 'Book_link' attribute is missing, update the cached data.
    Otherwise, simply return the cached data or scrape if not present.
    """
    if Cache.has('scrape_book_data', book_link):
        cached_data = Cache.get('scrape_book_data', book_link)
        if 'Book_link' not in cached_data:
            # Update the cached result with the new attribute
            cached_data['Book_link'] = book_link
            Cache.put('scrape_book_data', book_link, cached_data)
        return cached_data
    else:
        return scrape_book_data(book_link)

############################################################
# 3. The main function that handles pagination and processes listing pages
############################################################
@browser(
    parallel=5,
    block_images_and_css=True,
    tiny_profile=True,
    profile=""
)
def pdf_scraper(driver: Driver, book_language_urls):
    """
    Opens the listing page (given by book_language_url) and iterates over
    paginated results. For each page it:
      - Gets all book detail links,
      - For each link, it calls `update_or_get_cached_book_data()` (instead of direct scraping),
      - Saves the accumulated book data to file, and
      - Clicks the next-page button if available.
    """
    initial = psutil.net_io_counters()  # Bandwidth before scraping

    # Load the listing page
    driver.google_get(book_language_urls, wait=1)
    books = []

    while True:
        # Get all book links on the current listing page
        books_links = driver.get_all_links("h2 > a")
        
        for book_link in books_links:
            # Use the update function to ensure cached data includes the new attribute
            book_data = update_or_get_cached_book_data(book_link)
            books.append(book_data)
        
        
        # Ensure we are back on the main listing tab
        driver.switch_to_tab(driver._browser.tabs[0])
        
        # Check if a "next page" button exists
        next_page_button = driver.select("li.pagination-next > a")
        if next_page_button:
            next_page_button.click()
            time.sleep(2)  # Allow the next page to load
        else:
            break  # No more pages; exit loop

    final = psutil.net_io_counters()  # Bandwidth after scraping

    bytes_sent = final.bytes_sent - initial.bytes_sent
    bytes_received = final.bytes_recv - initial.bytes_recv


    return books

@task
def pdf_scraper_wrapper(book_language_urls_dict):

    #convert the user input into a list
    book_language_urls = list(book_language_urls_dict["links"])

    all_pdfs = []
    results = pdf_scraper(book_language_urls)
    for pdfs in results:
        all_pdfs.extend(pdfs)

    return all_pdfs



if __name__ == "__main__":

    pdf_scraper_wrapper()
