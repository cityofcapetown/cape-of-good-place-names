FROM python:3.6-alpine

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

RUN apk update && apk add git

COPY requirements.txt /usr/src/app/
RUN pip3 install --no-cache-dir -r requirements.txt

RUN apk del git

COPY . /usr/src/app

EXPOSE 8000

ENTRYPOINT ["python3"]

CMD ["-m", "cape_of_good_place_names"]