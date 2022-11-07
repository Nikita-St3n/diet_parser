#!/usr/bin/env python
# -*- coding: utf-8 -*- # строка нужна, чтобы не было ошибки Non-UTF-8 code starting with '\xd1' in file ...

import random
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import json
import csv
import time

ua = UserAgent()
headers = {'User-Agent': ua.random}

# сохраняем ссылку на страницу со ссылками на Категории

# url = 'https://health-diet.ru/table_calorie/'
#
# req = requests.get(url, headers=headers)
# src = req.text
# # print(src)
#
# with open("index.html", encoding="utf-8") as file:
#     src = file.read()
#
# soup = BeautifulSoup(src, 'lxml')
# all_products_hrefs = soup.find_all(class_="mzr-tc-group-item-href")
#
# all_categories_dict = {}
# for item in all_products_hrefs:
#     item_text = item.text
#     item_href = "https://health-diet.ru" + item.get("href")
#     print(f"{item_text}: {item_href}")
#     all_categories_dict[item_text] = item_href

# сохраняем ссылки на все Категории в JSON - файл, для его дальнейшего чтения

# with open("all_categories_dict.json", "w", encoding="utf-8") as file:
#     json.dump(all_categories_dict, file, indent=4, ensure_ascii=False)

with open("all_categories_dict.json", encoding="utf-8") as file:
    all_categories = json.load(file)

iteration_count = int(len(all_categories)) - 1
count = 0
print(f'Всего итераций: {iteration_count}')

for category_name, category_href in all_categories.items():
    rep = [",", " ", "-", "'", "__"]
    for item in rep:
        if item in category_name:
            category_name = category_name.replace(item, '_')

    req = requests.get(url=category_href, headers=headers)
    src = req.text

    with open(f"data/{count}_{category_name}.html", "w", encoding="utf-8") as file:
        file.write(src)

    with open(f"data/{count}_{category_name}.html", encoding="utf-8") as file:
        src = file.read()
    soup = BeautifulSoup(src, "lxml")

    # проверяем страницу на наличие таблицы

    alert_block = soup.find(class_="uk-alert-danger")
    if alert_block is not None:
        continue

    # собираем заголовки с таблицы и записываем их в CSV - файл

    table_head = soup.find(class_="mzr-tc-group-table").find("tr").find_all("th")

    product = table_head[0].text
    calories = table_head[1].text
    proteins = table_head[2].text
    fats = table_head[3].text
    carbohydrates = table_head[4].text

    with open(f"data/{count}_{category_name}.csv", "w", encoding="utf-8") as file:
        writer = csv.writer(file, delimiter="|")
        writer.writerow(
            (
                product,
                calories,
                proteins,
                fats,
                carbohydrates
            )
        )

    # собираем данные о продукте

    products_data = soup.find(class_="mzr-tc-group-table").find("tbody").find_all("tr")

    product_info = []
    for item in products_data:
        product_tds = item.find_all("td")

        title = product_tds[0].find('a').text
        calories = product_tds[1].text
        proteins = product_tds[2].text
        fats = product_tds[3].text
        carbohydrates = product_tds[4].text

        # JSON - файл с продуктами - словарями
        product_info.append({
            'Title': title,
            'Calories': calories,
            'Proteins': proteins,
            'Fats': fats,
            'Carbohydrates': carbohydrates
        })

        with open(f"data/{count}_{category_name}.json", "a", encoding="utf-8") as file:
            json.dump(product_info, file, indent=4, ensure_ascii=False)

        # Записываем данные в ранее созданный CSV - файл на каждую категорию
        with open(f"data/{count}_{category_name}.csv", "a", encoding="utf-8") as file:
            writer = csv.writer(file, delimiter="|")
            writer.writerow(
                (
                    title,
                    calories,
                    proteins,
                    fats,
                    carbohydrates
                )
            )

    count += 1  # номер категории
    iteration_count -= 1  # оставшиеся страницы
    print(f'[+] Итерация №{count}. {category_name} записано... Осталось итераций: {iteration_count}')

    if iteration_count == 0:
        print('Парсинг завершён успешно!')
        break

    time.sleep(random.randrange(1, 2))  # рандомная задержка перед выводом
