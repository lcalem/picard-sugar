import re
import requests

from pprint import pprint

import lxml.html


CRAWLING_INFO = {
    'picard': {
        "listing_url": "https://www.picard.fr/",
        "listing_selector": "li.pi-Nav-lvl1Item--treeview button",
        "product_selector": "ul#search-result-items a.pi-ProductCard-link",
        "product_name_selector": "h1.pi-ProductPage-title",
        'product_quantity_ref_selector': "table.pi-ProductTabsNutrition-table thead th:nth-child(2)",
        "product_sugar_title_selector": "table.pi-ProductTabsNutrition-table tbody tr:nth-child(3) td:nth-child(1)",
        "product_sugar_quantity_selector": "table.pi-ProductTabsNutrition-table tbody tr:nth-child(3) td:nth-child(2)"

    }
}


class ProductException(Exception):
    pass


class Crawler(object):
    '''
    will crawl a website to get sunscreen products htmls
    '''

    def __init__(self, website):
        if website not in CRAWLING_INFO:
            raise Exception("Unsupported website %s" % website)

        self.config = CRAWLING_INFO[website]

    def crawl(self):
        '''
        get the listing url content and yield the html of each product
        TODO: handle non 200 requests
        '''

        listing_url = self.config["listing_url"]
        listing_html = requests.get(listing_url).text

        htmldoc = lxml.html.fromstring(listing_html)

        categories = htmldoc.cssselect(self.config["listing_selector"])
        for category_elt in categories:
            count = 0
            button_id = category_elt.get('id')
            if not button_id.startswith('navLink'):
                print('Skipping category %s' % button_id)
                continue

            category_name = button_id.split("navLink")[1]
            category_url = "https://www.picard.fr/rayons/%s?start=0&sz=400" % category_name
            print('crawling category %s' % category_name)

            # crawl category
            category_html = requests.get(category_url).text
            categorydoc = lxml.html.fromstring(category_html)

            products = categorydoc.cssselect(self.config["product_selector"])
            for product_elt in products:
                count += 1
                product_url = product_elt.get('href')

                if product_url.startswith('/'):
                    product_url = 'https://www.picard.fr%s' % product_url

                # print("found product url %s" % product_url)
                yield category_name, product_url

            print('found %s products for category %s' % (count, category_name))


class PicardSugarExctractor(object):

    def __init__(self, output_path=None):
        self.output_path = output_path if output_path else "picard_results.csv"
        self.config = CRAWLING_INFO['picard']

    def parse_product(self, product_url):
        '''
        html for one product page
        output should be a dict with 2 fields:
            - product_name: str
            - sugar_value per 100g: float
        '''
        try:
            product_html = requests.get(product_url).text
            htmldoc = lxml.html.fromstring(product_html)

            sugar_quantity = htmldoc.cssselect(self.config["product_sugar_quantity_selector"])[0].text_content().strip().split('g')[1]
            sugar_quantity = float(re.sub(r"\s+", "", sugar_quantity, flags=re.UNICODE).replace(',', '.').replace('<', ''))

            return {
                "product_name": htmldoc.cssselect(self.config["product_name_selector"])[0].text_content().strip(),
                "reference_quantity": htmldoc.cssselect(self.config["product_quantity_ref_selector"])[0].text_content().strip(),
                "sugar_title": htmldoc.cssselect(self.config["product_sugar_title_selector"])[0].text_content().strip(),
                "sugar_quantity": sugar_quantity
            }
        except Exception as e:
            print("issue with product url %s:" % product_url)
            print(str(e))

    def extract_data(self):
        picard_crawler = Crawler('picard')
        products = list()

        for category_name, product_url in picard_crawler.crawl():

            try:
                product_results = self.parse_product(product_url)
                product_results['url'] = product_url
                product_results['category'] = category_name
                products.append(product_results)
            except ProductException as err:
                print(str(err))

        self.create_csv(products)

    def create_csv(self, product_results):
        sorted_products = sorted(product_results, key=lambda x: x["sugar_quantity"])

        with open(self.output_path, "w+") as f_out:
            f_out.write(";".join(["product name", "category name", "product url", "reference quantity", "sugar title", "sugar content"]) + "\n")

            for product in sorted_products:
                csv_parts = list()
                csv_parts.append(product["product_name"])
                csv_parts.append(product["category"])
                csv_parts.append(product["url"])
                csv_parts.append(product["reference_quantity"])
                csv_parts.append(product["sugar_title"])
                csv_parts.append(product["sugar_quantity"])

                f_out.write(";".join(csv_parts) + "\n")

        print("Saved picard data at %s" % self.output_path)


def main():
    '''
    TODO: handle non-200 requests
    '''
    extractor = PicardSugarExctractor()
    extractor.extract_data()


if __name__ == '__main__':
    main()
