#!ifarms/bin/python
"""
Microservice for images (api):
storage, transformations, conversions.
"""
# Losely based on a previous toy project of mine: https://github.com/sosi-org/REST-practice

from flask import Flask

from flask import jsonify
from flask import abort
from flask import request


from flask import make_response  # for 404

import datetime
import json
import imageio


API_ENDPOINT_URL = "/progimage.com/api/v1.0"

app = Flask(__name__)


def welcome_note():
    eurl = API_ENDPOINT_URL + "/all-local"
    return \
        "Welcome to ProgImage.com API.<br/>"+ \
        "See https://github.com/sosi-org/image-farms/blob/master/README.md<br/>"+ \
        "For full list: try: <a href=\""+ eurl + "\"> "+eurl+"</a>."

def incorrect_usage_note():
    #FIXME: too small.
    return make_response("Incorrect usage.", 404)


@app.route('/')
def index():
    return usage_note()


@app.errorhandler(404)
def not_found404(error):
    return make_response(jsonify({'error': 'Not found..'}), 404)


# Not recommended in production. For test only
@app.route(API_ENDPOINT_URL+'/all-local', methods=['GET'])
def invoices_listall():
    long_long_list = ['img1.png', 'img2.jpg']
    return jsonify({'images': long_long_list})

# used for download only
EXTENTIONS = {'image/gif': 'gif', 'image/jpeg':'jpeg', 'image/png':'png'}

#used for converted images:
MIME_LOOKUP = {'gif':'image/gif', 'jpeg':'image/jpeg', 'png':'image/png'}


def fetchlocal_original_mimetype_fromcontent(fileid):
    # todo: use imageio.get_reader()
    # get_meta_data()

    #metadata_filename = "imagestore/"+fileid+"/"+"original.bin"
    filename = "imagestore/"+fileid+"/"+"original.bin"
    with imageio.get_reader(filename) as r:
        md = r.get_meta_data()
        print(md)
        """
        {'version': b'GIF87a', 'extension': (b'NETSCAPE2.0', 27), 'loop': 0, 'duration': 10}
        """
        if md['version'] == b'GIF87a':
            return MIME_LOOKUP['gif']
        #elif:
        #elif:
        #elif:
        else:
            raise UnknownImageType(imgid=repr(imgid), comment="ImageIO could not detect the original image type.")
        #return mimetype

# fetchlocal_mimetype
def fetchlocal_original_mimetype_fromjson(fileid, key='mimetype'):
    DEFAULT_MIMETYPE = "image/jpeg"
    #DEFAULT_EXTENTION = "jpeg"
    # todo: use imageio.get_reader()
    # get_meta_data()
    try:
        metadata_filename = "imagestore/"+fileid+"/"+"original.bin"
        meta_data_json = open(metadata_filename, "rt").read()
        meta_data = json.loads(meta_data_json)
        mimetype = meta_data[fieldname]
        return mimetype #, EXTENTIONS[mimetype]
    except:
        return DEFAULT_MIMETYPE #, EXTENTIONS[DEFAULT_MIMETYPE]


def fetchlocal_binary(fileid):
    filename = "imagestore/"+fileid+"/"+"original.bin"
    return open(filename, "rb").read()

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
            #return make_response(jsonify({'error': repr(self.info), 'comment':"MIME type information could not be found from the orignal image file."}), 404)
            return make_response(jsonify({'error': repr(self.imgid), 'comment':self.comment}), 404)


class ImageHasNoMask(Exception):
    def __init__(self, imageid):
        self.imageid = imageid
    def response404(self):
         return make_response(jsonify({'error': "image has no mask/alpha channel.", "imageid": self.imageid}), 404)


@app.route(API_ENDPOINT_URL+'/<int:imgid>/original', methods=['GET'])
def retrieve_original(imgid):
    # from flask import send_file
    if imgid == 0:
        print("Default image requested.")
        #def get_image(pid):
        #image_binary = read_image(pid)
        #bytes_read

        # image_id
        fileid = "sample0000"
    else:
        #abort(404)
        return error404_response_image_notfound(imgid)

    try:
        #original_mimetype = fetchlocal_original_mimetype_fromjson(fileid)
        original_mimetype = fetchlocal_original_mimetype_fromcontent(fileid)

        print("original mimetype:", original_mimetype)
        #extention = EXTENTIONS[original_mimetype]

        image_binary = fetchlocal_binary(fileid)
        response = make_response(image_binary)
        response.headers.set('Content-Type', original_mimetype)

        download = False
        if download:
            orig_filename = fetchlocal_metadata(fileid, key='orig-name')
            response.headers.set('Content-Disposition', 'attachment', filename=orig_filename)

        return response
    except UnknownImageType as uierr:
        return uierr.response404(imgid=imgid, comment="MIME type information could not be found from the orignal image file.")
        #make_response(jsonify({'error': repr(uierr), 'comment':"MIME type information could not be found from the orignal image file."}), 404)

    except Exception as err:
        # not really 404
        #abort(404)
        return make_response(jsonify({'error': repr(err)}), 404)


# download  : as_attachment=True


def error404_response_image_notfound(imageid, exception=None):
    # abort(404)
    if exception is not None:
        return make_response(jsonify({'error': "image not found", "imageid": imageid, 'exception': repr(exception)}), 404)
    return make_response(jsonify({'error': "image not found", "imageid": imageid}), 404)

