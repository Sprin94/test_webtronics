
# Тестовое задание

Python developer

## Стек

Python, FastAPI, Docker, Docker-compose, PostgreSQL, Redis, Pytest.


## Приложение
Приложение - социальная сеть.   
Доступна регистраци и аутентификация по JWT токену.   
Пользователи имею возможность создавать посты и ставить лайки на чужие посты(При самолайке вернется ошибка).   
Документация по API доступна по ссылке /docs после поднятия приложения.


# Использование
### Без docker
1. Склонируйте данный репозиторий на свою локальную машину
2. Убедитесь, что у вас установлен пакет [Poetry](https://python-poetry.org/docs/)
3. Установите зависимости командой:
```sh
poetry install # или poetry install --with dev (для зависимостей разработки)
```
4. Заполните .env файл согласно образцу.
5. Выполните миграции:
```
alembic upgrade head
```
6. Запустите приложение:
```
python -m app.main
```

### Использование через docker
1. Склонируйте данный репозиторий на свою локальную машину
2. Заполните .env файл согласно образцу   
3. Выполните команду:
```sh
docker-compose up --build -d
```


### Тесты
1. Установите зависимости командой:
```sh
poetry install --with dev
```
2. Выполните:
```
pytest
```
