import requests
import pathlib
from pathlib import Path
from pathvalidate import sanitize_filename
from bs4 import BeautifulSoup


def check_for_redirect(response):
    if response.history:
        raise requests.exceptions.HTTPError


def download_txt(url, filename, path, params=None):
    filename = sanitize_filename(filename)
    filepath = Path(path) / filename
    response = requests.get(url, params=params)
    response.raise_for_status()
    check_for_redirect(response)
    with filepath.open('wb') as file:
        file.write(response.content)


def get_book_title():
    url = f'https://tululu.org/b{index}/'
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    title_tag = soup.find('body').find('h1')
    title_text = title_tag.text.split('::')
    title_text = title_text[0].strip()
    return title_text


path = 'books'
pathlib.Path(path).mkdir(exist_ok=True)
for index in range(1,11):
    payload = {"id": index}
    filename = get_book_title()
    filename = f'{index}.{filename}.txt'
    filepath = Path(path) / filename
    try:
        download_txt("https://tululu.org/txt.php", filename, path, params=payload)
    except requests.HTTPError:
        pass



