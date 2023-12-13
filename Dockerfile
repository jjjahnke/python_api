FROM	python:3.11.7-alpine3.18
WORKDIR /app
COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY ./src ./src
