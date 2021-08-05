# Change Toothbrush Bot - never forget to update things

![](https://github.com/DerevenetsArtyom/change-toothbrush-bot/actions/workflows/main.yml/badge.svg) 
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/) 
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com) 
![](https://img.shields.io/github/license/DerevenetsArtyom/change-toothbrush-bot)

The [bot](https://t.me/change_toothbrush_bot) that allows you to schedule your recurring tasks and get notified about it beforehand!

## 🔮 Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.


### Installing

Python version (minimal) required: `3.8`   
It's recommended to use `venv` or `virtualenv` for better isolation.  

```
python3 -m venv env
source env/bin/activate
```

Install the requirements:  
```
pip install -r requirements.txt
```


Put all necessary parameters into **.env** file.  
There is an example **.env.default**.  
At least your telegram token should be present as variable for correct work.

```
TELEGRAM_TOKEN = 'your token'
```

## ☄️ Running the tests and checking the codestyle

To run the tests:
```
pytest tests/
```

To verify that the code adheres to the project conventions:
```
make lint
```
That will run `black`, `isort` and `flake` checks.

## 🤖 Usage

Local usage is pretty simple - just run from the root directory
```
python3.8 src/bot.py
```

Instruction for translating messages:
```
# Step 1: extract texts
pybabel extract --input-dirs=src/ --output=locale/change-toothbrush-bot.pot --project=change-toothbrush-bot
 
# Step 2: create *.po files. E.g. create en, ru, uk locales.
pybabel init --locale=ru_RU --input-file=locale/change-toothbrush-bot.pot --output-dir=locale 
 
# Step 3: translate texts located in locale/{language}/LC_MESSAGES/*.po
 
# Step 4: compile translations
pybabel compile --directory=locale --statistics
 
# Step 5: When you change the code of your bot you need to update po & mo files.
#     Step 5.1: regenerate pot file:
          pybabel extract --input-dirs=src/ --output=locale/change-toothbrush-bot.pot --project=change-toothbrush-bot
#     Step 5.2: update po files
          pybabel update --output-dir=locale --input-file=locale/change-toothbrush-bot.pot
#     Step 5.3: update your translations (location and tools you know from step 3)
#     Step 5.4: compile mo files
          pybabel compile --directory=locale --statistics
```

You may take a look at [Makefile](Makefile) to get some insight about the usage.

## 🙋‍♂️ Hacking

PR's are welcome

## 🛠 Built With

* [`Python 3.8`](https://www.python.org/)
* [`python-telegram-bot`](https://python-telegram-bot.org/)
* [`Peewee ORM`](http://docs.peewee-orm.com/)

## 😍 Authors

* **[Artem Derevenets](https://github.com/DerevenetsArtyom)** - *Initial work*

## 👩‍💼 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
