# Picard sugar crawler

- Crawls french frozen products shop Picard's website to find products with the least amount of sugar
- Products without nutritional information on the webpage are ignored but logged.
- **Output:** csv file with ordered products by ascending order of sugar content per 100g / ml of product.
- **Usage:** `python3 picard_sugar.py`
- **Requirements:** packages `requests` and `lxml` (`pip3 install requests` and `pip3 install lxml` / `pip3 install cssselect`)
- Crawling can take a while
