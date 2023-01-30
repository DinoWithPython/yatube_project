# yatube_project
### Описание проекта
Социальная сеть блогеров, созданная во время обучения на Яндекс.Практикум. Позволяет пользователям создать учетную запись, публиковать записи, подписываться на любимых авторов и отмечать понравившиеся записи, комментировать записи.
### Используемые технологии
![Python](https://img.shields.io/badge/Python-3.7.9-green)
![Django](https://img.shields.io/badge/Django-2.2.16-green)

### Инструкция по запуску
- Установите Python 3.7.9;
### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:
```
git clone https://github.com/LunarBirdMYT/yatube_project
```

```
cd yatube_project
```

Cоздать и активировать виртуальное окружение:

```
python -m venv env
```

```
source env/bin/activate
```

```
python -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

### Запуск проекта
Перейти в папку с файлом manage.py и выполнить миграции:
```
python manage.py migrate
```
После чего запустить проект:
```
python manage.py runserver
```
