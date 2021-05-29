default:help

help:
	@echo "USAGE"
	@echo "  make <commands>"
	@echo ""
	@echo "AVAILABLE COMMANDS"
	@echo "  run		Start a bot"
	@echo "  black		Run black"
	@echo "  isort		Run isort"
	@echo "  lint		Run black and isort"


# ========
# Commands
# ========

run:
	@python3.8 src/bot.py

black:
	@black --line-length 120 src/

isort:
	@isort src/


lint: black isort
