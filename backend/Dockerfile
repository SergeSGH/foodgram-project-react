FROM python:3.7-slim

WORKDIR /app

COPY /foodgram .

COPY requirements.txt .

RUN pip3 install -r requirements.txt --no-cache-dir

CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000" ]

# CMD ["py foodgram/manage.py runserver"]
