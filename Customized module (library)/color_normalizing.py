import pandas as pd 
from colorthief import ColorThief
from sqlalchemy import create_engine
from sqlalchemy.engine.reflection import Inspector
import shutil
import os 
import ast

#Needs to start over from scrapped 10th
class SubCode:
    def __init__(self, result): 
        self.result = result 

    @staticmethod 
    def extracting(color_code_list, image_list): 
        output_list = []
        for index in range(len(color_code_list)): 
            color_code = color_code_list[index]
            image_name = image_list[index]
            for sub_code in color_code: 
                data_point = {
                    'image_name': image_name,
                    'color_code': sub_code
                }
                output_list.append(data_point)
        output_data_frame = pd.DataFrame(output_list)
        return output_data_frame
    
    @classmethod
    def dataframe_converting(cls, input_data): 
        if isinstance(input_data, str) and input_data.endswith('.xlsx'): 
            data_frame = pd.read_excel(input_data)
            column_list = data_frame.columns.tolist() 
            if 'color_code' in column_list and 'image_name' in column_list: 
                color_code_list = data_frame['color_code'].tolist()
                image_list = data_frame['image_name'] 
                color_code_list = [ast.literal_eval(code) for code in color_code_list]
                result = SubCode.extracting(color_code_list, image_list)
                return cls(result)
            elif 'score' in column_list and 'image_num' in column_list: 
                data_frame['image_num'] = data_frame['image_num'].astype(str) + '.png'
                data_frame.rename(columns={'image_num': 'image_name'}, inplace=True)
                data_frame['score'] = data_frame['score'].str.replace(',', '')
                data_frame['score'] = pd.to_numeric(data_frame['score'])
                data_frame = data_frame.loc[:, ['image_name', 'score']]
                result = data_frame
                return cls(result) 
        elif isinstance(input_data, list): 
            data_frame = pd.DataFrame(input_data)
            color_code_list = data_frame['color_code'].tolist() 
            image_list = data_frame['image_name'].tolist()
            result = SubCode.extracting(color_code_list, image_list)
            return cls(result)
        elif isinstance(input_data, pd.DataFrame): 
            column_list = input_data.columns.tolist() 
            color_code_list = input_data['color_code'].tolist() 
            image_list = input_data['image_name'].tolist() 
            color_code_list = [ast.literal_eval(code) for code in color_code_list]
            result = SubCode.extracting(color_code_list, image_list)
            return cls(result)

def removing_image(folder_name): 
    digit_num = ''
    for character in str(folder_name):  
        if character.isdigit(): 
            digit_num += character
    validate_name = 'image_score' + digit_num + '.xlsx'
    try: 
        inner_df = pd.read_excel(validate_name, names=['image_name', 'score'])
        inner_df['image_name'] = inner_df['image_name'].astype(str) + '.png'
        validate_images = inner_df['image_name'].tolist()
    except Exception: 
        print(f"The file {validate_name} doesn't exist")
    current_directory = os.getcwd()
    folder_path = os.path.join(current_directory, folder_name)
    if os.path.exists(folder_path): 
        print(f'Accessing to folder path {folder_path}')
    else: 
        print('Folder name not found, try again')
        return 
    total_images = os.listdir(folder_path)
    print(f'Found total images at {len(total_images)}')
    delete_count = 0
    for image in total_images: 
        if image not in validate_images: 
            delete_count += 1
    print(f'The total images is at {len(total_images)}')
    print(f'Expected to delete {delete_count} images')
    print(f'Remaining length at {len(total_images) - delete_count}')
    user = input('Continue to delete?(Yes/No)\n The process will create the backup folder')
    if user.lower().startswith('y'): 
        print('Creating the backup folder...')
        current_directory = os.getcwd() 
        source_path = os.path.join(current_directory, folder_name)
        destinated_name = str(folder_name) + '-Copy'
        destinated_path = os.path.join(current_directory, destinated_name)
        if os.path.exists(destinated_path): 
            for index in range(1000): 
                destinated_path, extension = os.path.splitext(destinated_path)
                destinated_path += f'({index})' + extension 
                if not os.path.exists(destinated_path): 
                    break 
        shutil.copytree(source_path, destinated_path)
        print(f'Back up folder created at {destinated_path}')
        for image in total_images: 
            if image not in validate_images: 
                deleted_path = os.path.join(folder_path, image)
                os.remove(deleted_path)
                print(f'Image {image} has been removed')
        print(f'The total of {delete_count} images has been removed')
    elif user.lower().startswith('n'): 
        print('Existing the function')
    else: 
        print('Exiting the function')
        return 

class ColorCode:     
    def __init__(self, output_list): 
        self.output_list = output_list
    
    @staticmethod
    def rgb_to_hex(rgb): 
        return '{:02x}{:02x}{:02x}'.format(*rgb)
    
    @classmethod
    def color_extracting(cls, folder_name, total_code): 
        output_list = []
        current_directory = os.getcwd() 
        folder_path = os.path.join(current_directory, folder_name) 
        total_images = os.listdir(folder_path)
        print(f'Found {len(total_images)} images')
        for image in total_images: 
            image_path = os.path.join(folder_path, image)
            color_thief = ColorThief(image_path)
            palette_list = color_thief.get_palette(color_count=total_code, quality=1)
            hex_list = [ColorCode.rgb_to_hex(rgb) for rgb in palette_list]
            print(f'Image {image} has the color code {hex_list}')
            data_point = {
                'image_name': image, 
                'color_code': hex_list
            }
            output_list.append(data_point)
        return cls(output_list)
        
def to_database(data_frame, table_name): 
    hostname = 'localhost'
    username = 'root'
    password = 'Bautroixanh12345'
    database_name = 'web_scrapping'
    connection_url = f'mysql://{username}:{password}@{hostname}/{database_name}'
    engine = create_engine(connection_url)
    inspector = Inspector(engine)
    if inspector.has_table(table_name): 
        print(f'Processing the table {table_name}')
        total_rows = len(data_frame)
        with engine.connect() as connection: 
            data_frame.to_sql(table_name, con=engine, index=False, if_exists='append')
        print(f'The total rows of {total_rows} has been pushed to the database')
    elif not inspector.has_table(table_name): 
        print(f'The table {table_name} was not found in the dataframe')
