# Фильтр желтушных новостей

Асинхронный веб-сервер, высчитывающий рейтинг "желтушности" новостных публикаций в интернете.

Пока поддерживается только один новостной сайт - [ИНОСМИ.РУ](https://inosmi.ru/). Для него разработан специальный адаптер, умеющий выделять текст статьи на фоне остальной HTML разметки. Для других новостных сайтов потребуются новые адаптеры, все они будут находиться в каталоге `adapters`. Туда же помещен код для сайта ИНОСМИ.РУ: `adapters/inosmi_ru.py`.

В перспективе можно создать универсальный адаптер, подходящий для всех сайтов, но его разработка будет сложной и потребует дополнительных времени и сил.

# Как установить

Вам понадобится Python версии 3.7 или старше. Для установки пакетов рекомендуется создать виртуальное окружение.

Первым шагом установите пакеты:

```python3
pip install -r requirements.txt
```

# Как запустить

```python3
python server.py
```

# Как использовать

Сервер обрабатывает GET-запросы на корневой путь `'/'` (в случае локального запуска это адрес `http://127.0.0.1:8080`) с параметром `urls`, в котором через запятую можно одновременно передать до 10 адресов страниц с новостями для анализа.

В ответ сервер возвращает json со списком ответов, содержащих url, статус его обработки, количество слов в статье и ее "рейтинг желтушности".

Этот механизм можно использовать для браузерного плагина.

# Как запустить тесты

Для тестирования используется [pytest](https://docs.pytest.org/en/latest/), тестами покрыты фрагменты кода сложные в отладке: text_tools.py, articles_processing.py и адаптеры. Команды для запуска тестов:

```
python -m pytest adapters/inosmi_ru.py
```

```
python -m pytest text_tools.py
```

```
python -m pytest articles_processing.py
```

# Цели проекта

Код написан в учебных целях. Это урок из курса по веб-разработке — [Девман](https://dvmn.org).
