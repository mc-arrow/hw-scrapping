import json
import bs4
import requests
from fake_headers import Headers

keywords = ['django', 'flask', 'MongoDB']

def get_fake_headers():
    return Headers(browser="chrome", os="win", headers=True).generate()

response = requests.get('https://spb.hh.ru/search/vacancy?text=python&area=1&area=2', headers=get_fake_headers())

page_data = bs4.BeautifulSoup(response.text, features='lxml')
vacancies = page_data.find_all(class_='serp-item_link')

parsed_data = []
for vacancy in vacancies:
    h2_tag = vacancy.find('h2', class_='bloko-header-section-2')
    a_tag = h2_tag.find('a')
    title = a_tag.find('span').text.strip()
    link = a_tag['href']
    company = vacancy.find('a', class_='bloko-link bloko-link_kind-secondary').text.strip()
    city = vacancy.find('span', {'data-qa':'vacancy-serp__vacancy-address'}).text.strip()
    salary = vacancy.find('span', class_='compensation-text--kTJ0_rp54B2vNeZ3CTt2')
    if salary:
        salary = salary.text.strip()
    else:
        salary = 'Не указана'

    article_response = requests.get(link, headers=get_fake_headers())
    vacancy_data = bs4.BeautifulSoup(article_response.text, features='lxml')
    vacancy_description = vacancy_data.find('div', class_='g-user-content').text
    
    if any(keyword in vacancy_description for keyword in keywords):
        parsed_data.append({
            'link': link,
            'title': title,
            'company': company,
            'city': city,
            'salary': salary,
        })

with open('vacancies.json', 'w', encoding='utf-8') as f:
    f.write(json.dumps(parsed_data, ensure_ascii=False, indent=4))

print('Парсинг завершен. Результаты сохранены в файле vacancies.json.')