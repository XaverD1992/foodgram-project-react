# Проект Foodgram 

### Описание
Проект "Foodgram" – это "продуктовый помощник". На этом сервисе авторизированные пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд. Для неавторизированных пользователей доступны просмотр рецептов и страниц авторов. 

### Адрес сервера, на котором запущен проект:
https://vinm.ddns.net/

### Почта и пароль администратора(для входа в админку):
email: lop@mail.ru

password: e1xdD990


### Как запустить проект на сервере в контейнерах:

Клонировать репозиторий и перейти в него в командной строке:

``` git@github.com:XaverD1992/foodgram-project-react.git ``` 
``` cd foodgram-project-react/infra ``` 

Установить на сервере docker и docker-compose.

- Для работы с GitHub Actions необходимо в репозитории в разделе Secrets > Actions создать переменные окружения:
```
SECRET_KEY              # секретный ключ Django проекта
DOCKER_PASSWORD         # пароль от Docker Hub
DOCKER_USERNAME         # логин Docker Hub
HOST                    # публичный IP сервера
USER                    # имя пользователя на сервере
SSH_PASSPHRASE              # *если ssh-ключ защищен паролем
SSH_KEY                 # приватный ssh-ключ
TELEGRAM_TO             # ID телеграм-аккаунта для посылки сообщения
TELEGRAM_TOKEN          # токен бота, посылающего сообщение

DB_ENGINE               # django.db.backends.postgresql
DB_NAME                 # postgres
POSTGRES_USER           # postgres
POSTGRES_PASSWORD       # postgres
DB_HOST                 # db
DB_PORT                 # 5432 (порт по умолчанию)
```

Запустить docker-compose:

```
docker-compose up -d

```

После окончания сборки контейнеров выполнить миграции:

```
docker-compose exec backend python manage.py migrate

```

Создать суперпользователя:

```
docker-compose exec backend python manage.py createsuperuser

```

Загрузить статику:

```
docker-compose exec backend python manage.py collectstatic --no-input 

```

Загрузить инредиенты:

```
sudo docker-compose exec backend python manage.py load_ingredients

```


### Как запустить бэкенд локально:

Клонировать репозиторий и перейти в него в командной строке:

``` git@github.com:XaverD1992/foodgram-project-react.git ``` 
``` cd foodgram-project-react ``` 

Создать и активировать виртуальное окружение:

``` python3 -m venv venv ``` 

* Если у вас Linux/macOS:
    ``` source venv/bin/activate ``` 

* Если у вас Windows:
    ``` source venv/Scripts/activate ```
    
``` python3 -m pip install --upgrade pip ``` 

Установить зависимости из файла requirements:

``` pip install -r requirements.txt ``` 

Выполнить миграции:

``` python3 manage.py migrate ``` 

Запустить проект:

``` python3 manage.py runserver ``` 

### В API доступны следующие эндпоинты:

* ```/api/users/```  Get-запрос – получение списка пользователей. POST-запрос – регистрация нового пользователя. Доступно без токена.

* ```/api/users/{id}``` GET-запрос – персональная страница пользователя с указанным id (доступно без токена).

* ```/api/users/me/``` GET-запрос – страница текущего пользователя. PATCH-запрос – редактирование собственной страницы. Доступно авторизированным пользователям. 

* ```/api/users/set_password``` POST-запрос – изменение собственного пароля. Доступно авторизированным пользователям. 

* ```/api/auth/token/login/``` POST-запрос – получение токена. Используется для авторизации по емейлу и паролю, чтобы далее использовать токен при запросах.

* ```/api/auth/token/logout/``` POST-запрос – удаление токена. 

* ```/api/tags/``` GET-запрос — получение списка всех тегов. Доступно без токена.

* ```/api/tags/{id}``` GET-запрос — получение информации о теге о его id. Доступно без токена. 

* ```/api/ingredients/``` GET-запрос – получение списка всех ингредиентов. Подключён поиск по частичному вхождению в начале названия ингредиента. Доступно без токена. 

* ```/api/ingredients/{id}/``` GET-запрос — получение информации об ингредиенте по его id. Доступно без токена. 

* ```/api/recipes/``` GET-запрос – получение списка всех рецептов. Возможен поиск рецептов по тегам и по id автора (доступно без токена). POST-запрос – добавление нового рецепта (доступно для авторизированных пользователей).

* ```/api/recipes/?is_favorited=1``` GET-запрос – получение списка всех рецептов, добавленных в избранное. Доступно для авторизированных пользователей. 

* ```/api/recipes/is_in_shopping_cart=1``` GET-запрос – получение списка всех рецептов, добавленных в список покупок. Доступно для авторизированных пользователей. 

* ```/api/recipes/{id}/``` GET-запрос – получение информации о рецепте по его id (доступно без токена). PATCH-запрос – изменение собственного рецепта (доступно для автора рецепта). DELETE-запрос – удаление собственного рецепта (доступно для автора рецепта).

* ```/api/recipes/{id}/favorite/``` POST-запрос – добавление нового рецепта в избранное. DELETE-запрос – удаление рецепта из избранного. Доступно для авторизированных пользователей. 

* ```/api/recipes/{id}/shopping_cart/``` POST-запрос – добавление нового рецепта в список покупок. DELETE-запрос – удаление рецепта из списка покупок. Доступно для авторизированных пользователей. 

* ```/api/recipes/download_shopping_cart/``` GET-запрос – получение текстового файла со списком покупок. Доступно для авторизированных пользователей. 

* ```/api/users/{id}/subscribe/``` GET-запрос – подписка на пользователя с указанным id. POST-запрос – отписка от пользователя с указанным id. Доступно для авторизированных пользователей

* ```/api/users/subscriptions/``` GET-запрос – получение списка всех пользователей, на которых подписан текущий пользователь Доступно для авторизированных пользователей.

## Стек технологий
- Python 3.11
- Django
- Django REST Framework
- PostgreSQL
- Docker
- Github Actions

### Автор проекта

**Владислав Суворов** 
