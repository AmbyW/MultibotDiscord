import os
import discord
import calendar
import requests
import threading

from discord.ext import commands
from datetime import datetime, date, timedelta
from functools import reduce
from prettytable import PrettyTable

from bot_discord.settings import DISCORD_TOKEN


intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.members = True



bot = commands.Bot(command_prefix="/", intents=intents)

# Función para hacer la solicitud a la API
def fetch_segmento(from_date, to_date):
    url = f"https://api-lok-live.leagueofkingdoms.com/api/stat/land/contribution?landId=138000&from={from_date.strftime('%Y-%m-%d')}&to={to_date.strftime('%Y-%m-%d')}"
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception('Error al obtener los datos')
    return response.json()

def get_date_ranges(from_date, to_date):
    date_starts = from_date
    date_ends = to_date
    date_range = abs(date_starts - date_ends) + timedelta(days=1)
    if date_range.days < 7:
        return [
            (from_date, to_date),
        ]
    range_date_days = date_range.days
    date_list = []
    while range_date_days > 0:
        next_days = 7 if range_date_days >= 7 else range_date_days
        range_date_days -= next_days
        date_list.append(
            (
                date_starts.strftime("%Y-%m-%d"),
                (date_starts + timedelta(days=next_days - 1)).strftime(
                    "%Y-%m-%d"
                ),
            )
        )
        date_starts += timedelta(days=next_days)
    return date_list

def make_urls(land_number, from_date, to_date):
    urls = []
    for date_start, date_end in get_date_ranges(from_date, to_date):
        urls.append(f"https://api-lok-live.leagueofkingdoms.com/api/stat/land/contribution?landId={land_number}&from={date_start}&to={date_end}"
        )
    return urls

def get_lands_data(urls):
    responses = []

    def make_requests(url: str):
        response = requests.get(url)
        if response.ok:
            responses.append(response.json())

    threads_list = []
    threads = len(urls)
    for thread_number in range(threads):
        thread = threading.Thread(
            name=f"requesting_url_no_{thread_number}",
            target=make_requests,
            args=(urls[thread_number],),
        )
        threads_list.append(thread)
        thread.start()

    for thread in threads_list:
        thread.join()

    return responses


# Agrupar los puntos
def agrupar_contribuciones(contribuciones):
    contribuciones_agrupadas = {}
    for contribucion in contribuciones:
        kingdom_id = contribucion['kingdomId']
        total = contribucion['total']
        if kingdom_id in contribuciones_agrupadas:
            contribuciones_agrupadas[kingdom_id]['total'] += contribucion['total']
        else:
            contribuciones_agrupadas[kingdom_id] = {
                'kingdomId': kingdom_id,
                'name': contribucion['name'],
                'total': total,
                'continent': contribucion['continent']
            }
    return list(contribuciones_agrupadas.values())

def process_lands_data(responses):
    lands_contributions = {}
    for data in responses:
        if data.get("result", False):
            for kingdom_contribution in data.get("contribution", []):
                kingdom_id = kingdom_contribution.get("kingdomId", "")
                kingdom_dev = kingdom_contribution.get("total", 0)
                kingdom_name = kingdom_contribution.get("name", "")
                kingdom_continent = kingdom_contribution.get("continent", 0)
                contribution = lands_contributions.get(kingdom_id, {
                    "continent": kingdom_continent,
                    "name": kingdom_name,
                    "total": 0,
                    "kingdomId": kingdom_id
                    })
                contribution["total"] += kingdom_dev
                lands_contributions[kingdom_id] = contribution
    return lands_contributions.values()



# Dividir el mensaje en 2000 para evitar error
async def send_long_message(ctx, message):
    for i in range(0, len(message), 2000):
        await ctx.send(message[i:i+2000])

@bot.command()
async def points(ctx):
    hoy = datetime.today()
    fecha_inicio = date(hoy.year, hoy.month, 1)
    fecha_final = date(hoy.year, hoy.month, calendar.monthrange(hoy.year, hoy.month)[1])
    land = 138000

    try:
        urls = make_urls(land, fecha_inicio, fecha_final)
        responses = get_lands_data(urls)
        contribuciones_totales = process_lands_data(responses)
        suma_total = reduce(
            lambda acumulado, contribucion: acumulado + contribucion['total'],
            contribuciones_totales,
            0
        )
        contribuciones_ordenadas = sorted(contribuciones_totales, key=lambda x: (
            0 if int(x['continent']) == 65 else int(x['continent']) + 1,
            -float(x['total'])
        ))
        rows_per_chunk = 32
        data_chunks = [contribuciones_ordenadas[i:i + rows_per_chunk] for i in range(0, len(contribuciones_ordenadas), rows_per_chunk)]
        table_header = f"📝 **Contribuciones del mes {hoy.strftime('%b')}({suma_total: <10.2f}dvp) en {data_chunks} partes** 📝\n"
        await ctx.send(table_header)
        for i, chunk in enumerate(data_chunks):
            tabla = PrettyTable()
            tabla.field_names = ["Nombre del Reino", "Contribución", "Continente"]
            tabla.align = "l"

            for item in chunk:
                tabla.add_row([
                    item["name"],
                    f"{item['total']:.2f}",
                    f"C{item['continent']}"
                ])
            await ctx.send(f"**Parte {i+1}/{len(data_chunks)}**\n```{tabla}\n```")
    except Exception as e:
       await ctx.send(f"Error: {e}")

@bot.command()
async def daypoints(ctx):
    hoy = datetime.today()
    land = 138000

    try:
        urls = make_urls(land, hoy, hoy)
        resultado = get_lands_data(urls)
        contribuciones_totales = process_lands_data(resultado)
        suma_total = reduce(
            lambda acumulado, contribucion: acumulado + contribucion['total'],
            contribuciones_totales,
            0
        )
        contribuciones_ordenadas = sorted(contribuciones_totales, key=lambda x: (
            0 if int(x['continent']) == 65 else int(x['continent']) + 1,
            -float(x['total'])
        ))
        rows_per_chunk = 32
        data_chunks = [contribuciones_ordenadas[i:i + rows_per_chunk] for i in range(0, len(contribuciones_ordenadas), rows_per_chunk)]

        table_header = f"📝 **Contribuciones del Día ({hoy.strftime("%d-%m-%Y")}) en {data_chunks} partes** 📝\n"
        table_header += f"🌍 **💰 **Total de puntos dados en el día {suma_total: <10.2f}** \n"
        await ctx.send(table_header)
        for i, chunk in enumerate(data_chunks):
            tabla = PrettyTable()
            tabla.field_names = ["Nombre del Reino", "Contribución", "Continente"]
            tabla.align = "l"

            for item in chunk:
                tabla.add_row([
                    item["name"],
                    f"{item['total']:.2f}",
                    f"C{item['continent']}"
                ])
            await ctx.send(f"**Parte {i+1}/{len(data_chunks)}**\n```{tabla}\n```")
    except Exception as e:
        await ctx.send(f"Error: {e}")

@bot.command()
async def limpiar(ctx, cantidad: int = 1000):
    await ctx.channel.purge(limit=cantidad)
    await ctx.send(f"🧹 Se han eliminado {cantidad} mensajes. 🧹", delete_after=5)

bot.run(DISCORD_TOKEN)
