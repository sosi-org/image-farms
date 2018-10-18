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


@app.route('/')
def index():
    eurl = API_ENDPOINT_URL + "/all-local"
    return \
        "Welcome to ProgImage.com API.<br/>"+ \
        "See https://github.com/sosi-org/image-farms/blob/master/README.md<br/>"+ \
        "For full list: try: <a href=\""+ eurl + "\"> "+eurl+"</a>."


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found (Sosi)'}), 404)


# Not recommended in production. For test only
@app.route(API_ENDPOINT_URL+'/all-local', methods=['GET'])
def invoices_listall():
    long_long_list = ['img1.png', 'img2.jpg']
    return jsonify({'images': long_long_list})

# used for download only
EXTENTIONS = {'image/gif': 'gif', 'image/jpeg':'jpeg'}

#used for converted images:
MIME_LOOKUP = {'gif':'image/gif', 'jpeg':'image/jpeg'}


def fetchlocal_mimetype(fileid, key='mimetype'):
    DEFAULT_MIMETYPE = "image/jpeg"
    #DEFAULT_EXTENTION = "jpeg"
    try:
        metadata_filename = "imagestore/"+fileid+"/"+"original.gif"
        meta_data_json = open(metadata_filename, "rt").read()
        meta_data = json.loads(meta_data_json)
        mimetype = meta_data[fieldname]
        return mimetype #, EXTENTIONS[mimetype]
    except:
        return DEFAULT_MIMETYPE #, EXTENTIONS[DEFAULT_MIMETYPE]

def fetchlocal_binary(fileid):
    filename = "imagestore/"+fileid+"/"+"original.gif"
    return open(filename, "rb").read()


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

        try:
            mimetype = fetchlocal_mimetype(fileid)
            print("mimetype:", mimetype)
            #extention = EXTENTIONS[mimetype]

            image_binary = fetchlocal_binary(fileid)
            response = make_response(image_binary)
            response.headers.set('Content-Type', mimetype)

            download = False
            if download:
                orig_filename = fetchlocal_metadata(fileid, key='orig-name')
                response.headers.set('Content-Disposition', 'attachment', filename=orig_filename)

            return response
        except Exception as err:
            # not really 404
            #abort(404)
            return make_response(jsonify({'error': repr(err)}), 404)

    else:
        #abort(404)
        return error404_response_image_notfound(imageid)
# download  : as_attachment=True

class ImageNotFound(Exception):
    def __init__(self, imageid):
        self.imageid = imageid

def error404_response_image_notfound(imageid, exception=None):
    if exception is not None:
        return make_response(jsonify({'error': "image not found", "imageid": imageid, 'exception': repr(exception)}), 404)
    return make_response(jsonify({'error': "image not found", "imageid": imageid}), 404)

#upload: imageio can directly fetch it


@app.route(API_ENDPOINT_URL+'/<int:imgid>/jpeg', methods=['GET'])
def make_jpeg(imgid):
    if imgid == 0:
        print("Default image requested.")
        fileid = "sample0000"
        try:
            image_format = 'jpeg'   # same as extention
            #mimetype = MIME_LOOKUP[image_format]
            #print("mimetype:", mimetype)
            print("fetching binary")

            original_image_binary = fetchlocal_binary(fileid)

            print("imageIO")
            im = imageio.imread(original_image_binary)
            #print(im)
            print("image read:", im.shape)

            #local_filename
            local_cached_filename = "imagestore/"+fileid+"/"+fileid+"."+image_format
            #cached_name = ""+"."+image_format
            print("writing: local_cached_filename:", local_cached_filename)

            # remove alpha channel
            im = im[:,:,:3]
            imageio.imwrite(local_cached_filename, im)
            # assumption: exntention, type, and imageio's extention are the same
            print("imwrite()")

            converted_binary = open(local_cached_filename, "rb").read()
            print("read binary()")
            response = make_response(converted_binary)
            converted_mimetype = MIME_LOOKUP[image_format]
            print("converted mimetype:", converted_mimetype)
            response.headers.set('Content-Type', converted_mimetype)

            return response
        except Exception as err:
            #abort(404)
            #return make_response(jsonify({'error': repr(err)}), 404)
            # error	"OSError('JPEG does not support alpha channel.',)"
            return error404_response_image_notfound(imgid, err)
        except ImageNotFound as imexc:
            return error404_response_image_notfound(imgid, imexc)

    else:
        #abort(404)
        return error404_response_image_notfound(imgid)


if __name__ == '__main__':
    app.run(debug=True)
