import aiohttp
import asyncio
import logging
import os
import time

import pymorphy2

from contextlib import asynccontextmanager
from enum import Enum
from urllib.parse import urlparse

from adapters import SANITIZERS
from adapters.exceptions import ArticleNotFound

from text_tools import calculate_jaundice_rate, split_by_words


TEST_ARTICLES = [
    'https://inosmi.ru/not/exist.html',
    'https://dvmn.org/modules/async-python/lesson/jaundice-rate/#9',
    'https://inosmi.ru/20230113/energetika-259651741.html',
]


class ProcessingStatus(Enum):
    OK = 'OK'
    FETCHING_ERROR = 'FETCHING_ERROR'
    TIMEOUT_ERROR = 'TIMEOUT_ERROR'
    PARSING_ERROR = 'PARSING_ERROR'


@asynccontextmanager
async def timer():
    time_start = time.monotonic()

    def get_execution_time():
        return round(time.monotonic() - time_start, 3)
    try:
        yield get_execution_time
    finally:
        pass


async def fetch(session: aiohttp.ClientSession, url: str):
    async with session.get(url) as response:
        response.raise_for_status()
        return await response.text()


async def process_article(
    url: str,
    charged_words: list,
    morph: pymorphy2.MorphAnalyzer,
    timeout=3
):
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(timeout)) as session:
        try:
            html = await fetch(session, url)
        except aiohttp.client_exceptions.ClientResponseError:
            return url, ProcessingStatus('FETCHING_ERROR'), None, None, None
        except asyncio.TimeoutError:
            return url, ProcessingStatus('TIMEOUT_ERROR'), None, None, None
        host = urlparse(url).netloc.replace('.', '_')
        async with timer() as time_used:
            try:
                plaintext = await asyncio.to_thread(SANITIZERS[host], html, plaintext=True)
            except (KeyError, ArticleNotFound):
                return url, ProcessingStatus('PARSING_ERROR'), None, None, None
            try:
                async with asyncio.timeout(timeout):
                    splitted_text = await asyncio.to_thread(split_by_words, morph, plaintext)
            except TimeoutError:
                return url, ProcessingStatus('TIMEOUT_ERROR'), None, None, time_used()
            analyzing_time = time_used()
        return (
            url,
            ProcessingStatus('OK'),
            len(splitted_text),
            calculate_jaundice_rate(splitted_text, charged_words),
            analyzing_time
        )


def test_process_article():
    with open(os.path.join('.', 'data', 'negative_words.txt'), 'r', encoding='UTF-8') as file:
        charged_words = [readline.strip() for readline in file]
    morph = pymorphy2.MorphAnalyzer()
    results = []
    for url in TEST_ARTICLES:
        results.append(asyncio.run(process_article(url, charged_words, morph)))
    assert results[0] == (TEST_ARTICLES[0], ProcessingStatus('FETCHING_ERROR'), None, None, None)
    assert results[1] == (TEST_ARTICLES[1], ProcessingStatus('PARSING_ERROR'), None, None, None)
    assert results[2][0] == TEST_ARTICLES[2]
    assert results[2][1] == ProcessingStatus('OK')
    assert results[2][2] > 0
    assert 0.0 < results[2][3] < 100.0

    timeout_result = asyncio.run(process_article(
        TEST_ARTICLES[2],
        charged_words,
        morph,
        timeout=0.3
    ))
    assert timeout_result[1] == ProcessingStatus('TIMEOUT_ERROR')
