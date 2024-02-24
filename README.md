"# image-scrapping" - Total scrapped data points (Unique scalar color code) was more than 70k, and there was a total of 24k unique color codes out of those, expect the model to learn effectively when the total data points reach to 160k - 240k.

For Color Hunt source, since this page follows the infinite scroll, the Python code also supports user to resume the scrapping process from where it was in the previous scrapping process. 

Each palette of 5 or 4 color codes will be processed step by step to load the scalar color code to the desintated database. 

For Unpslash, the source containing image (Most of the data points have been coming from this source), there will be the newly-created folder while attempting to run the Python file, which will later be used to store the scrapped images, the score feature in this case will be treated as "How many times that image being downloaded". 

For each source, the score feature will be sorted ascendingly and ranked with the targeted variable [0, 1, 2, 3] to avoid potential bias while combining multiple sources and rank all of them once. 

