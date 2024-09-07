import requests, asyncio

from bs4 import BeautifulSoup

from abc import ABC, abstractmethod


class BaseNotice(ABC):
    def __init__(self, url) -> None:
        self.url = url
        self.errors = 0
    
    @abstractmethod
    def _parse_data(self, soup: BeautifulSoup):
        pass

    def _get_response(self, url):
        headers = {
            "Accept": "text/html",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_3_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Safari/605.1.15"
        }
        
        response = requests.get(url=url, headers=headers)
        return response
    
    def _get_complaints(self, url):
        base_url = "https://zakupki.gov.ru"
        
        response = self._get_response(url)
        
        soup = BeautifulSoup(response.text, "lxml")
        
        complaints = soup.find_all("span", class_="registry-entry__header-mid__number")
        
        arr = ";".join([f"{base_url}{complaint.find('a')['href']}" for complaint in complaints])
        
        return arr    
    
    
    async def parse(self):
        response = self._get_response(self.url)

        if response.status_code != 200:
            self.errors += 1
            await asyncio.sleep(2)
            if self.errors == 2:
                raise ValueError("Ссылка указана неверно, или сайт не отвечает.") 

            return await self.parse()
        
        soup = BeautifulSoup(response.text, "lxml")
        parser_data = self._parse_data(soup)
        if parser_data:
            return parser_data
        else:
            raise ValueError("Не смог найти данные у тендера") 