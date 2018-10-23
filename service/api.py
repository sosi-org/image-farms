#!ifarms/bin/python
"""
Microservice for images (api):
storage, transformations, conversions.
"""
# Losely based on a previous toy project of mine: https://github.com/sosi-org/REST-practice

# ************************************************************
# dependencies

from flask import Flask

from flask import jsonify
#from flask import abort
from flask import request


#import datetime
#import json

import bson  # binary json. Used for uploading binary files.

#from images_service import ImagesService
import images_service

from image_exceptions import *

"""
Dont use:
import imageio
import os

"""
#FIXME  remove this:
import os


JSON_MIME='application/json'

class CODES:
    OK_CREATED = 201
    OK_FINE = 200
    ERROR_404 = 404
ERROR_404 = CODES.ERROR_404



from custom_responses import *

# ************************************************************
# *  config

API_ENDPOINT_URL = "/progimage.com/api/v1.0"


# self tests
def deployment_self_tests():
    images_service.service_deployment_test()


# ************************************************************

app = Flask(__name__)


def welcome_note():
    eurl = API_ENDPOINT_URL + "/all-local"
    return \
        "Welcome to ProgImage.com API.<br/>"+ \
        "See https://github.com/sosi-org/image-farms/blob/master/README.md<br/>"+ \
        "For full list: try: <a href=\""+ eurl + "\"> "+eurl+"</a>."

def incorrect_usage_note():
    #FIXME: too small.
    return make_response_jsonified({'error':"Incorrect usage."}, ERROR_404)


@app.route('/')
def index():
    return usage_note()


@app.errorhandler(ERROR_404)
def not_found404(error):
    return make_response_jsonified({'error': 'Not found..'}, ERROR_404)


# Not recommended in production. For test only
@app.route(API_ENDPOINT_URL+'/all-local', methods=['GET'])
def invoices_listall():
    return jsonify(images_service.invoices_listall())




"""
Test: metadata of nonexistant image
Test: metadata generation called only after (uploaded) file saved

"""







# to implement:
#  upload
#  check (infer?) real format  --> elready done!  For texting correct conversion.
# Check equality of two image files. (Or SERVED images)

# deploy:
#   deploy on docker on an s3 volume
# always define an upper bound (For eveything)  (image size, etc)

@app.route(API_ENDPOINT_URL+'/<int:imgid>/original', methods=['GET'])
def retrieve_original(imgid):
    # from flask import send_file
    try:
        (image_binary, original_mimetype, original_name) = \
            images_service.retrieve_original(imgid)

        response = make_response_plain(image_binary)
        response.headers.set('Content-Type', original_mimetype)

        download = False
        if download:
            response.headers.set('Content-Disposition', 'attachment', filename=orig_filename)

        return response

    except ImageIdNotFound as err:
            #abort(ERROR_404)
            return error404_response_image_notfound(err.imageid)
    except UnknownImageType as uierr:
        return uierr.response404(imgageid=imgid, comment="MIME type information could not be found from the orignal image file.")
        #make_response_jsonified({'error': repr(uierr), 'comment':"MIME type information could not be found from the orignal image file."}, ERROR_404)

    """
    except Exception as err:
        # not really 404
        #abort(ERROR_404)
        return make_response_jsonified({'error': repr(err)}, ERROR_404)
    """

# download  : as_attachment=True



#upload: imageio can directly fetch it


def extract_mask(fileid):
    try:
        converted_binary, converted_mimetype = images_service.extract_mask(fileid)
        response = make_response_plain(converted_binary)
        response.headers.set('Content-Type', converted_mimetype)
        return response

    except ImageHasNoMask as ihnm:
        return ihnm.response404() #make_response_jsonified({'error': "image not found", "imageid": imageid}, ERROR_404)

    except ImageIdNotFound as imexc:
        return imexc.response404() #error404_response_image_notfound(fileid, imexc)

    except ImageException as imexc:
        return imexc.response404()  # unsure

    except Exception as err:
        #abort(ERROR_404)
        #return make_response_jsonified({'error': repr(err)}, ERROR_404)
        # error	"OSError('JPEG does not support alpha channel.',)"
        return error404_response_image_notfound(fileid, err)


