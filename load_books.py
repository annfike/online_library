import argparse
import os
import pathlib
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def check_for_redirect(response):
    if response.history:
        raise requests.exceptions.HTTPError


def download_txt(url, filename, books_path, params=None):
    filename = sanitize_filename(filename)
    filepath = Path(books_path) / filename
    response = requests.get(url, params=params)
    response.raise_for_status()
    with filepath.open('w', encoding="utf-8") as file:
        file.write(response.text)


def download_image(url, book_id, images_path, params=None):
    unquoted = unquote(url)
    parsed = urlsplit(unquoted)
    splited_path = os.path.split(parsed.path)
    filename = f'{book_id}_{splited_path[-1]}'
    filepath = Path(images_path) / filename
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
    title, author = title_tag.text.split('::')
    title, author = title.strip(), author.strip()
    pic = soup.find('div', class_='bookimage').find('img')['src']
    pic_link = urljoin('https://tululu.org', pic)
    genre_tag = soup.find('span', class_='d_book')
    genres = [genre.text for genre in genre_tag.find_all('a')]
    comments = [comment.find('span').text for comment in soup.find_all('div', class_='texts')]
    book = {
        'Заголовок': title,
        'Автор': author,
        'Картинка': pic_link,
        'Жанр': genres,
        'Комментарии': comments,
    }
    return book


def main():
    books_path = 'books'
    images_path = 'images'
    pathlib.Path(books_path).mkdir(exist_ok=True)
    pathlib.Path(images_path).mkdir(exist_ok=True)
    parser = argparse.ArgumentParser(description='Get book')
    parser.add_argument('start_id', default=1, type=int, help='Укажите начальную страницу')
    parser.add_argument('end_id', default=10, type=int, help='Укажите конечную страницу')
    args = parser.parse_args()
    for book_id in range(args.start_id, args.end_id+1):
        payload = {'id': book_id}
        try:
            book_page = parse_book_page(book_id)
            book_title = book_page['Заголовок']
            filename = f'{book_id}.{book_title}.txt'
            url = book_page['Картинка']
            download_image(url, book_id, images_path)
            download_txt('https://tululu.org/txt.php', filename, books_path, params=payload)
        except requests.HTTPError:
            pass


if __name__ == '__main__':
    main()
