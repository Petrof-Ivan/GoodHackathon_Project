# placeReviewBot
This Telegram bot makes it possible to leave a review of a landscaped area by scanning a QR code of this area.

## Getting started
`Python 3` is used in this project.

Install required Python packages:
```
$ pip3 install -r ../pip-requirements.txt
```

Setup the database:
```
$ python3 manage.py migrate
```

Start the admin page:
```
$ python3 manage.py runserver
```

Add bot token:
```
$ echo "{TOKEN}" > token.txt
```

Run the bot:
```
$ python3 manage.py bot
```
