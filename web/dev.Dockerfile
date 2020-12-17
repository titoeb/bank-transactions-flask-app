FROM python:3

WORKDIR /usr/web

COPY requirements.txt ./ 

RUN pip install --no-cache-dir -r requirements.txt

ENV FLASK_APP=app.py

ENV FLASK_ENV=development

ENTRYPOINT ["flask", "run", "--host=0.0.0.0"]
