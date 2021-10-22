import argparse
import os
import pathlib
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit
import json
import re

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def parse_category(start_page, end_page):
    for page in range(start_page, end_page):
        url = f'https://tululu.org/l55/{page}'
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')
        book_tags = soup.select('.bookimage a')
        books = [book['href'] for book in book_tags]
    return books

        
def get_category_last_page():
    url = 'https://tululu.org/l55/1'
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    last_page_tags = soup.select('.npage')[-1]
    last_page = last_page_tags.text
    return last_page


def check_for_redirect(response):
    if response.history:
        raise requests.exceptions.HTTPError


def download_txt(url, filename, books_path, params=None):
    filename = sanitize_filename(filename)
    filepath = Path(books_path) / filename
    response = requests.get(url, params=params)
    response.raise_for_status()
    with filepath.open('w', encoding='utf-8') as file:
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
    title_tag = soup.select_one('body h1')
    title, author = title_tag.text.split('::')
    title, author = title.strip(), author.strip()
    pic = soup.select_one('.bookimage img')['src']
    pic_link = urljoin('https://tululu.org', pic)
    genres_tag = soup.select('span.d_book a')
    genres = [genre.text for genre in genres_tag]
    comments_tag = soup.select('.texts span')
    comments = [comment.text for comment in comments_tag]
    book = {
        'Заголовок': title,
        'Автор': author,
        'Картинка': pic_link,
        'Жанр': genres,
        'Комментарии': comments,
    }
    return book


def main():
    parser = argparse.ArgumentParser(description='Get book')
    parser.add_argument('--start_page', default=1, type=int, help='Начальная страница')
    parser.add_argument('--end_page', default=get_category_last_page(), type=int, help='Конечная страница')
    parser.add_argument('--book_folder', default='books', type=str, help='Папка для скачивания книг')
    parser.add_argument('--pic_folder', default='images', type=str, help='Папка для скачивания картинок')
    parser.add_argument('--skip_imgs', action='store_true', help='Не скачивать картинки')
    parser.add_argument('--skip_txt', action='store_true', help='Не скачивать книги')
    parser.add_argument('--json_path', type=str, help='path to JSON')
    args = parser.parse_args()
    books_path = args.book_folder
    images_path = args.pic_folder
    pathlib.Path(books_path).mkdir(exist_ok=True)
    pathlib.Path(images_path).mkdir(exist_ok=True)
    book_links = parse_category(args.start_page, args.end_page)
    books = []
    for book_link in book_links:
        book_id = re.search(r'\d+', book_link).group(0)
        payload = {'id': book_id}
        try:
            book_page = parse_book_page(book_id)
            book_title = book_page['Заголовок']
            filename = f'{book_id}.{book_title}.txt'
            url = book_page['Картинка']
            if not args.skip_imgs:
                download_image(url, book_id, images_path)
            if not args.skip_txt:
                download_txt('https://tululu.org/txt.php', filename, books_path, params=payload)
            del book_page['Картинка']
            book_folder = Path.cwd() / Path(books_path) / filename
            book_page['Ссылка'] = str(book_folder)
            books.append(book_page)
        except requests.HTTPError:
            pass
    json_path = args.json_path or ''
    pathlib.Path(json_path).mkdir(exist_ok=True)
    filepath_json = Path(json_path) / 'books.json'
    with open(filepath_json, 'w') as my_file:
        json.dump(books, my_file, ensure_ascii=False)




if __name__ == '__main__':
    main()
