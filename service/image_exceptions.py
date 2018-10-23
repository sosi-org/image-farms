"""
    Exception
    Respond404ableException (has 'error')
    ImageException (has imageid, error)
"""
from logger import *

class Respond404ableException(Exception):
    def __init__(self, *ka, **kw):
        #todo: (error,)
        super().__init__(*ka,**kw)
        #The error field (Readable info for API user)
        #self.error = error
        log_err(type(self))

    def response404(self):
        raise NotImplemented()

class ImageException(Respond404ableException):
    """ Any exception that has imageid """
    def __init__(self, imageid, *ka,**kw):
        super().__init__(*ka,**kw)
        #super().__init__(error, *ka,**kw)
        self.imageid = imageid
    def response404(self):
        raise NotImplemented()

class ImageIdNotFound(ImageException):
    def __init__(self, imageid):
        super().__init__(imageid)
    #def __init__(self, imageid):
    #    self.imageid = imageid
    def response404(self):
        return error404_response_image_notfound(self.imageid)   #,self

# mess
class UnknownImageType(ImageException):
    #def __init__(self, info, excep=None):
        #self.info = info
        #if excep is not None:
        #    self.excep = excep
    def __init__(self, imageid, comment=None):
        super().__init__(imageid)
        #self.imageid = imageid
        self.comment = comment

    def response404(self, comment=None):
        if comment is None:
            #return error404_response_image_notfound(self.info, self.excep if self.excep is not None else self)
            return error404_response_image_notfound(self.imageid)
        else:
            #return uierr.response404(comment="MIME type information could not be found from the orignal image file.")
            #return make_response_jsonified({'error': repr(self.info), 'comment':"MIME type information could not be found from the orignal image file."}, 404)
            # FIXME: call error404_xxxx....
            return make_response_jsonified({'error': repr(self.imageid), 'comment':self.comment}, 404)


class ImageAlreadyExists(ImageException):
    """ e.g. When trying to replace and existing image. """
    def __init__(self, imagename, hashcode):
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
    def response404(self):
         return make_response_jsonified({'error': "image has no mask/alpha channel.", "imageid": self.imageid}, 404)
