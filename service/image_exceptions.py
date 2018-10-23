
class ImageNotFound(Exception):
    def __init__(self, imageid):
        self.imageid = imageid
    def response404(self):
        return error404_response_image_notfound(self.imageid, self)

# mess
class UnknownImageType(Exception):
    #def __init__(self, info, excep=None):
        #self.info = info
        #if excep is not None:
        #    self.excep = excep
    def __init__(self, imgid, comment=None):
        self.imgid = imgid
        self.comment = comment

    def response404(self, comment=None):
        if comment is None:
            #return error404_response_image_notfound(self.info, self.excep if self.excep is not None else self)
            return error404_response_image_notfound(self.imgid)
        else:
            #return uierr.response404(comment="MIME type information could not be found from the orignal image file.")
            #return make_response_jsonified({'error': repr(self.info), 'comment':"MIME type information could not be found from the orignal image file."}, 404)
            # FIXME: call error404_xxxx....
            return make_response_jsonified({'error': repr(self.imgid), 'comment':self.comment}, 404)


class ImageAlreadyExists(Exception):
    """ e.g. When trying to replace and existing image. """
    def __init__(self, imagename, hashcode):
        self.imagename = imagename
        self.hashcode = hashcode
    def response404(self):
        #respondize. stringify. jsonize. repr. 404repr. respond_repr
         return make_response_jsonified({'error': "image already exists.", "imagename": self.imagename, "hashcode": self.hashcode}, 404)



class ImageTooLarge(Exception):
    """  """
    def __init__(self, size_pair, volume_bytes):
        self.size_pair = size_pair
        self.volume_bytes = volume_bytes
    def response404(self):
        #respondize. stringify. jsonize. repr. 404repr. respond_repr
         return make_response_jsonified({
             'error': "image too large. maximum %d (bytes), %d x %d" % (service_config['max-size'], service_config['max-width'], service_config['max-width'] ),
             "size_pair": "%d x %d" % self.size_pair,
             "volume_bytes": self.volume_bytes
         }, 404)

class ImageHasNoMask(Exception):
    def __init__(self, imageid):
        self.imageid = imageid
    def response404(self):
         return make_response_jsonified({'error': "image has no mask/alpha channel.", "imageid": self.imageid}, 404)
