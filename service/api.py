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


import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

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


JSON_MIME='application/json'

#from enum import Enum, unique

class CODES:
    OK_CREATED_201 = 201
    OK_FINE200 = 200
    ERROR_404 = 404

ERROR_404 = CODES.ERROR_404

# Enum not used. It is slow.
REST_POST = 'POST'
REST_DELETE ='DELETE'
REST_GET = 'GET'
REST_PUT = 'PUT'
REST_PATCH = 'PATCH'
REST_OPTIONS ='OPTIONS'
REST_HEAD = 'HEAD'


from custom_responses import *

# ************************************************************
# *  config

API_ENDPOINT_URL = "/progimage.com/api/v1.0"
CLIENT_ENDPOINT_URL = "/progimage.com/api/v1.0"

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

def incorrect_usage_note_response(hint_moreinfo, suggested_urls=[]):
    #FIXME: too small.
    r = {'error':"Incorrect usage."}
    r['comment'] = hint_moreinfo
    if len(suggested_urls) > 0:
        # todo: make <a href>
        r['suggestions-try'] = suggested_urls
    return make_response_jsonified(r, ERROR_404)


@app.route('/')
def index():
    return incorrect_usage_note_response("\"api/\" has nothing to do.", suggested_urls=[CLIENT_ENDPOINT_URL+ "/all-local", CLIENT_ENDPOINT_URL+ "/0/original/"])






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



@app.route(API_ENDPOINT_URL+'/<int:imageid_int>/original', methods=['GET'])
def retrieve_original(imageid_int):
    # from flask import send_file
    try:
        folderhash = folderhash_from_imageid(imageid_int)
        del imageid_int
        #folderhash = str(imageid_int)
        #folderhash = folderhash_from_imageid(imageid_int)
        (image_binary, original_mimetype, original_name) = \
            images_service.retrieve_original(folderhash)

        response = make_response_plain(image_binary)
        response.headers.set('Content-Type', original_mimetype)

        download = False
        if download:
            response.headers.set('Content-Disposition', 'attachment', filename=orig_filename)

        return response

    except ImageIdNotFound as err:
            #abort(ERROR_404)
            return error404_response_image_notfound(err.imageid)
    except UnknownFileFormat as uierr:
        return uierr.response404(imgageid=imageid_int, comment="MIME type information could not be found from the orignal image file.")
        #make_response_jsonified({'error': repr(uierr), 'comment':"MIME type information could not be found from the orignal image file."}, ERROR_404)

    """
    except Exception as err:
        # not really 404
        #abort(ERROR_404)
        return make_response_jsonified({'error': repr(err)}, ERROR_404)
    """

# download  : as_attachment=True



#upload: imageio can directly fetch it


def folderhash_from_imageid(imageid_int):
    # assert int
    assert (imageid_int+2)/2 == (imageid_int)/2+1, repr(imageid_int)

    if imageid_int == 0:
        folderhash = "sample0000"
        return folderhash
    return str(imageid_int)


def extract_mask(folderhash):
    try:
        converted_binary, converted_mimetype = images_service.extract_mask(folderhash)
        response = make_response_plain(converted_binary)
        response.headers.set('Content-Type', converted_mimetype)
        return response

    except ImageHasNoMask as ihnm:
        return ihnm.response404() #make_response_jsonified({'error': "image not found", "imageid": imageid}, ERROR_404)

    except ImageIdNotFound as imexc:
        return imexc.response404() #error404_response_image_notfound(folderhash, imexc)

    except ImageException as imexc:
        return imexc.response404()  # unsure

    """
    #FIXME: Direct usae of 'Exception' is discouraged
    except Exception as err:
        #abort(ERROR_404)
        #return make_response_jsonified({'error': repr(err)}, ERROR_404)
        # error	"OSError('JPEG does not support alpha channel.',)"
        return error404_response_image_notfound(folderhash, err)
    """


def convert_to_format_and_respond(imageid_int, image_format):
    #folderhash = str(imageid_int)
    folderhash = folderhash_from_imageid(imageid_int)
    del imageid_int
    assert type(folderhash) is str
    try:
        log_warn(image_format+ ".  req:"+folderhash)
        converted_binary, converted_mimetype = images_service.convert_to_format_and_respond(folderhash, image_format)
        response = make_response_plain(converted_binary)
        response.headers.set('Content-Type', converted_mimetype)

        return response

    except ImageIdNotFound as ex:
        log_err(image_format+ ".  req:"+folderhash)
        return ex.response404()

    #except ImageIdNotFound as imexc:
    #    return error404_response_image_notfound(folderhash, imexc)
    #except Exception as err:
    #    return error404_response_image_notfound(folderhash, err)


