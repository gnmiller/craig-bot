from imgur_python import Imgur
import requests

class my_imgur:
    """Wrapper for imgur class to perform API actions"""
    # table of valid image types for this application
    api_key = -1
    img_type_dict = -1
    def __init__ (self, api_key, data_types):
        """Init the object with the imgur API key and, if provided, a dict of img data types."""
        if( not isinstance( api_key, string)):
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

    def get_image_resp ( image_uri ):
        """Wrapper for requests.get"""
        return requests.get( image_uri )
    
    def get_image ( image_resp ):
        """Return the content from a reqeusts response"""
        try:
            if(not isinstance( req_resp, requests.models.Response )):
                raise TypeError("Invalid data type passed as response. Got: {}, expected: requests.models.Response".format(type(req_resp)))
        except TypeError as e:
            print(e)
            return -1
        return req_resp.content

    def get_image_type( req_resp ):
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
                raise TypeError("Invalid data type passed as response. Got: {}, expected: requests.models.Response".format(type(req_resp)))
        except TypeError as e:
            print(e)
            return -1

        data_type = req_resp.headers['Content-Type']
        for k in img_type_dict.keys():
            if str(k) in data_type:
                d_type=img_type_dict[k]
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

    def gen_f_name( image_type ):
        """Generate a random 8 character string to help prevent name collisions then concatenate with a file type"""
        return str(uuid4())[0:7]+str(image_type)
    
