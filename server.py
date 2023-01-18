import asyncio
import os

import aiohttp
import pymorphy2

from aiohttp import web
from functools import partial

from articles_processing import process_article


async def analyze_page(
    request: aiohttp.ClientRequest,
    charged_words: list,
    morph: pymorphy2.MorphAnalyzer
):
    params = request.rel_url.query.get('urls')
    if not params:
        return web.json_response({'error': "no params passed"})
    if len(params) > 10:
        return web.json_response({'error': "too many urls in request, should be 10 or less"}, status=400)
    urls = params.split(',')
    tasks = []
    async with asyncio.TaskGroup() as tg:
        for url in urls:
            task = tg.create_task(process_article(url, charged_words, morph))
            tasks.append(task)
    response_data = []
    for task in tasks:
        result = task.result()
        response_data.append(
            {
                'url': result[0],
                'status': result[1].name,
                'score': result[3],
                'words_count': result[2],
            }
        )
    return web.json_response(response_data)


with open(os.path.join('.', 'data', 'negative_words.txt'), 'r', encoding='UTF-8') as file:
    charged_words = [readline.strip() for readline in file]
morph = pymorphy2.MorphAnalyzer()
callback = partial(analyze_page, charged_words=charged_words, morph=morph)
app = web.Application()
app.add_routes([web.get('/', callback)])
web.run_app(app)
