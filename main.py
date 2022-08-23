import os
import re
from collections import defaultdict
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler


import pandas
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader, select_autoescape


WINERY_FOUNDATION_YEAR = 1920
WINE_CATEGORY_WITHOUT_TYPE = 'Напитки'


def get_winery_age(foundation_year):
    winery_years = datetime.now().year - foundation_year
    if re.match(r'\d*(1\d)$', str(winery_years)):
        return f'{winery_years} лет'
    elif re.match(r'\d*(1)$', str(winery_years)):
        return f'{winery_years} год'
    elif re.match(r'\d*([2-4])$', str(winery_years)):
        return f'{winery_years} года'
    return f'{winery_years} лет'


if __name__ == '__main__':

    load_dotenv()
    wines_data = os.getenv('WINES_DATA', default='wines_test_data.xlsx')

    all_wines = pandas.read_excel(
        wines_data,
        sheet_name="Лист1",
        keep_default_na=False
    )

    wine_categories = sorted(
        set(all_wines['Категория'].to_list())
    )

    categorized_wines = defaultdict(list)

    for category in wine_categories:
        wines = all_wines[
            all_wines['Категория'] == category
            ].to_dict(orient='records')
        categorized_wines[category] = wines

    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('template.html')

    rendered_page = template.render(
        winery_years=get_winery_age(WINERY_FOUNDATION_YEAR),
        categorized_wines=categorized_wines,
        no_type=WINE_CATEGORY_WITHOUT_TYPE,
    )

    with open('index.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)

    server = HTTPServer(('0.0.0.0', 8000), SimpleHTTPRequestHandler)
    server.serve_forever()
