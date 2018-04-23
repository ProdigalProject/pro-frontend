FROM python:3.6-slim
WORKDIR /app
ADD . /app
RUN apt update && apt install -y gcc python-dev python3-dev libmysqlclient-dev
COPY requirements.txt /app
RUN pip install -r /app/requirements.txt 
EXPOSE 8000
ENTRYPOINT ["python", "manage.py", "runserver", "0.0.0.0:8000"]
