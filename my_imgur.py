from imgur_python import Imgur
from uuid import uuid4
import requests

class my_imgur:
    """Wrapper for imgur class to perform API actions"""
    # table of valid image types for this application
    api_key = -1
    img_type_dict = -1

    def __init__ (self, api_key, secret_key, access_key, refresh_key, data_types):
        """Init the object with the imgur API key and, if provided, a dict of img data types."""
        if( not isinstance( api_key, str)):
            raise TypeError("Invalid API key.")
        else:
            self.api_key = api_key
        if( isinstance( data_types, dict)):
            self.img_type_dict = data_types
        else:
            self.img_type_dict = {
                'svg':'.svg',
                'png':'.png',
                'jpg':'.jpg',
                'jpeg':'.jpeg',
                'gif':'.gif',
                'webm':'.webm'
            }
        self.my_image = -1
        self.cur_resp = -1
        self.my_uri = -1
        self.my_type = -1
        self.my_name = -1
        self.imgur_client = Imgur({'client_id': api_key, 'client_secret':secret_key, 'access_token':access_key, 'refresh_token':refresh_key})

    def fetch_image( self, image_uri ):
        self.my_uri = image_uri
        self.cur_resp = self.get_image_resp( image_uri )
        self.my_image = self.get_image( self.cur_resp )
        self.my_type = self.get_image_type( self.cur_resp )
        self.my_name = self.gen_f_name( self.my_type )

    def get_image_resp ( self, image_uri ):
        """Wrapper for requests.get"""
        return requests.get( image_uri )
    
    def get_image ( self, image_resp ):
        """Return the content from a reqeusts response"""
        try:
            if(not isinstance( image_resp, requests.models.Response )):
                raise TypeError("Invalid data type passed as response while getting image. Got: {}, expected: requests.models.Response".format(type(image_resp)))
        except TypeError as e:
            print(e)
            return -1
        return image_resp.content
    
    def get_image_type( self, req_resp ):
        """Attempt to determine the type of image file that was fetched. Currently supported formats are svg, png, jpg (jpeg), gif, and web.
        Parameters:
            req_resp: Expects a response object as requests.models.Response

        Returns:
            A string containing a valid extension for the image provided. -1 is returned on an error.
        Excepts:
            TypeError: If a valid image content-type is not detected.
        """
        try:
            if(not isinstance( req_resp, requests.models.Response )):
                raise TypeError("Invalid data type passed as response while getting type. Got: {}, expected: requests.models.Response".format(type(req_resp)))
        except TypeError as e:
            print(e)
            return -1

        data_type = req_resp.headers['Content-Type']
        for k in self.img_type_dict.keys():
            if str(k) in data_type:
                d_type=self.img_type_dict[k]
                break
            else: 
                d_type=-1
        try:
            if(isinstance(d_type, int)):
                raise TypeError("Invalid image type detected. Expected one of: svg, jpg, png, gif, or web. Hint: {}".format(req_resp.headers['Content-Type']))
        except TypeError as e:
            print(e)
            return -1
        return d_type

    def gen_f_name( self, image_type ):
        """Generate a random 8 character string to help prevent name collisions then concatenate with a file type"""
        return str(uuid4())[0:7]+str(image_type)
    
    def my_upload(self):
        try:
            if(self.my_image == -1):
                raise Exception("No image file has been fetched. Try fetch_image() first.")
            if(self.cur_resp == -1):
                raise Exception("No data response loaded, Try fetch_image() first.")
            if(self.my_uri == -1):
                raise Exception("No image loaded, try fetch_image() first.")
            if(self.my_type == -1):
                raise Exception("No image type detected, try fetch_image() first.")
            
        except Exception as e:
            print(e)
            self.my_image = -1
            self.cur_resp = -1
            self.my_uri = -1
            self.my_type = -1
            self.my_name = -1
            return -1
        import pdb
        import tempfile
        with tempfile.NamedTemporaryFile( mode = 'r+b', delete=False ) as f:
            d = f.write( self.my_image )
            f.close()
            upl_resp = self.imgur_client.image_upload(f.name, "Testing post", "Bot test post", "Application Album", 0)
        print( upl_resp )
