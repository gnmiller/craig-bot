from my_imgur import *
from funcs import *
settings = get_settings( 'settings.json' )
imgur_token = settings['imgur']['token']
imgur_secret = settings['imgur']['secret']
imgur_access = settings['imgur']['access']
imgur_refresh = settings['imgur']['refresh']
bot_album = settings['bot']['album_id']

uri = ["http://192.168.1.233:8080/test-image3.jpg","http://192.168.1.233:8080/test-image2.jpg"]
for i in uri:
    imgur_unit = my_imgur( api_key=imgur_token, 
                          secret_key=imgur_secret,  
                          access_key=imgur_access, 
                          refresh_key=imgur_refresh, 
                          data_types=None, 
                          album_id=bot_album, 
                          db_file="craig-bot.sql" )
    data = imgur_unit.fetch_image( i )
    imgur_data = imgur_unit.my_upload()