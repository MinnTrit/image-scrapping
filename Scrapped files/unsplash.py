from playwright.sync_api import sync_playwright 
import pandas as pd
from urllib.parse import urlparse 
import requests
from PIL import Image
import os 
import io 
import time 

def getting_image(image_source, folder_path):
    for filename, source in enumerate(image_source): 
        filepath = os.path.join(folder_path, str(filename) + '.png')
        retries = 3
        retry = 0
        while retry < retries: 
            try: 
                resposne = None    
                response = requests.get(source)
                if response: 
                    break 
            except Exception as e: 
                print(f'Time out, retrying...')
                retry += 1
        if response.status_code == 200: 
            image = Image.open(io.BytesIO(response.content))
            image.save(filepath)
            print(f'Image downloaded and saved at {filepath}')
        else: 
            print('Failed to download the image')

def getting_score(first_image, page_context, iterations, count): 
    result_list = []
    if first_image: 
        first_image.hover()
        page_context.wait_for_timeout(2000)
        first_image.click() 
        time.sleep(2)
        wait_retry = 0
        wait_retries = 3
    while wait_retry < wait_retries: 
        for index in range(iterations):
            if count == iterations: 
                wait_retry += 3
                break 
            try: 
                download_locator = page_context.query_selector('div._NeDM h3:has-text("Downloads") + span')
                if download_locator: 
                    reshaped_download = download_locator.text_content()
                    image_num = f'{index}'
                    score = reshaped_download
                    data_point = {
                        'image_num': image_num, 
                        'score': score
                    }
                    count += 1
                    print(data_point)
                    result_list.append(data_point)
                elif not download_locator: 
                    print(f'No score found for image number {index}')
                    count += 1
                page_context.keyboard.press('ArrowRight')
                time.sleep(1)
            except Exception as e: 
                print('The time is out, retrying...')
                wait_retry += 1
    return result_list
    
def scrolling_pages(page_context, current_length, threshold): 
    for index in range(1000): 
        if index == 0: 
            pass 
        elif index > 0: 
            viewport_height = page_context.viewport_size['height']
            midpoint = viewport_height // 2
            page_context.evaluate(f'window.scrollBy(0, {midpoint})')
            time.sleep(0.5)
            image_locator = page_context.query_selector_all('div.zmDAx div div img.tB6UZ.a5VGX')
            image_source = [image.get_attribute('src') for image in image_locator]
            next_length = len(image_source)
            if current_length < next_length: 
                current_length = next_length
                print(f'Found items at {current_length}')
            elif current_length >= threshold:
                print(f'Exit scrolling, found items at {current_length}') 
                break
    return image_source

with sync_playwright() as pw:
    print('Connecting to browser...') 
    browser = pw.chromium.launch(headless=True)
    context = browser.new_context(viewport={'height':600, 
                                            'width': 1100})
    page = context.new_page() 
    page.goto('https://unsplash.com')

    #Create the scrapped folder directory
    current_dictory = os.getcwd()
    for index in range(100): 
        folder_name = f'scrapped_images{index}'
        folder_path = os.path.join(current_dictory, folder_name)
        if not os.path.exists(folder_path): 
            try: 
                os.makedirs(folder_path, exist_ok=True)
                print(f'Folder {folder_name} created')
                break 
            except OSError as e: 
                print(f'Error occurred for folder {folder_name}: {e}')
        else: 
            print(f'Folder {folder_name} already existed')
    '''
    Scrolling through the images before scrapping 
    '''
    print('Starting scrolling in first page...') 
    current_length = 24
    # Adjust the threshold for the total scrapped images 
    THRESHOLD = 1000
    image_source = scrolling_pages(page, current_length, THRESHOLD)
    print(f'Expected to scrape {len(image_source)} items')
    '''
    Start the scrapping process to get all the images 
    '''
    getting_image(image_source, folder_path)
    file_list = os.listdir(folder_path)
    image_files = [file for file in file_list if file.endswith('.jpg') or file.endswith('.png')]
    num_images = len(image_files)
    print(f'Total number of images coming from the folder: {num_images}')
    '''
    Retrieving total images to get the according score
    '''
    #Start getting the according score of the image
    print('Start getting score in 2nd page...')
    score_page = context.new_page()
    score_page.goto('https://unsplash.com')
    images_locator = score_page.wait_for_selector('div.zmDAx div.MorZF img')
    all_images = score_page.query_selector_all('div.zmDAx div.MorZF img')
    first_image = all_images[0]
    iterations = len(image_source)
    count = 0
    print(f'Expected getting the total of {iterations} items')
    score_output = getting_score(first_image, score_page, iterations, count)

    df = pd.DataFrame(score_output)
    for i in range(100): 
        filename = f'image_score{i}.xlsx'
        if os.path.exists(filename): 
            continue
        else: 
            df.to_excel(filename)
            break
    print('Saved as excel file')

    page.wait_for_timeout(5000)

    print('Successfully connected to browser')
    context.close() 
    browser.close()