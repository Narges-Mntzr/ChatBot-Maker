# build image
# docker build -t chatbot:latest .
# run container
# docker run --name chatbot --rm -d -p 8000:8000 -it chatbot:latest 

FROM python:3.11-slim

COPY ./requirements.txt app/requirements.txt

RUN pip install -r app/requirements.txt

COPY ./ /app

# for moodel.imgField
RUN python -m pip install Pillow 

# run django apps
CMD ["python", "app/myproject/manage.py", "runserver", "0.0.0.0:8000"]

