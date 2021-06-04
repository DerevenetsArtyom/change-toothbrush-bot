default:help

help:
	@echo "USAGE"
	@echo "  make <commands>"
	@echo ""
	@echo "AVAILABLE COMMANDS"
	@echo "  run		Start a bot"
	@echo "  black		Run black"
	@echo "  isort		Run isort"
	@echo "  flake		Run flake8"
	@echo "  lint		Run black, isort and flake8"


# ========
# Commands
# ========

run:
	@python3.8 src/bot.py

black:
	@black --line-length 120 src/

isort:
	@isort src/

flake:
	@flake8 src/


lint: black flake isort
