# Covid-19_Dashboard
Covid-19 Death Perception under Prof. Veena Bansal IITK

Requirements:
PC with Python 3.8.x or later

Steps:
    1) Install Required Libraries using command in terminal:  
Pip install os logging dash pandas numpy dash_table dash_bootstrap_components plotly matplotlib io requests schedule time json folium sqlalchemy  
    2) To run the code temporarily, just run dash.py using python. It will return a link that can be opened in any browser (For temporary proposes I have turned off sql queries and storage which can be turned on by uncommenting the code in dashb.py. It will need to have a sql server up and running, with a database named Dashboard on it)  
    3) To permanently run the server you have to run automate.py and wait until 0100 hours for it to run, after that it will update automatically at 0100. Keep the server up   
    
    
    
Hope you like the dashboard
