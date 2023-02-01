FROM python:3.8

WORKDIR /xeneta

ADD . /xeneta


RUN pip3 install -r requirements.txt

EXPOSE 5000

CMD ["python", "app.py"]