#upload: imageio can directly fetch it



def extract_mask(fileid):
    try:
        print("===========================================")
        original_image_binary = fetchlocal_binary(fileid)
        im = imageio.imread(original_image_binary)

        image_format = 'png'
        converted_mimetype = MIME_LOOKUP[image_format]

        #local_filename
        local_cached_filename = "imagestore/"+fileid+"/mask."+image_format


        # remove alpha channel
        if im.shape[2] >3:
            mask = im[:,:,3]
        else:
            raise ImageHasNoMask(fileid)

        imageio.imwrite(local_cached_filename, mask)
        #todo: add metadata

        converted_binary = open(local_cached_filename, "rb").read()
        response = make_response(converted_binary)
        response.headers.set('Content-Type', converted_mimetype)
        return response

    except ImageHasNoMask as ihnm:
        return ihnm.response404() #make_response(jsonify({'error': "image not found", "imageid": imageid}), 404)

    except ImageNotFound as imexc:
        return imexc.response404() #error404_response_image_notfound(fileid, imexc)

    except Exception as err:
        #abort(404)
        #return make_response(jsonify({'error': repr(err)}), 404)
        # error	"OSError('JPEG does not support alpha channel.',)"
        return error404_response_image_notfound(fileid, err)


def convert_to_format_and_respond(fileid, image_format):
    """ Note: I dont cache here. It is up to the browser and server to cache it."""
    try:
        print("fetching binary. ", fileid, image_format)

        #original_mimetype = fetchlocal_original_mimetype_fromjson(fileid)

        #converted_mimetype = MIME_LOOKUP.get(image_format, "UNKNOWN1")
        #converted_mimetype = MIME_LOOKUP[image_format]
        converted_mimetype = MIME_LOOKUP.get(image_format, None)
        assert converted_mimetype is not None

        print("converted mimetype:", converted_mimetype)

        original_image_binary = fetchlocal_binary(fileid)

        print("imageIO")
        im = imageio.imread(original_image_binary)
        #print(im)
        print("image read:", im.shape)

        #if converted_mimetype != original_mimetype:

        if True:
            # do the conversion

            #local_filename
            local_cached_filename = "imagestore/"+fileid+"/"+fileid+"."+image_format
            #cached_name = ""+"."+image_format
            print("writing: local_cached_filename:", local_cached_filename)


            # remove alpha channel
            im = im[:,:,:3]
            imageio.imwrite(local_cached_filename, im)
            # assumption: exntention, type, and imageio's extention are the same
            print("imwrite()")
        else:
            pass

        converted_binary = open(local_cached_filename, "rb").read()
        print("read binary()")
        response = make_response(converted_binary)
        response.headers.set('Content-Type', converted_mimetype)

        return response

    except ImageNotFound as imexc:
        return error404_response_image_notfound(fileid, imexc)

    except Exception as err:
        #abort(404)
        #return make_response(jsonify({'error': repr(err)}), 404)
        # error	"OSError('JPEG does not support alpha channel.',)"
        return error404_response_image_notfound(fileid, err)


def file_id_from_imageid(imgid):
    if imgid == 0:
        fileid = "sample0000"
        return fileid
    else:
        #return error404_response_image_notfound(imgid)
        raise ImageNotFound(imgid)

@app.route(API_ENDPOINT_URL+'/<int:imgid>/jpeg', methods=['GET'])
def convert_jpeg(imgid):
    #pre_image_lookup
    #if imgid == 0:
    #    print("convertion requested.")
    #    fileid = "sample0000"
    #else:
    #    return error404_response_image_notfound(imgid)

    print("convertion requested.")
    fileid = file_id_from_imageid(imgid)

    image_format = 'jpeg'   # same as extention
    return convert_to_format_and_respond(fileid, image_format)

@app.route(API_ENDPOINT_URL+'/<int:imgid>/gif', methods=['GET'])
def convert_gif(imgid):
    #if imgid == 0:
    #    print("convertion requested.")
    #    fileid = "sample0000"
    #else:
    #    return error404_response_image_notfound(imgid)

    fileid = file_id_from_imageid(imgid)

    image_format = 'gif'   # same as extention
    return convert_to_format_and_respond(fileid, image_format)

@app.route(API_ENDPOINT_URL+'/<int:imgid>/png', methods=['GET'])
def convert_png(imgid):
    fileid = file_id_from_imageid(imgid)
    image_format = 'png'   # same as extention
    #print(fileid, image_format, "=-=-=-=-=")
    #print(fileid, image_format, "*********")
    return convert_to_format_and_respond(fileid, image_format)

@app.route(API_ENDPOINT_URL+'/<int:imgid>/mask', methods=['GET'])
def extract_mask_api(imgid):
    print("imgid",imgid)
    fileid = file_id_from_imageid(imgid)
    print("imgid",imgid)
    image_format = 'png'   # same as extention
    return extract_mask(fileid)
    #return convert_to_format_and_respond(fileid, image_format)


@app.route(API_ENDPOINT_URL+'/<int:imgid>', methods=['GET'])
def incorrect_usage1(imgid):
    return incorrect_usage_note()


if __name__ == '__main__':
    app.run(debug=True)
