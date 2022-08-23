# Проект blog-platform
Платформа для блогов — с авторизацией, персональными лентами, с комментариями и подпиской на авторов.
Проект написан на Python/Django.

### Список некоторых используемых технологий/пакетов:

* python==3.7.8
* django==2.2.6
* pillow==7.0.0
* sorl-thumbnail==12.6.3
* django-debug-toolbar==3.2.4
* flake8

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
