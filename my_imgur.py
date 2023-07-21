from imgur_python import Imgur
from uuid import uuid4
import requests, tempfile, sqlite3
import pdb # TODO remove

class my_imgur:
    """Wrapper for imgur class to perform API actions"""
    # table of valid image types for this application
    _img_type_dict = None
    _imgur_client = None
    _my_db_info = None

    def __init__ (self, api_key, secret_key, access_key, refresh_key, album_id, data_types, db_file):
        """Init the object with the imgur API key and, if provided, a dict of img data types."""
        if( not isinstance( api_key, str)):
            raise TypeError("Invalid API key.")
        else:
            self.api_key = api_key

        if( isinstance( album_id, str ) ):
            self._my_album = album_id
        else: 
            self._my_album = None

        if( db_file == None ):
            db_name = "craig-bot"+self._gen_rand_name()+".sql"
            try:
                self._my_db = sqlite3.connect( db_name )
                self._cur = self._my_db.cursor()
                self._init_db( self._my_db, self._cur )
            except Exception as e:
                # not good
                print(e)
                exit()

        if( isinstance( data_types, dict)):
            self._img_type_dict = data_types
        else:
            self._img_type_dict = {
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
        self._db_file = None
        self._imgur_client = Imgur({'client_id': api_key, 'client_secret':secret_key, 'access_token':access_key, 'refresh_token':refresh_key})

    def _init_db( self, cursor ):
        try:
            if( not isinstance( cursor, sqlite3.cursor ) ):
                raise ValueError("sqlite db does not appear to be initialized. Check cursor?")
            stmt = "CREATE TABLE imgur( image_id, url, album_id, upload_date ) IF NOT EXISTS"
            res = cursor.execute( stmt )
        except ValueError as e:
            print(e)
            return None
        return cursor
    
    def _insert_image( self, cursor, resp ):
        """Insert image data into the DB after a successful call to _my_upload"""
        try:
            if( not isinstance( cursor, sqlite3.cursor ) ):
                raise ValueError("sqlite db does not appear to be initialized. Check cursor?")
            #stmt = "INSERT INTO imgur VALUES"
            raise NotImplementedError("NYI")
        except Exception as e:
            print(e)
            return e

    def fetch_image( self, image_uri ):
        """Propagate data fields based on supplied URI
        
        Returns:
            A dictionary object of the parsed values.
        """
        try:
            if( not isinstance( image_uri, str )):
                raise ValueError("Invalid data type passed as image URI. Hint: {}".format(type(image_uri)))
            self._my_uri = image_uri
            self._cur_resp = self._get_image_resp( image_uri )
            self._my_image = self.get_image( self._cur_resp )
            self._my_type = self._get_image_type( self._cur_resp )
            self._my_name = self._gen_f_name( self._my_type )
            return { "uri":self._my_uri, "resp":self._cur_resp, "data":self._my_image, "ext":self._my_type, "name":self._my_name }
        except Exception as e:
            print(e)
            return e

    def _get_image_resp ( self, image_uri ):
        """Wrapper for requests.get"""
        resp = requests.get( image_uri )
        if(not resp.status_code == 200):
            raise Exception("Invalid status caught from requests. Got {}, expected 200. URI: {}".format( resp.status_code, image_uri))
        else:
            return resp
    
    def get_image ( self, image_resp ):
        """Wrapper for getting the content field of a requests.models.Response object"""
        try:
            if(not isinstance( image_resp, requests.models.Response )):
                raise ValueError("Invalid data type passed as response while getting image. Got: {}, expected: requests.models.Response".format(type(image_resp)))
        except ValueError as e:
            print(e)
            return None
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
                raise ValueError("Invalid data type passed as response while getting type. Got: {}, expected: requests.models.Response".format(type(req_resp)))
            if(not req_resp.status_code == 200):
                raise Exception("Invalid status code for image URI ({}). Status: {}".format( self._my_type, req_resp.status_code))
            data_type = req_resp.headers['Content-Type'] # extract HTML data type to guess format
            for k in self._img_type_dict.keys():
                if str(k) in data_type:
                    d_type=self._img_type_dict[k]
                    break
                else: 
                    d_type=None
        except ValueError as e:
            print(e)
            return None

        try:
            if(isinstance(d_type, int)):
                raise ValueError("Invalid image type detected. Expected one of: svg, jpg, png, gif, or web. Hint: {}".format(req_resp.headers['Content-Type']))
        except TypeError as e:
            print(e)
            return None
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
            pdb.set_trace()
            if( self._imgur_client == None ):
                raise AssertionError("Imgur client not connected. Check API keys?")
            if(self._my_image == None):
                raise AssertionError("No image file has been fetched. Try fetch_image() first.")
            if(self._cur_resp == None):
                raise AssertionError("No data response loaded, Try fetch_image() first.")
            if(self._my_uri == None):
                raise AssertionError("No image loaded, try fetch_image() first.")
            if(self._my_type == None):
                raise AssertionError("No image type detected, try fetch_image() first.")
        except AssertionError as e:
            print(e)
            self._my_image = None
            self._cur_resp = None
            self._my_uri = None
            self._my_type = None
            self._my_name = None
            self._my_album = None
            return None
        try:
            with tempfile.NamedTemporaryFile( mode = 'r+b', delete=False ) as f:
                d = f.write( self._my_image )
                f.close()
                upl_resp = self._imgur_client.image_upload(f.name, "Testing post", "Bot test post", self.my_album, 0)
                pdb.set_trace()
            return upl_resp
        except:
            return None

    def my_delete( self, image_id ):
        """Wrapper for imgur.client_delete()"""
        return self._imgur_client.client_delete( image_id )
