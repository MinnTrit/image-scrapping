Total scrapped data points (Unique scalar color code) was more than 70k, and there was a total of 24k unique color codes out of those, expect the model to learn effectively when the total data points reach to 160k - 240k.

For Color Hunt source, since this page follows the infinite scroll, the Python code also supports user to resume the scrapping process from where it was in the previous scrapping process. 

Each palette of 5 or 4 color codes will be processed step by step to load the scalar color code to the desintated database. 

For Unpslash, the source containing image (Most of the data points have been coming from this source), there will be the newly-created folder while attempting to run the Python file, which will later be used to store the scrapped images, the score feature in this case will be treated as "How many times that image being downloaded". 

For each source, the score feature will be sorted ascendingly and ranked with the targeted variable [0, 1, 2, 3] to avoid potential bias while combining multiple sources and rank all of them once. 

### INSTALLING THE NECCESSARIES LIBRARIES
  * Some external libraries for the code that I have been used for this project: 
    * Web crawlling: 
      * Playwright: ```pip install playwright```
    * Data Processing: 
      * Ast: ```pip install AST``` 
      * Pandas: ```pip install pandas```
      * Numpy: ```pip install numpy```
    * Image processing: 
      * Color Thief: ```pip install colorthief```
    * Database interactions: 
      * SQLAlchemy & MySQLClient: ```pip install SQLAlchemy``` & ```pip install mysqlclient```
    * Folder manipulation: 
      * Shutils: ```pip install shutils```
    * Machine Learning libraries: 
      * Pytorch: ```pip install torch``` 
      * Sklearn: ```pip install scikit-learn``` 

### How to use the customized module
  The main purpose of this module is to normalize the scrapped color code coming from Unsplash
  * Removing images with the instance method *removing_image*:
    * Understanding the concept for why it will be essential to remove the images:
      * Not all the images will be displayed with the *download* times on this source. The image scrapping process will indeed crawl all the images equal to that found items printed out in the terminal, but the *image_score* excel file (Which has 1 data point as an example of {'image_name': 0, 'score': 2,540}), will only scrap the sources of images containing the *download* times. Please refer to the image below for more referrence: 
    * ![image](https://github.com/MinnTrit/image-scrapping/assets/151976884/1f4d6d0f-f639-4400-9629-4f83eda54f70)
    * ![image](https://github.com/MinnTrit/image-scrapping/assets/151976884/7f61ca87-0fea-4e84-afca-c496a036e9a6)
  The *removing_images* method will take the *folder of the created scrapped images* as the keyword argument and find its according *image_score excel file* of that crawl (Make sure both the folder and the excel file is in the same directory). It will then convert the "image_name" column of the *image_score excel file* to the list, containing only the images having the *download times* (For some '--' in the score section, it will be replaced with 0), the images in the *scrapped_images folder* which don't have their name in this column list will be removed (The method will also create the back up folder for the scrapped images).
Usage example:
![image](https://github.com/MinnTrit/image-scrapping/assets/151976884/857d7c5b-fb17-42dd-bbb5-dc66696c432b)

  * Extracting the color code from the remaining images: 
    * The class method *color_extracting* of the class *ColorCode* can be used to achieve this desired behavior:
      * It takes in 2 keyword arguments, including *[folder_name, total_code]*. Where *folder_name* refers to the scrapped images folder, and the *total_code* refers to the number of color to be extracted from the image, which is *10* in this case. You can access the result of this process by accessing the attribute *output_list* of this class instance to see the result. 
Usage example: 
![image](https://github.com/MinnTrit/image-scrapping/assets/151976884/9b2336d6-c487-4fba-b66a-3c064ddda9ed)

After the completion of the process, you can refer to *image_output.output_list* to see the result in the dataframe as the following image:
![image](https://github.com/MinnTrit/image-scrapping/assets/151976884/afdaef51-1cbe-467f-a909-82e5a4b1666f)

  * Cleaning up the data frame to push the data to the database:
    * The class method *dataframe_converting* of the class *SubCode* can be used to achieve this desired behavior: 
      * It takes in 1 of these 3 possible keyword arguments, including *[excel file, list, dataframe]*, the excel file section will be divided to 2 sub-sections. The first one is for when the file was saved in the excel file (Your choice to save it or not) after the color extracting process has finsihed, and the second one is designed to work directly with the image score scrapped from the website.
        * For the scrapped images data frame that we have made previously, this method will convert the full color code to break it down to individual color code. For instance, the image *0.png* that we have seen previously has its color codes at ![image](https://github.com/MinnTrit/image-scrapping/assets/151976884/05831e9e-b293-486d-bccf-2e6b540ad46c).
        * This image will then be converted to the following result after calling this method ![image](https://github.com/MinnTrit/image-scrapping/assets/151976884/cca6e6c2-1285-49b1-9bf7-2eb1ed228ad6)
        * For the *image_score excel file*, the purpose is to convert the "image_name" column from *integer number*, for example, *0* to the string with *.png* extension as *0.png* and the "score" column to be cleaned and converted to *integer number*.
        * After calling this class method on the instance, you can refer to the attribute *result* of this instance to access the actual data frame result of this method.
Usage example (You can pass in the dataframe from the previous process, for this example, the contents from the previous process were saved as the excel file):
![image](https://github.com/MinnTrit/image-scrapping/assets/151976884/bc37305d-5a2a-4c7b-8f0f-93c888409f35)

  *Merging the data frame and push the data to the database: 
    * Since you have cleaned up 2 data frames, both for the scrapped images and their image scores, the 2 data frames can join each other on the *image_name* column. Afterward, you can import the method *to_database* from this module to push this data frame to the destinated source. 
Usage example:
![image](https://github.com/MinnTrit/image-scrapping/assets/151976884/125c88b2-4545-4d60-b56c-354ffc9e1df6)

### Preparing the targeted variable for the machine learning model: 
  * As stated previously, each source should be ranked individually to avoid potential bias while fetching data from multiple sources, the code sipnet below will give you the general concept to rank the color code based on the *score* of its own source: 
```
def ranking_column(data_frame): 
    column_list = data_frame.columns.tolist()
    column_list = [column.lower() for column in column_list]
    if 'score' in column_list: 
        quantile = [0, 0.25, 0.5, 0.75, 1]
        labels = [0, 1, 2, 3]
        data_frame['score'] = pd.to_numeric(data_frame['score'])
        data_frame.sort_values(by='score', ascending=True, inplace=True)
        data_frame.insert(len(column_list), 'rank', pd.qcut(data_frame['score'], q=quantile, labels=labels))
    else: 
        print(f"Can't conduct ranking for {data_frame}, no column score found")
    return data_frame
df2 = ranking_column(df2)
df3 = ranking_column(df3) 
df4 = ranking_column(df4)
```
Now that with the targeted vairables and the color codes preproccessed, you can use these data samples to train the model :3, thanks for reading my notes

