from playwright.sync_api import sync_playwright 
from sqlalchemy import create_engine, Column, Table, String, Integer, MetaData
from sqlalchemy.orm import sessionmaker, declarative_base
import time 

counts = 5
count = 0

Base = declarative_base() 
class ColorsTable(Base): 
    __tablename__ = 'colors'
    id = Column(Integer, primary_key=True)
    color_code = Column(String(255))
    score = Column(String(255))

hostname = 'localhost'
username = 'root'
password = 'Bautroixanh12345'
database_name = 'web_scrapping'
connection_url = f'mysql://{username}:{password}@{hostname}/{database_name}'
engine = create_engine(url=connection_url)
table_name = 'colors'
metadata = MetaData() 
table = Table(table_name, metadata, autoload_with=engine)
Session = sessionmaker(bind=engine)
session = Session() 

def to_database(data_point): 
    data_instance = ColorsTable(**data_point)
    session.add(data_instance)
    session.commit()

def finding_color(current_context): 
    retry = 0 
    retries = 3
    while retry < retries: 
        function_definition = ''' 
                    () => {
                    return document.querySelectorAll('div.palette-big_value').length > 0;
                    } 
                    '''      
        try: 
            current_context.wait_for_function(function_definition)
        except TimeoutError: 
            print('The time is out, retrying...')
            retry += 1 
        color_code = current_context.query_selector_all('div.palette-big_value')
        reshaped_color_code = current_context.evaluate(''' (colors) => {
            return colors.map(color => color.textContent);
        }''',  color_code)
        return reshaped_color_code
    print(f'Running out of tries')
def finding_score(current_context): 
    favorite_score = current_context.wait_for_selector('button.btn.btn--secondary.btn--m.btn--with-icon span')
    favorite_text = favorite_score.evaluate('(favorite) => favorite.textContent')
    return favorite_text

with sync_playwright() as pw: 
    print(f'Connecting to web browser')
    browser = pw.chromium.launch(headless=True)
    context = browser.new_context(viewport={
        'width': 1200, 
        'height': 650
    })
    page = context.new_page() 
    page.goto('https://coolors.co/palettes/trending')
    time.sleep(1)

    try: 
        cookies_button = page.wait_for_selector('div.iubenda-cs-opt-group-consent button', timeout=10000)
    except Exception as e: 
        print(f'No cookies button found {e}')
    try: 
        if cookies_button: 
            cookies_button.click()
            print('Cookies button pressed')
    except NameError: 
        print(f"Can't cookies since button wasn't found")
    time.sleep(1)
    try: 
        close_button = page.wait_for_selector('div.modal.modal--m.is-visible div div div a.modal_button-right.modal_close-btn.btn.btn--xs.btn--transparent.btn--icon', timeout=10000)
    except Exception as e: 
        print(f'There is no close button {e}')
    try: 
        if close_button: 
            close_button.click() 
            print('Close button pressed')
    except NameError: 
        print(f"Can't press close since button wasn't found")
    print('Scrolling down the page')
    previous_length = 0
    for index in range(1000): 
        page.evaluate('''() => {
            window.scrollTo(0, document.body.scrollHeight); 
        }''')
        time.sleep(2)
        dots_list = page.query_selector_all('a.link.link--secondary.palette-card_more-btn')
        if index == 0: 
            previous_length = len(dots_list)
        elif index > 0: 
            next_length = len(dots_list)
            if next_length != previous_length: 
                previous_length = next_length 
                continue 
            elif next_length == previous_length: 
                print(f'Reach the bottom of the page')
                break 
    print(f'Total expected scrapped {len(dots_list)}')
    print('Start scrapping the website')
    for dots in dots_list: 
        dots.click() 
        open_button = page.wait_for_selector('a.link div.popover-menu_label:has-text("Open palette")')
        if open_button: 
            context_retry = 0
            context_retries = 3
            while context_retry < context_retries: 
                open_button.click()   
                page.wait_for_timeout(4000)
                try: 
                    new_page = context.pages[-1]
                    if str(new_page.url) == 'https://coolors.co/palettes/trending': 
                        print(f'Fail to load new context')
                        new_page.close()
                        context_retry += 1
                    else: 
                        break
                except TimeoutError: 
                    print(f'Retrying....')
                    context_retry += 1
            time.sleep(1)

            #Finding the scrapped data
            color_retries = 3
            color_retry = 0
            while color_retry < color_retries: 
                try: 
                    color_code = finding_color(current_context=new_page)
                    score = finding_score(current_context=new_page)
                    if color_code and score: 
                        break
                except TimeoutError: 
                    print('Time out for waiting color')
                    color_retry += 1
            data_point = {
                'color_code': color_code, 
                'score': score
            }
            print(data_point)
            for code in color_code: 
                sub_point = {
                    'color_code': code, 
                    'score': score
                }
                to_database(sub_point)
            new_page.close()
        
    page.wait_for_timeout(5000)

    print('Connected successfully to web browser')

    browser.close() 