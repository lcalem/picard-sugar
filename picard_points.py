import argparse

import re
import requests
from bs4 import BeautifulSoup


def get_price_from_url(url):
    response = requests.get(url)

    if response.status_code == 200:
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')

        title = soup.title.string if soup.title else 'unknown'
       
        price_div = soup.find('div', class_='pi-ProductDetails-salesPrice')
        if price_div:
            text = price_div.get_text(strip=True)

            match = re.search(r'[\d,.]+', text)
            if match:
                price = float(match.group().replace(',', '.'))

        else:
            print(f"no page!, status code: {response.status_code}")

    return title, price


def process_urls(urls, points):
    for url in urls:
        product_name, price = get_price_from_url(url)
        if price is not None:
            # f"{'Points':<10} {'Price':>10} {'€ per point':>10} {'URL':<60}"
            print(f"{points:<10} {price:<10.2f} {price/points:<15.3f} {product_name:<60.57}")
            # print(f"→ {product_name}: {price / points:.3f} € per point ({points} points)")
        else:
            print(f"{points:<10} {'N/A':<10.2f} {'N/A':<15.3f} {'unknown':<60.57}")


# python picard.py --urls100 --urls300 --urls700
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--urls100', nargs='*')
    parser.add_argument('--urls300', nargs='*')
    parser.add_argument('--urls700', nargs='*')
    args = parser.parse_args()

    header = f"{'Points':<10} {'Price':<10} {'€ per point':<15} {'Product':<60}"
    print(header)
    print('-' * len(header))

    if args.urls100:
        process_urls(args.urls100, 100)

    if args.urls300:
        process_urls(args.urls300, 300)

    if args.urls700:
        process_urls(args.urls700, 700)

