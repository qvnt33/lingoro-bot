import asyncio

from bs4 import BeautifulSoup

from utils.tender.parse.base_lav import BaseNotice


class Notice223(BaseNotice):           
    def _parse_data(self, soup: BeautifulSoup):
        names = soup.findAll('div', class_="registry-entry__body-value")
        
        tender_name = names[0].text.strip()
        customer_name = names[1].text.strip()
        
        items = soup.find_all("div", class_="card-common-content")
        for item in items:
            rows = item.find('div', class_="row").find_all("div")
            for row in rows:
                title = row.find("div", class_="common-text__title")
                if title is None:
                    continue
                if "Дата и время окончания срока подачи заявок" in title.text:
                    title_value = row.find("div", class_="common-text__value").text.strip().split()[:2]
                    return {
                        'name': tender_name, 
                        'customer_name': customer_name, 
                        'deadline_date': title_value[0], 
                        'deadline_time': title_value[1]
                    }
                
