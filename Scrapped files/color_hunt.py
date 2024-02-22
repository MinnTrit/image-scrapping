from playwright.sync_api import sync_playwright
from sqlalchemy import create_engine, Column, String, Integer
import time
from sqlalchemy.orm import sessionmaker, declarative_base 
import copy

Base = declarative_base() 
class ColorHunt(Base): 
    __tablename__ = 'color_hunt'
    id = Column(Integer, primary_key=True)
    color_code = Column(String(255))
    score = Column(String(255))

hostname = 'localhost'
username = 'root'
password = 'Bautroixanh12345'
database_name = 'web_scrapping'
connection_url = f'mysql://{username}:{password}@{hostname}/{database_name}'
engine = create_engine(url=connection_url)
Session = sessionmaker(bind=engine)
session = Session() 

def to_database(input_data): 
    data_instance = ColorHunt(**input_data)
    session.add(data_instance)
    session.commit() 

def cleaning_string(code_list): 
    output_list = []
    for value in code_list: 
        value = value.replace('#', '')
        output_list.append(value)
    return output_list

def getting_code(current_index, code_length, main_page): 
    color_list = main_page.query_selector_all(f'div.item[data-index="{current_index}"] div.place')
    reshaped_color_list = main_page.evaluate('''(colors) => {
return colors.map(color => color.textContent); 
}''', color_list)
    final_color = cleaning_string(reshaped_color_list)
    new_code_length = len(color_list)
    output_color = final_color[code_length:new_code_length]
    if len(output_color) == 4: 
        return output_color, new_code_length
    elif len(output_color) != 4: 
        return False, new_code_length

def getting_favorite(current_index, score_length, main_page): 
    try: 
        favorite_list = main_page.query_selector_all(f'div.item[data-index="{current_index}"] div div.button.like span')
        reshaped_favorite = main_page.evaluate('''(favorites) => {
return favorites.map(favorite => favorite.textContent);
}''', favorite_list)
        new_score_length = len(favorite_list)
        favorite_output = reshaped_favorite[score_length:new_score_length][0]
        return favorite_output, new_score_length
    except AttributeError: 
        pass

def getting_all_features(start_index, 
                         end_index, 
                         main_page,
                         code_length, 
                         score_length,
                         LEFTOFF=None): 
    if LEFTOFF is None: 
        print(f'Start scrapping from index {start_index} - {end_index}')
    result_list = []
    if LEFTOFF is None: 
        for index in range(start_index, end_index):
            color_output, new_code_length = getting_code(index, code_length, main_page)
            if color_output != False: 
                color_output = cleaning_string(color_output)
            if color_output == False:
                print(f'Exit scrapping, found unmatch length') 
                break 
            favorite_output, new_score_length = getting_favorite(index, score_length, main_page)
            if favorite_output: 
                data_point = {
                    'color_code': color_output, 
                    'score': favorite_output
                }
                print(data_point)
                result_list.append(data_point)
            elif not favorite_output:
                print("Exit the scrapping, length doesn't match")
                break
        return result_list, new_code_length, new_score_length
    elif LEFTOFF is not None: 
        pass
    
def scrolling_pages(current_length, main_page, LEFTOFF=None): 
    checking_list = []
    initial_length = len(main_page.query_selector_all('div.item[style]'))
    fix_length = copy.deepcopy(initial_length)
    if LEFTOFF is None: 
        while current_length != (fix_length + 40): 
            main_page.evaluate('''() => {
                window.scrollTo(0, document.body.scrollHeight);
            }''')
            time.sleep(1)
            next_length = main_page.query_selector_all('div.item[style]')
            if current_length not in checking_list: 
                checking_list.append(current_length) 
                print(f'Scrolled through {max(checking_list)} items')
            if current_length < len(next_length): 
                current_length = len(next_length)
        return current_length
    elif LEFTOFF is not None: 
        while current_length < LEFTOFF: 
            main_page.evaluate('''() => {
                window.scrollTo(0, document.body.scrollHeight);
            }''')
            time.sleep(0.5)
            next_length = main_page.query_selector_all('div.item[style]')
            if current_length not in checking_list: 
                checking_list.append(current_length) 
                print(f'Scrolled through {max(checking_list)} items')
            if current_length < len(next_length): 
                current_length = len(next_length)
        return current_length
        
with sync_playwright() as pw: 
    print('Connecting to web browser')
    browser = pw.chromium.launch(headless=True)
    context = browser.new_context(viewport={'width': 1200, 
                                            'height': 600})
    main_page = context.new_page() 
    main_page.goto('https://colorhunt.co')
    waiting_definition = ''' () => {
    return document.querySelectorAll('div.item[data-index="0"] div.place').length > 0; 
    }
'''
    main_page.wait_for_function(waiting_definition)
    print('Starting scrolling...')
    current_length = 40
    code_length = 0
    score_length = 0
    start_index = 0
    end_index = 40
    #Adjust the values for where it was left off 
    PREVIOUS_LEFTOFF = 3280 #Currently at 3280
    #Don't adjust the LEFTOFF variable
    LEFTOFF = PREVIOUS_LEFTOFF + 40 if PREVIOUS_LEFTOFF is not None else None
    for i in range(100): 
        #Dealing with getting the features
        if LEFTOFF is None: 
            try: 
                result_list, new_code_length, new_score_length = getting_all_features(start_index, 
                                                                                end_index, 
                                                                                main_page,
                                                                                code_length, 
                                                                                score_length,
                                                                                LEFTOFF)
            except NameError:
                print('Stopping...')
                break
            for result in result_list: 
                code = result['color_code']
                score = result['score']
                for sub_code in code: 
                    data_point = { 
                        'color_code': sub_code, 
                        'score': score
                    } 
                    to_database(data_point)
            print(f'Pushed to database')
            time.sleep(2)
        elif LEFTOFF is not None: 
            pass
        #Dealing with scrolling down pages 
        if LEFTOFF is None: 
            new_length = scrolling_pages(current_length, main_page, LEFTOFF)
            current_length = copy.deepcopy(new_length)
            code_length = copy.deepcopy(new_code_length)
            score_length = copy.deepcopy(new_score_length)
            time.sleep(2)
        elif LEFTOFF is not None: 
            new_length = scrolling_pages(current_length, main_page, LEFTOFF)
            current_length = copy.deepcopy(new_length)
            print(f'Current length is at {current_length}')
            code_length = int((current_length - 40) / 10)
            score_length = int((current_length - 40) / 40)
            LEFTOFF = None
            time.sleep(2)

    print('Successfully connected to the browser')
    context.close()
    browser.close()
        

