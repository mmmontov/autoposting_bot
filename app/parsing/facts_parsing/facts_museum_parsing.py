import aiohttp
from bs4 import BeautifulSoup
from fake_useragent import UserAgent



# парсинг факта с сайта
async def fact_parse():
    headers = {'user-agent': UserAgent().random}

    main_url = 'https://facts.museum/'
    async with aiohttp.ClientSession() as session:
        response = await session.get(f'{main_url}/random', headers=headers)
        if response.ok:
            soup = BeautifulSoup(await response.text(), 'lxml')
            try:
                title = soup.find('div', class_='col-lg-5 mb-2').find('h2').text.strip()
                fact_block = soup.find('div', class_='col-lg mb-3 p-0')
                fact_text = fact_block.find('p', class_='content').text
                fact_image = main_url + fact_block.find('img')['src']
                post_text = f'<b>{title}</b>\n\n' + fact_text
                return post_text, fact_image
            except AttributeError:
                return None
        else:
            fact_parse()
        
# промежуточная функция (хз зач)    
async def gather_fact():
    fact = await fact_parse()
    if fact:
        fact_text, fact_image = fact
        return fact_text, fact_image
    else:
        return None
            
            
if __name__ == '__main__':
    import asyncio
    asyncio.run(fact_parse())