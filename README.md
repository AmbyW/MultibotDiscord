#### run the bot

# created the database
python manage.py migrate

# create a copy of sample_envrc file name .env
cp ./sample_envrc ./.env

# fill .env with the correct values

# run the bot
python bot.py

#### run celery for periodic tasks to fetch automatically contribution from API
celery -A bot_discord worker -B -l debug

#### launch web admin
python manage.py runserver

then visit http://127.0.0.1:8000/admin

