from playwright.sync_api import sync_playwright 
from sqlalchemy import Table, MetaData, create_engine, Column, String, Integer
from sqlalchemy.orm import declarative_base, sessionmaker
import time 

Base = declarative_base() 

class ColorDrop(Base): 
    __tablename__ = 'color_drop'
    id = Column(Integer, primary_key=True)
    color_code = Column(String(255))
    score = Column(Integer)

hostname = 'localhost'
username = 'root'
password = 'Bautroixanh12345'
database_name = 'web_scrapping'
connection_url = f'mysql://{username}:{password}@{hostname}/{database_name}'
engine = create_engine(url=connection_url)
Session = sessionmaker(bind=engine) 
session = Session() 
metadata = MetaData()
table_name = 'color_drop'
table = Table(table_name, metadata, autoload_with=engine)

def to_database(data_point): 
    data_instance = ColorDrop(**data_point)
    session.add(data_instance)
    session.commit()

def cleaning_code(input_sentence): 
    input_sentence = input_sentence.replace('#', '')
    return input_sentence 

def normalizing_score(input_sentence): 
    input_sentence = input_sentence.strip() 
    return input_sentence

def finding_color(color_list, index):
    color_code = color_list[index].query_selector_all('div.colors div span')
    color_code = page.evaluate('''(colors) => {
        return colors.map(color => color.textContent);
    }''', color_code)
    color_code = [cleaning_code(color) for color in color_code]
    return color_code

def finding_score(score_list, index): 
    score = score_list[index].text_content()
    reshaped_score = normalizing_score(score)
    return reshaped_score

def scrolling_pages():
    pass 

with sync_playwright() as pw: 
    print('Connecting to the browser')
    browser = pw.chromium.launch(headless=True)
    context = browser.new_context(viewport={'width': 1200, 
                                            'height': 600})
    page = context.new_page() 
    page.goto('https://colordrop.io')
    time.sleep(2)
    print(f'Start scrolling down the pages')
    current_length = 0
    for index in range(100): 
        if index == 0: 
            total_items = len(page.query_selector_all('div.row div.tiny-6.small-4.medium-3.large-2.wide-1'))
            current_length += total_items
        elif index > 0: 
            page.evaluate(''' () => {
                window.scrollTo(0, document.body.scrollHeight); 
            }''')
            time.sleep(2.5)
            new_length = len(page.query_selector_all('div.row div.tiny-6.small-4.medium-3.large-2.wide-1'))
            if current_length < new_length: 
                current_length = new_length
            elif current_length == new_length: 
                print('Reached the bottom of the page')
                break
    print(f'Expected total scrapped items at {current_length}')
    print('Start scrapping the page')
    #Finding all the colors code 
    color_list = page.query_selector_all('div.row div.tiny-6.small-4.medium-3.large-2.wide-1')
    #Finding all the favorite score 
    score_list = page.query_selector_all('span.like-count')
    scraped_count = 0
    for index in range(len(color_list)): 
        codes = finding_color(color_list, index)
        score = finding_score(score_list, index)
        data_item = {
            'color_code': codes, 
            'score': score
        }
        print(data_item)
        for sub_code in codes:
            data_point = { 
                'color_code': sub_code, 
                'score': score
            }
            to_database(data_point)
        scraped_count += 1
    print(f'Total scrapped items {scraped_count}') 

    print('Connected successfully to the browser')
    context.close() 
    browser.close() 
    