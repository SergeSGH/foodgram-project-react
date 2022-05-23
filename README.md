[![foodgram](https://github.com/SergeSGH/foodgram-project-react/actions/workflows/main.yml/badge.svg)](https://github.com/SergeSGH/foodgram-project-react/actions/workflows/main.yml)
# foodgram
### Описание:
проект для записи своих любимых рецептов с картинками
можно подписываться на других авторов и формировать список покупок для магазина
### Технологии:
```
Python, Django, Django REST Framework, PostgreSQL, JavaScript, Yandex Cloud
```
### Войти в админ зону и отредактировать данные проекта можно здесь:
http://foodgram.hopto.org/admin/ (login: admin, pass: admin)

### Автор:
Сергей Приходько

### Как запустить проект: 

Клонировать репозиторий и перейти в него в командной строке:
```
git clone https://github.com/SergeSGH/foodgram-project-react.git
```
```
cd foodgram-project-react
```
В папке проекта создать файл .env в котором определить ключевые переменные:  
```
DB_ENGINE: вид БД
DB_NAME: имя БД
POSTGRES_USER: логин пользователя БД
POSTGRES_PASSWORD: пароль пользователя БД
DB_HOST: приложение БД 
DB_PORT: порт БД
```
Собрать и запустить контейнеры:
```
docker-compose up -d --build
```

Инициировать БД:
```
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```
Перенести первоначальные данные с ингредиентами и рецептами:
```
docker-compose exec web python manage.py loaddata base_dump.json
```