@app.route(API_ENDPOINT_URL+'/<int:imageid_int>/jpeg', methods=['GET'])
def convert_jpeg(imageid_int):
    log("LJPEGG")
    #folderhash = folderhash_from_imageid(imageid_int)
    #del imageid_int

    return convert_to_format_and_respond(imageid_int, 'jpeg')
    """
    try:
        (binary, mimetype) =  images_service.convert_jpeg(imageid_int)
        response = make_response_plain(binary)
        response.headers.set('Content-Type', mimetype)
        return response
    except ImageIdNotFound as ex:
        return ex.response404()
    """

@app.route(API_ENDPOINT_URL+'/<int:imageid_int>/gif', methods=['GET'])
def convert_gif(imageid_int):
    #folderhash = folderhash_from_imageid(imageid_int)
    #del imageid_int
    return convert_to_format_and_respond(imageid_int, 'gif')
    """
    try:
        (binary, mimetype) = images_service.convert_gif(imageid_int)
        response = make_response_plain(binary)
        response.headers.set('Content-Type', mimetype)
        return response
    except ImageIdNotFound as ex:
        return ex.response404()
    """


@app.route(API_ENDPOINT_URL+'/<int:imageid_int>/png', methods=['GET'])
def convert_png(imageid_int):
    #folderhash = folderhash_from_imageid(imageid_int)
    #del imageid_int
    return convert_to_format_and_respond(imageid_int, 'png')
    """
    try:
        (binary, mimetype) = images_service.convert_png(imageid_int)
        response = make_response_plain(binary)
        response.headers.set('Content-Type', mimetype)
        return response
    except ImageIdNotFound as ex:
        return ex.response404()
    """

@app.route(API_ENDPOINT_URL+'/<int:imageid_int>/mask', methods=['GET'])
def extract_mask_api(imageid_int):
    try:
        folderhash = folderhash_from_imageid(imageid_int)
        del imageid_int
        (binary, mimetype) =  images_service.extract_mask_api(folderhash)
        response = make_response_plain(binary)
        response.headers.set('Content-Type', mimetype)
        return response
    except ImageIdNotFound as ex:
        return ex.response404()


def check_security(original_filename):
    # checks if a filename is secure (not very long, etc)
    return True

#from logging import *
#from my_logger import *
from logger import *

#def wrap_in_excp_cathcers():
#    pass


@app.route(API_ENDPOINT_URL+'/upload', methods=['PUT', 'GET', 'DELETE', 'PATH', 'OPTIONS'])
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
        }, CODES.OK_CREATED_201)
        response.headers.set('Content-Type', JSON_MIME)
        return response

    except Respond404ableException as ex:
        log_err("during upload: " + repr(ex))
        #return err.response404(imageid=imageid_int, comment="MIME type information could not be found from the orignal image file.")
        return make_response_jsonified({'error': "Use DELETE and then POST, instead."}, ERROR_404)

    """
    except Exception as err:
        log_err("free exception" + repr(err) + "blah")
        return make_response_jsonified({'error': err, 'exception': err}, ERROR_404)
    """


#@app.route(API_ENDPOINT_URL+'/<int:imageid_int>/', methods=['GET'])
@app.route(API_ENDPOINT_URL+'/<int:imageid_int>', methods=['GET', 'POST', 'PUT'])
def incorrect_usage1(imageid_int):
    """ No such api opetaion. """ #no_operation_on_main
    return incorrect_usage_note_response("Use api/<imageid>/original or gif or jpeg or ...")

@app.route(API_ENDPOINT_URL+'/<int:imageid_int>', methods=['PUT'])
def incorrect_replace_image(imageid_int):
    """ No such api operation. """
    return incorrect_usage_note_response("Modification of an uploaded image is not supported in this version.")

# how to check incomplete uploaded images?

@app.route(API_ENDPOINT_URL+'/<int:imageid_int>', methods=['DELETE'])
def destroy_iamge(imageid_int):
    """ DELETE: Removes all current representations of the target resource given by a URL """
    folderhash = folderhash_from_imageid(imageid_int)
    del imageid_int
    ownership_proof = "DELETE s arguments"
    images_service.kill_image(folderhash, ownership_proof)
    """
    if success == 1:
        pass
    else:
        raise "Something went wrong"
    """

"""
@app.route(API_ENDPOINT_URL+'/favicon.ico', methods=['GET'])
def favicon():
    return;
"""

if __name__ == '__main__':

    deployment_self_tests()

    app.run(debug=True)
