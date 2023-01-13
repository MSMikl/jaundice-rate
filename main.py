import aiohttp
import asyncio

import pymorphy2

from adapters import SANITIZERS

from text_tools import calculate_jaundice_rate, split_by_words


async def fetch(session, url):
    async with session.get(url) as response:
        response.raise_for_status()
        return await response.text()


async def main(url):
    charged_words = ['жестокость', 'преступность', 'изобличать', 'США']
    async with aiohttp.ClientSession() as session:
        html = await fetch(session, url)
        plaintext = SANITIZERS['inosmi_ru'](html, plaintext=True)
        morph = pymorphy2.MorphAnalyzer()
        splitted_text = split_by_words(morph, plaintext)
        print(len(splitted_text))
        print(calculate_jaundice_rate(splitted_text, charged_words))


if __name__ == '__main__':
    asyncio.run(main('https://inosmi.ru/20230113/dezinformatsiya-259666334.html'))
