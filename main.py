import re
from collections import defaultdict
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler


import pandas
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


deserialized_wines = pandas.read_excel(
    'wine1.xlsx',
    sheet_name='Лист1',
    usecols=['Название', 'Сорт', 'Цена', 'Картинка']
).to_dict(orient='records')

deserialized_categorized_wines = pandas.read_excel(
    'wine3.xlsx',
    sheet_name="Лист1",
    keep_default_na=False
)

wine_categories = sorted(
    set(deserialized_categorized_wines['Категория'].to_list())
)

categorized_wines = defaultdict(list)

for category in wine_categories:
    wines = deserialized_categorized_wines[
        deserialized_categorized_wines['Категория'] == category
        ].to_dict(orient='records')
    categorized_wines[category] = wines


env = Environment(
    loader=FileSystemLoader('.'),
    autoescape=select_autoescape(['html', 'xml'])
)

template = env.get_template('template.html')

rendered_page = template.render(
    winery_years=get_winery_age(WINERY_FOUNDATION_YEAR),
    deserialized_wines=deserialized_wines,
    categorized_wines=categorized_wines,
    no_type=WINE_CATEGORY_WITHOUT_TYPE,
)

with open('index.html', 'w', encoding="utf8") as file:
    file.write(rendered_page)

server = HTTPServer(('0.0.0.0', 8000), SimpleHTTPRequestHandler)
server.serve_forever()
