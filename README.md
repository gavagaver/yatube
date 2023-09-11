# YaTube - социальная сеть авторов
[![CI](https://github.com/gavagaver/yatube/actions/workflows/tests.yml/badge.svg?branch=master)](https://github.com/gavagaver/yatube/actions/workflows/tests.yml)

Социальная сеть YaTube позволяет пользователям публиковать посты, комментировать их, а также подписываться на других пользователей. 


## Описание
В проекте реализовано:
- Регистрация пользователей
- Публикация постов с загрузкой изображений
- Комментирование постов
- Лайки постов
- Подписка на авторов
- Пагинация постов
- Написаны тесты


## Установка и запуск
1. [ ] Клонировать репозиторий и перейти в него в командной строке:

```bash
git clone https://github.com/gavagaver/yatube.git && cd yatube
```

1. [ ] Создать и активировать виртуальное окружение:

###### Windows:
```bash
python -m venv venv
```
```bash
source venv/Scripts/activate
```
```bash
python -m pip install --upgrade pip
```
###### Linux:
```bash
python3 -m venv venv
```
```bash
source venv/bin/activate
```
```bash
python3 -m pip install --upgrade pip
```

1. [ ] Установить зависимости
```bash
pip install -r requirements.txt
``` 
1. [ ] Перейти в папку с manage.py

```bash
cd yatube
``` 

1. [ ] Применить миграции
###### Windows:
```bash
python manage.py migrate
```
###### Linux:
```bash
python3 manage.py migrate
```

1. [ ] Запустить проект
###### Windows:
```bash
python manage.py runserver
```
###### Linux:
```bash
python3 manage.py runserver
```


## Стек
- Python 3.7
- Django 2.2
- SQLite3


## Об авторе
Голишевский Андрей Вячеславович  
Python-разработчик (Backend)  
E-mail: gav@gaver.ru  
Telegram: @gavagaver  
Россия, г. Москва  
