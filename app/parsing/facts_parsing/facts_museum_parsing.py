import aiohttp
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from openai import AsyncOpenAI
import aiohttp, aiofiles
from app.core.config import config



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
        # if fact_text:
        #     fact_text = await generate_fact(fact_text)
        return fact_text, fact_image
    else:
        return None
            
            

async def generate_fact(fact):
    client = AsyncOpenAI(
        base_url=config.open_router.base_url,
        api_key=config.open_router.api_key,
    )
    async with aiofiles.open('app/parsing/facts_parsing/facts_prompt.txt', 'r') as f:
        prompt_template = await f.read()
        
    prompt = prompt_template.format( # Можно вынести в конфиг
        max_chars=250,
        channel_tag='https://t.me/world_of_amazing_facts',
        fact=fact,
    )
    
    
    completion = await client.chat.completions.create(
        model=config.open_router.model,
        messages=[
            {
            "role": "user",
            "content": prompt
            }
        ]
    )
    fact = completion.choices[0].message.content
    return fact.strip() if fact else "⚠️ Не удалось сгенерировать факт."


        
        
if __name__ == '__main__':
    import asyncio
    asyncio.run(fact_parse())