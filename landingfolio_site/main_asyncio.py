import asyncio
import aiohttp
import aiofiles
import json
import os
import time

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"
}


async def get_data_file(headers):
    """Collect data and return a JSON file"""

    # url = "https://www.landingfolio.com/"

    # r = requests.get(url=url, headers=headers)

    # with open("index.html", "w") as file:
    #     file.write(r.text)

    offset = 0
    img_count = 0
    result_list = []
    async with aiohttp.ClientSession() as session:
        flag = True
        while flag:
            url = f"https://s1.landingfolio.com/api/v1/inspiration/?offset={offset}&color=%23undefined"
            response = await session.get(url=url, headers=headers)
            data = await response.json(content_type=None)

            for item in data:
                if "description" in item:

                    images = item.get("images")
                    img_count += len(images)

                    for img in images:
                        img.update({"url": f"https://landingfoliocom.imgix.net/{img.get('url')}"})

                    result_list.append(
                        {
                            "title": item.get("title"),
                            "description": item.get("description"),
                            "url": item.get("url"),
                            "images": images
                        }
                    )
                else:
                    with open("result_list_asyncio.json", "a", encoding='utf-8') as file:
                        json.dump(result_list, file, indent=4, ensure_ascii=False)

                    print(f"[INFO] Work finished. Images count is: {img_count}\n{'=' * 20}")
                    flag = False
                    break

            print(f"[+] Processed {offset}")
            offset += 1

        try:
            with open("result_list_asyncio.json") as file:
                src = json.load(file)
        except Exception as _ex:
            print(_ex)
            return "[INFO] Check the file path!"

        tasks = []

        for item in src[:100]:
            item_name = item.get("title")
            item_imgs = item.get("images")

            if os.path.exists(f"data2/{item_name}"):
                continue
            else:
                os.mkdir(f"data2/{item_name}")

            for img in item_imgs:
                task = asyncio.create_task(download_imgs(session=session, url=img["url"],
                                                         file_path=f"data2/{item_name}/{img['type']}.png"))
                await asyncio.sleep(0.05)

                tasks.append(task)

        await asyncio.gather(*tasks)


async def download_imgs(session, url, file_path):
    """Download images"""

    async with session.get(url=url) as response:
        response_img = await response.read()

        async with aiofiles.open(file_path, 'wb') as file:
            await file.write(response_img)


def main():
    start_time = time.time()

    asyncio.get_event_loop().run_until_complete(get_data_file(headers=headers))

    finish_time = time.time() - start_time
    print(f"Worked time: {finish_time}")


if __name__ == "__main__":
    main()
