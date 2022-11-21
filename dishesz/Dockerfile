FROM python:3.9
RUN mkdir /code
WORKDIR /code
COPY . /code


RUN pip install --upgrade pip

# uwsgi setup

RUN pip install uwsgi
RUN pip install -r requirements.txt
RUN pip install -U 'Twisted[tls,http2]'

CMD ["uwsgi", "--ini", "/code/backend.ini"]
CMD ["uwsgi", "--socket", "/code/backend.sock", "--module" , "/code/backend.wsgi", "--chmod-socket=666"]
CMD ["python3", "manage.py", "collectstatic"] 