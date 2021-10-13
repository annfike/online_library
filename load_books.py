import requests
import pathlib
from pathlib import Path

# url = "https://tululu.org/txt.php?id=32168"
#
# response = requests.get(url)
# response.raise_for_status()
#
# filename = 'sand_of_mars.txt'
# with open(filename, 'wb') as file:
#     file.write(response.content)


def load_book(path, filename, url, params=None):
    filepath = Path(path) / filename
    response = requests.get(url, params=params)
    response.raise_for_status()
    with filepath.open('wb') as file:
        file.write(response.content)


path = 'books'
pathlib.Path(path).mkdir(exist_ok=True)
for index in range(1,11):
    url = "https://tululu.org/txt.php"
    payload = {"id": index}
    filename = f'book{index}.txt'
    filepath = Path(path) / filename
    response = requests.get(url, params=payload)
    response.raise_for_status()
    with filepath.open('wb') as file:
        file.write(response.content)