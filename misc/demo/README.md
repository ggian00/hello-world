# Quickstart

Install with pip:

    pip install .

Install with poetry:

    poetry install .

Configure with .env (in current working directory):

    MINE=https://mineURL.com
    API=https://APIURL.com

Configure with shell environment variables:

    export MINE=https://mineURL.com
    export API=https://APIURL.com

Run:

    python demo/app.py

    # or with poetry
    poetry run demo/app.py


Run with docker-compose:

    docker compose up

    # Ignore the comments below
    # don't forget to create the .env in the proect root
    # docker build -t demo-python-app .
    # docker run -v $(pwd)/output:/app/output demo-python-app

    # with one command and autoremove of the image
    # docker run --rm -it -v $(pwd)/output:/app/output $(docker build -q .)





