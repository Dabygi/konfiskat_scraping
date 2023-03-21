import requests
from bs4 import BeautifulSoup
import json
import csv
from tqdm import tqdm
import multiprocessing

# making headlines csv
with open('konfiskat.csv', 'w', encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(
        (
        'ID',
        'Title',
        'Code',
        'Address',
        'Price'
        )
    )

def process_page(page_number):
    url = f'http://konfiskat.by/konfiskat/?limit=100&PAGEN_1={page_number}'
    req = requests.get(url)
    result = req.content

    soup = BeautifulSoup(result, "lxml")
    products = soup.find("div", class_="bx_catalog_list bx_blue").find_all("div", class_="bx_catalog_item_container")

    product_info = []
    for product in products:
        id_code = int(product.get("id")[14:])
        titles = product.find("div", class_="col-2 konfiscat-text").find("a").text.strip()

        code_number = product.find("div", class_="col-2 konfiscat-text").find("b", string="	Код").next_element.\
            next_element.text.replace(':', '').replace(' ', '').strip()

        try:
            address = product.find("div", class_="col-2 konfiscat-text").find("b", string="	Место реализации").\
            next_element.next_element.text.replace(':', '').replace(' ', '').strip()
        except AttributeError:
            address = 'None'

        prices = product.find("div", class_="bx_catalog_item_price").find("div", style="   font-size:15px;display:none")\
            .text.strip()
        prices2 = prices.replace('бел.руб.', '').replace('(', '').replace(')', '').replace(' ', '').strip()
        prices3 = int(prices2)/10000

        product_info.append(
            {
                'ID': id_code,
                "Title": titles,
                "Code": code_number,
                "Address": address,
                "Price": prices3
            }
        )

        # writing data to csv

        with open('konfiskat.csv', "a", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(
                (
                    id_code,
                    titles,
                    code_number,
                    address,
                    prices3
                )
            )

    return product_info

if __name__ == '__main__':
    # main loop
    page_numbers = list(range(1, 209))
    with multiprocessing.Pool() as pool:
        results = list(tqdm(pool.imap(process_page, page_numbers), total=len(page_numbers)))

    # writing data to json
    with open('konfiskat.json', "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
