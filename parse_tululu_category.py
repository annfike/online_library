import argparse
import os
import pathlib
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit
import json

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def parse_categorye(start_page, end_page):
    for page in range(start_page, end_page):
        url = f'https://tululu.org/l55/{page}'
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')
        book_selector = '.bookimage a'
        book_tags = soup.select(book_selector)
        books = [book['href'] for book in book_tags]
        book_pages = [urljoin('https://tululu.org', book) for book in books]
        return book_pages
        

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
    title_selector = "body h1"
    title_tag = soup.select_one(title_selector)
    title, author = title_tag.text.split('::')
    title, author = title.strip(), author.strip()
    pic_selector = ".bookimage img"
    pic = soup.select_one(pic_selector)['src']
    pic_link = urljoin('https://tululu.org', pic)
    genre_selector = "span.d_book a"
    genres_tag = soup.select(genre_selector)
    genres = [genre.text for genre in genres_tag]
    comments_selector = ".texts span"
    comments_tag = soup.select(comments_selector)
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
    books_path = 'books'
    images_path = 'images'
    pathlib.Path(books_path).mkdir(exist_ok=True)
    pathlib.Path(images_path).mkdir(exist_ok=True)
    parser = argparse.ArgumentParser(description='Get book')
    parser.add_argument('start_page', default=1, type=int, help='Укажите начальную страницу')
    parser.add_argument('end_page', default=1, type=int, help='Укажите конечную страницу')
    args = parser.parse_args()
    book_links = parse_categorye(args.start_page, args.end_page)
    for book_link in book_links:
        parsed = urlsplit(book_link)
        book_id = os.path.split(parsed.path)[0][2:]
        payload = {'id': book_id}
        try:
            book_page = parse_book_page(book_id)
            with open("books.json", "a") as my_file:
                json.dump(book_page, my_file, ensure_ascii=False)
            book_title = book_page['Заголовок']
            filename = f'{book_id}.{book_title}.txt'
            url = book_page['Картинка']
            download_image(url, book_id, images_path)
            download_txt('https://tululu.org/txt.php', filename, books_path, params=payload)
        except requests.HTTPError:
            pass



if __name__ == '__main__':
    main()
