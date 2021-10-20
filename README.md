# Скрипт для загрузки книг жанра "Научная фантастика"

 - записывает в файл 'books.json' название книги, автора, ссылку на картинку, жанр, комментарии
 - загружает текст книги и картинку
 

## Как установить

 - Python3 должен быть уже установлен.   
 - Затем используйте `pip` (или `pip3`, есть конфликт с Python2) для установки зависимостей:  
```python
   pip install -r requirements.txt
   ```
 - Для запуска скрипта в качестве аргументов надо указать с какой по какую страницы каталога книг по научной фантастике вы хотите скачать книги:  
```python
   parse_tululu_category.py --start_page 'начальная страница' --end_page 'конечная страница'

   Например, следующая команда загрузит книги с 3 по 8 страницы:
   parse_tululu_category.py --start_page 3 --end_page 8
 ```

- Дополнительные (необязательные) аргументы:
```python
   --dest_folder 'папка' - указать папку для скачивания книг и картинок
   --skip_imgs           - не скачивать фотографии
   --skip_txt            - не скачивать книги
   --json_path 'папка'   - указать папку для скачивания файла books.json
```  
 
## Цели проекта

Код написан в учебных целях — это урок в курсе по Python и веб-разработке на сайте [Devman](https://dvmn.org).
