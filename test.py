from my_imgur import *
from funcs import *
settings = get_settings( 'settings.json' )
imgur_token = settings['imgur']['token']
imgur_secret = settings['imgur']['secret']
imgur_access = settings['imgur']['access']
imgur_refresh = settings['imgur']['refresh']

uri = "https://cdn.ttgtmedia.com/rms/ux/responsive/img/tss_tt_logo.png"
imgur_unit = my_imgur( imgur_token, imgur_secret, imgur_access, imgur_refresh, data_types=None )
imgur_unit.fetch_image( uri )
imgur_unit.my_upload()