all:
	docker build -t tg-alte-mensa-bot:latest .
	heroku container:push web -a tg-alte-mensa-bot
	heroku container:release web -a tg-alte-mensa-bot

