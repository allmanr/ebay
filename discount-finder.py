import requests
import json
import time
import schedule
from datetime import datetime, timedelta

# Configuration
EBAY_API_ENDPOINT = "https://api.ebay.com/buy/browse/v1/item_summary/search"
APP_ID = 'YOUR_APP_ID'  # Replace with your eBay App ID
SELLER_ID = 'SELLER_ID'  # Replace with the eBay seller ID
DISCOUNT_THRESHOLD = 0.15  # 15% discount threshold


class DiscountFinder():
    def __init__(self, app_id, seller_id, discount_threshold):
        self.app_id = app_id
        self.seller_id = seller_id
        self.discount_threshold = discount_threshold

    def get_books(self):
        params = {
            'category_ids': '267',  # eBay Books category ID
            'filter': f'condition:VeryGood,seller:{self.seller_id}',
            'limit': 100  # Adjust as needed
        }
        headers = {
            'Authorization': f'Bearer {self.app_id}',
        }

        response = requests.get(EBAY_API_ENDPOINT, headers=headers, params=params)
        if response.status_code != 200:
            print("Error fetching data from eBay:", response.text)
            return []
        
        return response.json().get('itemSummaries', [])

    def check_discounts(self):
        books = self.get_books()
        for book in books:
            if 'price' in book and 'salesTax' in book['price']:
                current_price = float(book['price']['value'])

                if current_price > 15.0:
                    print(f"Hella expensive alert for {book['title']}")

                trending_price = self.get_trending_price(book['title'])  # Implement your trend price logic here
                
                if trending_price and current_price < trending_price * (1 - DISCOUNT_THRESHOLD):
                    print(f"Discount alert for {book['title']}! Current Price: {current_price}, "
                        f"Trending Price: {trending_price}, Discount: {(1 - (current_price / trending_price)) * 100:.2f}%")

    def get_trending_price(self, book_title, condition='VeryGood'):
        end_date = datetime.now()
        start_date = end_date - timedelta(days=60)
        
        params = {
            'q': book_title,
            'filter': f'condition:{condition}',
            'limit': 100,
            'matchAll': 'true'
        }
        
        headers = {
            'Authorization': f'Bearer {self.app_id}',
        }
        
        response = requests.get(EBAY_API_ENDPOINT, headers=headers, params=params)
        
        if response.status_code != 200:
            print("Error fetching data from eBay:", response.text)
            return None
        
        items = response.json().get('itemSummaries', [])
        
        prices = []
        
        for item in items:
            item_condition = item.get('condition', 'N/A')
            
            # Replace with appropriate logic to gather sold listings
            price_value = float(item['price']['value'])
            
            # Here we would filter based on the release/sale date, but for simplicity, we do not have that in the API response
            # So we'll assume all entries are within the latest 60 days - in practice, you would check actual sale dates
            
            if item_condition == condition:
                prices.append(price_value)

        # Calculate the average price for the collected prices
        if prices:
            average_price = sum(prices) / len(prices)
            return average_price
        else:
            return None


def run_monitor():
    print("Checking for discounted books...")
    check_discounts()

# Schedule to check every hour
schedule.every(1).hour.do(run_monitor)

if __name__ == "__main__":
    testfinder = DiscountFinder(APP_ID, SELLER_ID, DISCOUNT_THRESHOLD)
    testfinder.check_discounts()
    
    while True:
        exit(1)
        schedule.run_pending()
        time.sleep(1)