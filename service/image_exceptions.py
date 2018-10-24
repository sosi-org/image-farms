"""
    Exception
    Respond404ableException (has 'error')
    ImageException (has imageid, error)
"""
from logger import *
#from custom_responses import error404_response_image_notfound, make_response_jsonified
from custom_responses import make_response_jsonified

# No flask/http modules are imported here.
# Any http/flask-related function is via the `custom_responses` module.

class Respond404ableException(Exception):
    def __init__(self, *ka, **kw):
        #todo: (error,)
        super().__init__(*ka,**kw)
        #The error field (Readable info for API user)
        #self.error = error

        #dont call repr() here: We still haven't finished the constructor.
        #log_err("(R) "+str(type(self))+" "+repr(self))

    def response404(self):
        raise NotImplemented()

class ImageException(Respond404ableException):
    """ Any exception that has imageid """
    def __init__(self, imageid, *ka,**kw):
        super().__init__(*ka,**kw)
        #super().__init__(error, *ka,**kw)
        self.imageid = imageid
        assert type(imageid) is str
        #log_err(""+str(type(self))+" "+repr(self))
        assert self.imageid == imageid
        log_err(""+str(type(self))+":"+str(self.imageid))
    def response404(self):
        raise NotImplemented()

class ImageIdNotFound(ImageException):
    def __init__(self, imageid):
        super().__init__(imageid)
        assert self.imageid == imageid
        assert type(imageid) is str
        #log_err("EEEEEEEEE>>>>>>>>>>>>>>>>>"+str(type(self))+" "+repr(self))

#doesnt work
    #def __repr__(self):
    #    return "<ImageIdNotFound>(%s)"%str(self.imageid)

    #def __init__(self, imageid):
    #    self.imageid = imageid
    def response404(self):
        log_err("self.imageid   "+str(self.imageid  ))
        #return error404_response_image_notfound(self.imageid)   #,self
        info_dict = {'error': "Image not found:"+str(self.imageid), "imageid": self.imageid, 'exception': repr(self)}
        r = make_response_jsonified(info_dict, 404)
        return r
        #{'error': "image not found", "imageid": imageid, 'exception': repr(exception)},


# mess
class UnknownFileFormat(ImageException):
    #def __init__(self, info, excep=None):
        #self.info = info
        #if excep is not None:
        #    self.excep = excep
    def __init__(self, imageid, comment=None, imageio_metadata=None, format=None):
        super().__init__(imageid)
        #self.imageid = imageid
        self.comment = comment
        self.imageio_metadata = imageio_metadata
        self.format = format

    def response404(self, comment=None):
        #if comment is None:
        #    #return error404_response_image_notfound(self.info, self.excep if self.excep is not None else self)
        #    return error404_response_image_notfound(self.imageid)
        #else:
        if True:
            #return uierr.response404(comment="MIME type information could not be found from the orignal image file.")
            #return make_response_jsonified({'error': repr(self.info), 'comment':"MIME type information could not be found from the orignal image file."}, 404)
            # FIXME: call error404_xxxx....
            info_dict = {'error': repr(self.imageid), 'comment':self.comment, "imageio_metadata":self.imageio_metadata, 'format':self.format}
            print("HERE")
            print(info_dict)
            r = make_response_jsonified(info_dict, 404)
            print("rrrrrrrrrrrrrrrrrrrr")
            print(r)
            print("rrrrrrrrrrrrrrrrrrrr")
            return r


class ImageAlreadyExists(ImageException):
    """ e.g. When trying to replace and existing image. """
    def __init__(self, imagename, hashcode):
        """
        @param imagename: the logical name (client-size filename) of the uploaded file.
        @param hashcode: image_id
        """
        super().__init__(hashcode)
        self.imagename = imagename
        #self.imageid = hashcode
        self.hashcode = hashcode
    def response404(self):
        #respondize. stringify. jsonize. repr. 404repr. respond_repr
         return make_response_jsonified({'error': "image already exists.", "imagename": self.imagename, "hashcode": self.hashcode}, 404)



class ImageTooLarge(ImageException):
    """  """
    def __init__(self, imageid, size_pair, volume_bytes):
        super().__init__(imageid)

        assert type(imageid) is str

        #FIXME:; dimension
        self.size_pair = size_pair
        self.volume_bytes = volume_bytes
    def response404(self):
        #respondize. stringify. jsonize. repr. 404repr. respond_repr
         return make_response_jsonified({
             'error': "image too large. maximum %d (bytes), %d x %d" % (service_config['max-size'], service_config['max-width'], service_config['max-width'] ),
             "size_pair": "%d x %d" % self.size_pair,
             "volume_bytes": self.volume_bytes
         }, 404)


class ImageHasNoMask(ImageException):
    def __init__(self, imageid):
        super().__init__(imageid)
        #self.imageid = imageid
        assert type(imageid) is str
    def response404(self):
         return make_response_jsonified({'error': "image has no mask/alpha channel.", "imageid": self.imageid}, 404)
