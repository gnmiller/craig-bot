from imgur_python import Imgur
from uuid import uuid4
import requests, tempfile
import pdb # TODO remove

class my_imgur:
    """Wrapper for imgur class to perform API actions"""
    # table of valid image types for this application
    api_key = None
    img_type_dict = None

    def __init__ (self, api_key, secret_key, access_key, refresh_key, album_id, data_types):
        """Init the object with the imgur API key and, if provided, a dict of img data types."""
        if( not isinstance( api_key, str)):
            raise TypeError("Invalid API key.")
        else:
            self.api_key = api_key

        if( isinstance( album_id, str ) ):
            self.my_album = album_id
        else: 
            self.my_album = None

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
        
        self._my_image = None
        self._cur_resp = None
        self._my_uri = None
        self._my_type = None
        self._my_name = None
        self._imgur_client = Imgur({'client_id': api_key, 'client_secret':secret_key, 'access_token':access_key, 'refresh_token':refresh_key})

    def fetch_image( self, image_uri ):
        """Propagate data fields based on supplied URI
        
        Returns:
            A dictionary object of the parsed values.
        """
        try:
            self._my_uri = image_uri
            self._cur_resp = self._get_image_resp( image_uri )
            self._my_image = self.get_image( self._cur_resp )
            self._my_type = self._get_image_type( self._cur_resp )
            self._my_name = self._gen_f_name( self._my_type )
            return { "uri":self._my_uri, "resp":self._cur_resp, "data":self._my_image, "ext":self._my_type, "name":self.my_name }
        except Exception as e:
            print(e)
            return e

    def _get_image_resp ( self, image_uri ):
        """Wrapper for requests.get"""
        return requests.get( image_uri )
    
    def get_image ( self, image_resp ):
        """Wrapper for getting the content field of a requests.models.Response object"""
        try:
            if(not isinstance( image_resp, requests.models.Response )):
                raise TypeError("Invalid data type passed as response while getting image. Got: {}, expected: requests.models.Response".format(type(image_resp)))
        except TypeError as e:
            print(e)
            return -1
        return image_resp.content
    
    def _get_image_type( self, req_resp ):
        """Attempt to determine the type of image file that was fetched. Currently supported formats are svg, png, jpg (jpeg), gif, and web.
        Parameters:
            req_resp: Expects a response object as requests.models.Response

        Returns:
            A string containing a valid extension for the image provided. -1 is returned on an error.
        """
        try:
            if(not isinstance( req_resp, requests.models.Response )):
                raise TypeError("Invalid data type passed as response while getting type. Got: {}, expected: requests.models.Response".format(type(req_resp)))
        except TypeError as e:
            print(e)
            return None

        data_type = req_resp.headers['Content-Type']
        for k in self.img_type_dict.keys():
            if str(k) in data_type:
                d_type=self.img_type_dict[k]
                break
            else: 
                d_type=None
        try:
            if(isinstance(d_type, int)):
                raise TypeError("Invalid image type detected. Expected one of: svg, jpg, png, gif, or web. Hint: {}".format(req_resp.headers['Content-Type']))
        except TypeError as e:
            print(e)
            return -1
        return d_type

    def _gen_f_name( self, image_type ):
        """Generate a random 8 character string to help prevent name collisions then concatenate with a file type"""
        return str(uuid4())[0:7]+str(image_type)
    
    def _gen_rand_name( self ):
        """Spit out a 12 character string for a name/description to avoid collisions"""
        return str(uuid4())[0:11]
    
    def my_upload(self):
        """Wrapper for imgur.image_upload(). Parameters are supplied by calling fetch_image() first.
        
        Returns"""
        try:
            if(self._my_image == None):
                raise Exception("No image file has been fetched. Try fetch_image() first.")
            if(self._cur_resp == None):
                raise Exception("No data response loaded, Try fetch_image() first.")
            if(self._my_uri == None):
                raise Exception("No image loaded, try fetch_image() first.")
            if(self._my_type == None):
                raise Exception("No image type detected, try fetch_image() first.")
        except Exception as e:
            print(e)
            self._my_image = None
            self._cur_resp = None
            self._my_uri = None
            self._my_type = None
            self._my_name = None
            self.my_album = None
            return None
        try:
            with tempfile.NamedTemporaryFile( mode = 'r+b', delete=False ) as f:
                d = f.write( self._my_image )
                f.close()
                upl_resp = self._imgur_client.image_upload(f.name, "Testing post", "Bot test post", self.my_album, 0)
            return upl_resp
        except:
            return None
