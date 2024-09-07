import time
from bs4 import BeautifulSoup

from utils.tender.parse.base_lav import BaseNotice


class Notice44(BaseNotice):           
    def _parse_data(self, soup: BeautifulSoup):     
        names = soup.findAll('span', class_="cardMainInfo__content")
        
        tender_name = names[0].text.strip()
        customer_name = names[1].text.strip()
        
        tender_id = soup.find("span", class_="cardMainInfo__purchaseLink").text.replace("№", "").strip()

        complaints_url = f"https://zakupki.gov.ru/epz/complaint/search/search_eis.html?searchString={tender_id}&fz94=on&cancelled=on&considered=on&regarded=on"
        
        time.sleep(1)
        complaints = self._get_complaints(complaints_url)
        
        items = soup.find_all("div", class_="col")
        for item in items:
            rows = item.find_all("section", class_="blockInfo__section")
            for row in rows:
                title = row.find("span", class_="section__title")
                if title is None:
                    continue
                if "Дата и время окончания срока подачи заявок" in title.text:
                    title_value = row.find("span", class_="section__info").text.strip().split()[:2]
                    return {
                        'name': tender_name,
                        'customer_name': customer_name,
                        'deadline_date': title_value[0],
                        'deadline_time': title_value[1],
                        'complaints': complaints
                    }
    

