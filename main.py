from threading import Thread

import requests
from bs4 import BeautifulSoup
import smtplib
import time

from settings import settings


class DeadList:
    __slots__ = ['url', 'prev_content']

    def __init__(self):
        self.url = settings.url
        self.prev_content = ''

    @staticmethod
    def __sending(name, email_text, link):
        # Отправитель
        sender = settings.sender
        # Получатель
        recipient = settings.recipient
        # Инициализация smtp-сервера через контексный менеджер
        with smtplib.SMTP(host=settings.smtp_url, port=settings.smtp_port) as smtp_server:
            # SMTP-соединение в режим TLS для шифровки команд
            smtp_server.starttls()
            smtp_server.login(settings.login, settings.password)

            # К сожалению, кириллицу sendmail не поддерживает, поэтому энкод в utf-8
            message = f"New name in death note: {name}\n\n" \
                      f"{email_text}\n\n" \
                      f"Link to dead wiki: {link}".encode('utf-8')

            smtp_server.sendmail(sender, recipient, message)

    def loop(self):
        while True:
            response = requests.get(self.url)
            soup = BeautifulSoup(response.text, 'html.parser')

            content = soup.find(id='mw-content-text').get_text()[:500]

            if content != self.prev_content:
                headings = soup.find_all('h3')
                for heading in headings:
                    ul = heading.find_next_sibling('ul')
                    if ul:
                        a = ul.find('a')
                        if a:
                            name = a.text
                            link_person = 'https://en.wikipedia.org' + a['href']
                            response_person = requests.get(link_person)
                            soup_person = BeautifulSoup(response_person.text, 'html.parser')
                            languages = {el.get('lang'): el.get('href') for el in
                                         soup_person.select('li.interlanguage-link > a')}
                            if 'ru' in languages:
                                link_person = languages.get('ru')
                                response_person = requests.get(link_person)
                                soup_person = BeautifulSoup(response_person.text, 'html.parser')
                            person_content = soup_person.find(id='mw-content-text')
                            ps = person_content.find_all('p')
                            for p in ps:
                                if p.get_text() != '\n':
                                    text = p.get_text(strip=True)
                                    self.__sending(name=name,
                                                   email_text=text,
                                                   link=link_person)
                                    self.prev_content = content
                                    break
                            break

            time.sleep(3600)  # ежечасная проверка


if __name__ == '__main__':
    Thread(target=DeadList().loop, daemon=True).start()
