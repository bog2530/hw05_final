# Cоц. сеть для публикации дневников Yatube

### Технологии
- Python 3.8
- Django 2.2.16
- SQLite
- Pytest


## Описание
Cоц. cеть для публикации дневников.

Функционал:
- Регистрация пользователей
- Панель администрирования
- Создание сообщение с загрузкой фотографий, удаление сообщений
- Комментирование
- Подписки на авторов
- Личная страница 
- Создание сообществ


## Как запустить проект

#### Клонировать репозиторий и перейти в него в командной строке:
```
https://github.com/bog2530/hw05_final.git
```

```
cd hw05_final
```

#### Cоздать и активировать виртуальное окружение:
```
python3 -m venv env
```

```
. env/bin/activate
```

#### Установить зависимости из файла requirements.txt:
```
python -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

#### Перейти в рабочую папку 
```
cd yatube
```

#### Выполнить миграции:
```
python manage.py migrate
```

#### Запустить проект:
```
python manage.py runserver
```

## Автор
[Шумский Богдан](https://github.com/bog2530)

Telegram: [@bog2530](https://t.me/bog2530)

Email: bog2530@gmail.com
