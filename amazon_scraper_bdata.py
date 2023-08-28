import asyncio
from playwright.async_api import async_playwright
import pandas as pd

username='YOUR_BRIGHTDATA_USERNAME'
password='YOUR_BRIGHTDATA_PASSWORD'
auth=f'{username}:{password}'
host = 'YOUR_BRIGHTDATA_DEFAULT_HOST'
browser_url = f'wss://{auth}@{host}'

async def scrape_amazon_bdata():
    async with async_playwright() as pw:
        print('connecting')
        # Launch new browser
        browser = await pw.chromium.connect_over_cdp(browser_url)
        print('connected')
        page = await browser.new_page()
        print('navigating')
        # Go to Amazon URL
        await page.goto('https://www.amazon.com/s?i=fashion&bbn=115958409011', timeout=600000)
        print('data extraction in progress')
        # Extract information
        results = []
        listings = await page.query_selector_all('div.a-section.a-spacing-small')
        for listing in listings:
            result = {}
            # Product name
            name_element = await listing.query_selector('h2.a-size-mini > a > span')
            result['product_name'] = await name_element.inner_text() if name_element else 'N/A'
            
            # Rating
            rating_element = await listing.query_selector('span[aria-label*="out of 5 stars"] > span.a-size-base')
            result['rating'] = await rating_element.inner_text() if rating_element else 'N/A'
            
            # Number of reviews
            reviews_element = await listing.query_selector('span[aria-label*="stars"] + span > a > span')
            result['number_of_reviews'] = await reviews_element.inner_text() if reviews_element else 'N/A'
            
            # Price
            price_element = await listing.query_selector('span.a-price > span.a-offscreen')
            result['price'] = await price_element.inner_text() if price_element else 'N/A'

            if(result['product_name']=='N/A' and result['rating']=='N/A' and result['number_of_reviews']=='N/A' and result['price']=='N/A'):
                pass
            else:
                results.append(result)
        # Close browser
        await browser.close()
        
        return results

# Run the scraper and save results to a CSV file
results = asyncio.run(scrape_amazon_bdata())
df = pd.DataFrame(results)
df.to_csv('amazon_products_bdata_listings.csv', index=False)