def convert_to_format_and_respond(fileid, image_format):
    try:
        converted_binary, converted_mimetype = images_service.convert_to_format_and_respond(fileid, image_format)
        response = make_response_plain(converted_binary)
        response.headers.set('Content-Type', converted_mimetype)

        return response

    except ImageIdNotFound as imexc:
        return error404_response_image_notfound(fileid, imexc)

    except Exception as err:
        return error404_response_image_notfound(fileid, err)


@app.route(API_ENDPOINT_URL+'/<int:imgid>/jpeg', methods=['GET'])
def convert_jpeg(imgid):
    (binary, mimetype) =  images_service.convert_jpeg(imgid)
    response = make_response_plain(binary)
    response.headers.set('Content-Type', mimetype)
    return response

@app.route(API_ENDPOINT_URL+'/<int:imgid>/gif', methods=['GET'])
def convert_gif(imgid):
    (binary, mimetype) = images_service.convert_gif(imgid)
    response = make_response_plain(binary)
    response.headers.set('Content-Type', mimetype)
    return response

@app.route(API_ENDPOINT_URL+'/<int:imgid>/png', methods=['GET'])
def convert_png(imgid):
    (binary, mimetype) = images_service.convert_png(imgid)
    response = make_response_plain(binary)
    response.headers.set('Content-Type', mimetype)
    return response

@app.route(API_ENDPOINT_URL+'/<int:imgid>/mask', methods=['GET'])
def extract_mask_api(imgid):
    (binary, mimetype) =  images_service.extract_mask_api(imgid)
    response = make_response_plain(binary)
    response.headers.set('Content-Type', mimetype)
    return response


def check_security(original_filename):
    # checks if a filename is secure (not very long, etc)
    return True

#from logging import *
from logger import *

#def wrap_in_excp_cathcers():
#    pass

@app.route(API_ENDPOINT_URL+'/upload', methods=['PUT', 'GET', 'DELETE'])
def put_file():
    log_err("no PUT")
    #err = NotImplemented("PUT", moreinfo="Use DELETE and then POST, instead.)
    return make_response_jsonified({'error': "Use DELETE and then POST, instead."}, ERROR_404)


#from flask import Flask, flash, request, redirect, url_for


@app.route(API_ENDPOINT_URL+'/upload', methods=['POST'])
def upload_file():
    # log_err("during upload: ", repr("ex"))

    log("UPLOADing using POST:")
    try:
        #after using BSON in client:  request.data: b'\x07\x02\x00\x00\x05binary_content\x00\xc3\x01\x00\x00\x00\xff\xd8\xff\xe0\x00\x10JFIF...'
        body = bson.loads(request.data)  # is binary
        binary_content = body['binary_content']
        filename = body['filename']
        meta_data, folderhash = images_service.do_actual_upload(filename, binary_content)

        #content metadata (almost like a cache of one aspect of the contents: image format, and maybe width, height)
        response = make_response_jsonified({
            'metadata': meta_data,
            'image-id': folderhash,
        }, CODES.OK_CREATED)
        response.headers.set('Content-Type', JSON_MIME)
        return response

    except Respond404ableException as ex:
        log_err("during upload: " + repr(ex))
        #return err.response404(imageid=imgid, comment="MIME type information could not be found from the orignal image file.")
        return make_response_jsonified({'error': "Use DELETE and then POST, instead."}, ERROR_404)

    """
    except Exception as err:
        log_err("free exception" + repr(err) + "blah")
        return make_response_jsonified({'error': err, 'exception': err}, ERROR_404)
    """


@app.route(API_ENDPOINT_URL+'/<int:imgid>', methods=['GET'])
def incorrect_usage1(imgid):
    return incorrect_usage_note()


"""
@app.route(API_ENDPOINT_URL+'/favicon.ico', methods=['GET'])
def favicon():
    return;
"""

if __name__ == '__main__':

    deployment_self_tests()

    app.run(debug=True)
