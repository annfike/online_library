import requests
import pathlib
from pathlib import Path
from pathvalidate import sanitize_filename
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os
from urllib.parse import unquote, urlsplit


def check_for_redirect(response):
    if response.history:
        raise requests.exceptions.HTTPError


def download_txt(url, filename, path, params=None):
    filename = sanitize_filename(filename)
    filepath = Path(path) / filename
    response = requests.get(url, params=params)
    response.raise_for_status()
    with filepath.open('wb') as file:
        file.write(response.content)


def download_image(url, path, params=None):
    pathlib.Path(path).mkdir(exist_ok=True)
    unquoted = unquote(url)
    parsed = urlsplit(unquoted)
    splited_path = os.path.split(parsed.path) 
    filename = splited_path[-1] 
    filepath = Path(path) / filename
    response = requests.get(url, params=params)
    response.raise_for_status()
    with filepath.open('wb') as file:
       file.write(response.content)

    
def parse_book_page(index):
    url = f'https://tululu.org/b{index}/'
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)
    soup = BeautifulSoup(response.text, 'lxml')
    title_tag = soup.find('body').find('h1')
    title_text = title_tag.text.split('::')
    title = title_text[0].strip()
    author = title_text[1].strip()
    pic = soup.find('div', class_='bookimage').find('img')['src']
    pic_link = urljoin('https://tululu.org', pic)
    for genre_tag in soup.find_all('span', class_='d_book'):
        genres = []
        for genre in genre_tag.find_all('a'):
            genres.append(genre.text)
    comments = []
    for comment in soup.find_all('div', class_='texts'):
        comments.append(comment.find('span').text)
    book = dict()
    book["Заголовок"] = title
    book["Автор"] = author
    book["Картинка"] = pic_link
    book["Жанр"] = genres
    book["Комментарии"] = comments
    return book


path = 'books'
pathlib.Path(path).mkdir(exist_ok=True)
for index in range(1,11):
    payload = {"id": index}
    #filename = get_book_title(index)
    #filename = f'{index}.{filename}.txt'
    #filepath = Path(path) / filename
    try:
        print(parse_book_page(index))
        #download_image(url, 'images')
        #download_txt("https://tululu.org/txt.php", filename, path, params=payload)
    except requests.HTTPError:
        pass



