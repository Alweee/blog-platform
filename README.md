# Blog-Platform
### Описание:
Сайт, на котором можно создать свою страницу.
Если на нее зайти, то можно посмотреть все записи автора.
Записи можно отправить в сообщество и посмотреть там посты разных авторов.
Можно подписываться на других авторов и оставлять комментарии под их постами.
Автор может выбрать имя и уникальный адрес для своей страницы.

### Cтек технологий:
[![Python](https://img.shields.io/badge/-Python-464646?style=flat&logo=Python&logoColor=56C0C0&color=008080)](https://www.python.org/)
[![Django](https://img.shields.io/badge/-Django-464646?style=flat&logo=Django&logoColor=56C0C0&color=008080)](https://www.djangoproject.com/)


### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:Alweee/blog-platform.git
```

```
cd yatube
```

Cоздать и активировать виртуальное окружение:

```
python -m venv venv
```

```
source venv/bin/activate
```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python3 manage.py migrate
```

Запустить проект:

```
python3 manage.py runserver
```
