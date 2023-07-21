from my_imgur import *
from funcs import *
settings = get_settings( 'settings.json' )
imgur_token = settings['imgur']['token']
imgur_secret = settings['imgur']['secret']
imgur_access = settings['imgur']['access']
imgur_refresh = settings['imgur']['refresh']

uri = ["http://192.168.1.233:8080/test-image.jpg","http://192.168.1.233:8080/test-image2.jpg"]
for i in uri:
    imgur_unit = my_imgur( imgur_token, imgur_secret, imgur_access, imgur_refresh, data_types=None )
    data = imgur_unit.fetch_image( uri )
    imgur_data = imgur_unit.my_upload()