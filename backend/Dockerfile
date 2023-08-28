FROM python:3.11
# RUN pip install --upgrade setuptools &&\
#     pip install neuralpy
WORKDIR /app
COPY requirements.txt /app
RUN pip3 install -U pip &&\ 
    pip3 install -r requirements.txt --no-cache-dir
COPY . .
CMD ["gunicorn", "backend.wsgi:application", "--access-logfile '-'", "--error-logfile '-'", "--bind", "0:8000" ]
# CMD ["python", "manage.py", "runserver", "0:8000"] 