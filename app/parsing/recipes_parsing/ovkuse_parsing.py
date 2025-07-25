from openai import AsyncOpenAI
import aiohttp, aiofiles
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from app.core.config import config


async def create_recipe():
    recipe = await _parse_recipe()
    print(recipe)
    recipe_text, recipe_image = recipe
    if recipe_text:
        recipe = await generate_recipe(recipe_text)
    return recipe, recipe_image


async def generate_recipe(recipe):
    client = AsyncOpenAI(
        base_url=config.open_router.base_url,
        api_key=config.open_router.api_key,
    )
    async with aiofiles.open('app/parsing/recipes_parsing/recipe_prompt.txt', 'r') as f:
        prompt_template = await f.read()
        
    prompt = prompt_template.format( # Можно вынести в конфиг
        max_chars=900,
        raw_recipe=recipe,
        channel_tag='@best_tasty_recipes'  
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
    recipe = completion.choices[0].message.content
    return recipe.strip() if recipe else "⚠️ Не удалось сгенерировать рецепт."



async def _parse_recipe():
    headers = {'user-agent': UserAgent().chrome}
    random_url = 'https://ovkuse.ru/catalog/random'

    async with aiohttp.ClientSession() as session:
        response = await _try_response(session, random_url, headers)
        if not response:
            return None

        soup = BeautifulSoup(await response.text(), 'lxml')
        recipe_link = soup.find('div', class_='catalog-mt-4')
        if not recipe_link:
            return None

        recipe_url = recipe_link.find('a', class_='catalog-c-button')['href']
        if not recipe_url:
            return None

        response = await _try_response(session, recipe_url, headers)
        if not response:
            return None

        try:
            soup = BeautifulSoup(await response.text(), 'lxml')
            title = soup.find('h1', class_='text-2xl').text
            ingredients = [x.text for x in soup.find('ul', class_='text-grafit').find_all('li')]
            steps = [x.text for x in soup.find('div', class_='mb-4').find_all('div', class_='my-2')]
            image = soup.find('div', class_='swiper-wrapper').find('div', class_='swiper-slide').find('img')['src']

            recipe_text = f"{title}\n" + "\n".join(ingredients) + "\n" + "\n".join(steps)
            return (recipe_text, image)
        except Exception as e:
            return f"Ошибка при парсинге рецепта: {e}"

async def _try_response(session: aiohttp.ClientSession, url, headers):
    try:
        response = await session.get(url, headers=headers)
        if response.ok:
            return response
    except aiohttp.ClientConnectionError:
        pass
    return None