# Assignment: HTTP-based API

Develop an [HTTP-based API](#task-1-http-based-api) capable of handling the GET request described below. Our stack is based on Flask, but you are free to choose any Python framework you like. All data returned is expected to be in JSON format. Please demonstrate your knowledge of SQL (as opposed to using ORM querying tools).


Implement an API endpoint that takes the following parameters:

* date_from
* date_to
* origin
* destination

and returns a list with the average prices for each day on a route between port codes *origin* and *destination*. Return an empty value (JSON null) for days on which there are less than 3 prices in total.

Both the *origin, destination* params accept either port codes or region slugs, making it possible to query for average prices per day between geographic groups of ports.

    curl "http://127.0.0.1/rates?date_from=2016-01-01&date_to=2016-01-10&origin=CNSGH&destination=north_europe_main"

```
    [
        {
            "average_price": "1077",
            "day": "2016-01-01"
          },
          {
            "average_price": "1077",
            "day": "2016-02-02"
          }
        ...
    ]
```

# Initial setup

To start off you will need to clone the GIT repository:

```bash
git clone https://github.com/shaikhsdf/rates-repo.git
```

You can execute the Dockerfile by running:

```bash
docker image build -t xeneta .
```

This will create a container with the name *xeneta*, which you can view by the following command:

```bash
docker image ls
```

This will create a container with the name *xeneta*, which you can view by the following command:

```bash
docker container run --net=host -p 5000:5000 xeneta
```

by running the container you must now be able to see the message *Running on http://127.0.0.1:5000*

Now, that the app is running we can access the api either by using *curl "http://127.0.0.1:5000/rates?date_from=2016-01-01&date_to=2016-01-10&origin=CNSGH&destination=north_europe_main"* in terminal or by directing going to http://127.0.0.1:5000/rates?date_from=2016-01-01&date_to=2016-01-10&origin=CNSGH&destination=north_europe_main  on your choice of browser or postman.

Feel free to use test the url with your choice of data in the params


Incase, you face any issue with the dockerfile you can still run the app by manually installing requirements.txt file:

```
pip install -r requirements.txt
```

*Make sure you create a new virtual environment* - Always a good idea!!!


# Database setup

I have used the provided database and data so, to make the setup we need to create an empty database and populate it with the data from rates.sql located in *db* folder.

Well you can also set it up by following the below steps:

```bash
docker build -t xeneta-db .
```

This will create a container with the name *xeneta*


Pull Docker PostgreSQL Image:

```bash
docker pull postgres
```


You can start the container for port 5432 so that you can connect to the exposed postgres instance via the IP *127.0.0.1* or *172.17.0.1* or *localhost*: 


```bash
docker run -p 0.0.0.0:5432:5432 xeneta-db
```

To connect with the db you can either use PGAdmin and connect using user as *postgres* and password *ratestask* or via following command:

```bash
PGPASSWORD=ratestask psql -h 127.0.0.1 -U postgres
```

Once you are connected to the database you must be able to view the tables in schema. If not than try running the db/rates.sql in PGAdmin.

