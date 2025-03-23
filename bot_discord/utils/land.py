import requests
import threading

from datetime import timedelta, date
from functools import reduce
from prettytable import PrettyTable
from discord.ext.commands import Context

LAND_ID = 138000


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


def make_urls(from_date, to_date):
    urls = []
    for date_start, date_end in get_date_ranges(from_date, to_date):
        urls.append(
            f"https://api-lok-live.leagueofkingdoms.com/api/stat/land/contribution?landId={LAND_ID}&from={date_start}&to={date_end}"
            )
    return urls


def get_lands_data(urls):
    responses = []

    def make_requests(url: str):
        response = requests.get(url)
        response.raise_for_status()
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


async def show_lands_contributions(ctx: Context, date_from: date, date_to: date):
    urls = make_urls(date_from, date_to)
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
    data_chunks = [contribuciones_ordenadas[i:i + rows_per_chunk] for i in
                   range(0, len(contribuciones_ordenadas), rows_per_chunk)]
    time_frame = "hoy" if date_from == date_to else "mes"
    date_show = date_from.strftime("%B") if time_frame == "mes" else date_to.strftime("%d-%m-%Y")
    table_header = f"📝 **Contribuciones del {time_frame} {date_show} ({suma_total: <10.2f} dvp) en {len(data_chunks)} partes** 📝\n"
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
        await ctx.send(f"**Parte {i + 1}/{len(data_chunks)}**\n```{tabla}\n```")
