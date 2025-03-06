from botasaurus_server.server import Server
from src.pdf_scraper import pdf_scraper_wrapper

# Add the scraper to the server
Server.add_scraper(pdf_scraper_wrapper)