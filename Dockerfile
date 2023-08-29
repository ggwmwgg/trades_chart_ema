FROM python:3
ENV PYTHONUNBUFFERED=1
LABEL authors="GGwM"
WORKDIR /app
COPY . /app
RUN pip install --upgrade pip
RUN pip install -r requirements.txt