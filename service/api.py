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


import datetime
import json
import imageio
import bson  # binary json. Used for uploading binary files.
import os


from image_exceptions import *

JSON_MIME='application/json'

class CODES:
    OK_CREATED = 201
    OK_FINE = 200
    ERROR_404 = 404
ERROR_404 = CODES.ERROR_404

KILO = 1024
MEGA = KILO*KILO
GIGA = MEGA*KILO


from custom_responses import *

# ************************************************************
# *  config

API_ENDPOINT_URL = "/progimage.com/api/v1.0"

# direct access discouraged:
IMAGE_BASE = '../imagestore/'

# self tests
def deployment_self_tests():
    # Makes sure we are running from the correct folder
    assert os.path.exists(IMAGE_BASE)

# code-time constant
service_config = {
    'max-size': MEGA,
    'max-width': 10000,
}

# load-time (after deploy-time) constant
service_config_state = {
    'partition-id': 1,
}

# implementation consts

# used for download only
EXTENTIONS = {'image/gif': 'gif', 'image/jpeg':'jpeg', 'image/png':'png'}

#used for converted images:
MIME_LOOKUP = {'gif':'image/gif', 'jpeg':'image/jpeg', 'png':'image/png'}


#DEFAULT_IMAGE_NAME
ORIGINAL_BIN_FILENAME = "original.bin"

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
    long_long_list = ['img1.png', 'img2.jpg']
    return jsonify({'images': long_long_list})



def fetchlocal_original_mimetype_fromcontent(fileid):
    # todo: use imageio.get_reader()
    # get_meta_data()

    #metadata_filename = "IMAGE_BASE + fileid+"/"+"original.bin"
    filename = IMAGE_BASE + fileid+"/"+ORIGINAL_BIN_FILENAME
    with imageio.get_reader(filename) as r:
        md = r.get_meta_data()
        #md = get_metadata_locally(fileid)
        print(md)
        """
        GIF:
        {'version': b'GIF87a', 'extension': (b'NETSCAPE2.0', 27), 'loop': 0, 'duration': 10}
        """
        if 'version' in md and md['version'] == b'GIF87a':
            log("GIF")
            return MIME_LOOKUP['gif']
        elif 'jfif_version' in md or 'jfif' in md:
            """
            JPEG:
                {'jfif_version': (1, 1), 'dpi': (72, 72), 'jfif': 257, 'jfif_unit': 1, 'jfif_density': (72, 72)}
            """
            log("JPEG")
            return MIME_LOOKUP['jpeg']
        else:
            log_err("unknown type")
            raise UnknownImageType(imgid=repr(imgid), comment="ImageIO could not detect the original image type.")
        #return mimetype
    #throw image does not exist

"""
Test: metadata of nonexistant image
Test: metadata generation called only after (uploaded) file saved

"""

def metadata_filename_from_folderhash(folderhash):
    return IMAGE_BASE + folderhash+"/"+"metadata.json"

def get_metadata_locally(folderhash):
    # fetchlocal_metadata()
    metadata_filename = metadata_filename_from_folderhash(folderhash)
    meta_data_json = open(metadata_filename, "rt").read()
    metadata = json.loads(meta_data_json)
    return metadata


def generate_metadata(fileid, original_name):
    """ from stored file.  original_name: uploaded name """
    metadata_filename = metadata_filename_from_folderhash(fileid)
    mimetype = fetchlocal_original_mimetype_fromcontent(fileid)

    metadata = {'orig-name':original_name, 'mimetype': mimetype}
    #with file(metadata_filename, "wt") as f:
    #    f.save(json.dumps(metadata))
    #    f.close()
    if os.path.exists(metadata_filename):
        log_warn("metadata file exists", metadata_filename)

    log(repr(metadata))

    with open(metadata_filename, "wt") as file:
        file.write(
            json.dumps(metadata)
        )
    #metadata = get_metadata_locally(fileid)
    return

# fetchlocal_mimetype
def fetchlocal_original_mimetype_fromjson(fileid, key='mimetype'):
    DEFAULT_MIMETYPE = "image/jpeg"
    #DEFAULT_EXTENTION = "jpeg"
    # todo: use imageio.get_reader()
    # get_meta_data()
    try:
        metadata = get_metadata_locally(fileid)
        fieldname = key
        mimetype = metadata[fieldname]
        return mimetype #, EXTENTIONS[mimetype]
    except:
        return DEFAULT_MIMETYPE #, EXTENTIONS[DEFAULT_MIMETYPE]


def fetchlocal_binary(fileid):
    filename = IMAGE_BASE + fileid+"/"+"original.bin"
    return open(filename, "rb").read()



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
    if imgid == 0:
        print("Default image requested.")
        #def get_image(pid):
        #image_binary = read_image(pid)
        #bytes_read

        # image_id
        fileid = "sample0000"
    else:
        #abort(ERROR_404)
        return error404_response_image_notfound(imgid)

    try:
        #original_mimetype = fetchlocal_original_mimetype_fromjson(fileid)
        original_mimetype = fetchlocal_original_mimetype_fromcontent(fileid)

        print("original mimetype:", original_mimetype)
        #extention = EXTENTIONS[original_mimetype]

        image_binary = fetchlocal_binary(fileid)
        response = make_response_plain(image_binary)
        response.headers.set('Content-Type', original_mimetype)

        download = False
        if download:
            orig_filename = fetchlocal_metadata(fileid, key='orig-name')
            response.headers.set('Content-Disposition', 'attachment', filename=orig_filename)

        return response
    except UnknownImageType as uierr:
        return uierr.response404(imgid=imgid, comment="MIME type information could not be found from the orignal image file.")
        #make_response_jsonified({'error': repr(uierr), 'comment':"MIME type information could not be found from the orignal image file."}, ERROR_404)

    except Exception as err:
        # not really 404
        #abort(ERROR_404)
        return make_response_jsonified({'error': repr(err)}, ERROR_404)


# download  : as_attachment=True



#upload: imageio can directly fetch it


def extract_mask(fileid):
    try:
        print("===========================================")
        original_image_binary = fetchlocal_binary(fileid)
        im = imageio.imread(original_image_binary)

        image_format = 'png'
        converted_mimetype = MIME_LOOKUP[image_format]

        #local_filename
        local_cached_filename = IMAGE_BASE + fileid+"/mask."+image_format


        # remove alpha channel
        if im.shape[2] >3:
            mask = im[:,:,3]
        else:
            raise ImageHasNoMask(fileid)

        imageio.imwrite(local_cached_filename, mask)
        #todo: add metadata

        converted_binary = open(local_cached_filename, "rb").read()
        response = make_response_plain(converted_binary)
        response.headers.set('Content-Type', converted_mimetype)
        return response

    except ImageHasNoMask as ihnm:
        return ihnm.response404() #make_response_jsonified({'error': "image not found", "imageid": imageid}, ERROR_404)

    except ImageNotFound as imexc:
        return imexc.response404() #error404_response_image_notfound(fileid, imexc)

    except Exception as err:
        #abort(ERROR_404)
        #return make_response_jsonified({'error': repr(err)}, ERROR_404)
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
            local_cached_filename = IMAGE_BASE + fileid+"/"+fileid+"."+image_format
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
        response = make_response_plain(converted_binary)
        response.headers.set('Content-Type', converted_mimetype)

        return response

    except ImageNotFound as imexc:
        return error404_response_image_notfound(fileid, imexc)

    except Exception as err:
        return error404_response_image_notfound(fileid, err)

"""
file_id:  an <int>
imageid:  foldername
"""

def file_id_from_imageid(imgid):
    # assert int
    assert (imgid+2)/2 == (imgid)/2+1, repr(imgid)

    if imgid == 0:
        fileid = "sample0000"
        return fileid
    #elif imgid == 12:
    #    file_id = "00012"
    #    return file_id

    #else:
    #    #return error404_response_image_notfound(imgid)
    #    raise ImageNotFound(imgid)
    return str(imgid)

def foldername_from_folderhash(folderhash):
    local_foldername = IMAGE_BASE + folderhash
    return local_foldername

@app.route(API_ENDPOINT_URL+'/<int:imgid>/jpeg', methods=['GET'])
def convert_jpeg(imgid):

    print("convertion requested.")
    fileid = file_id_from_imageid(imgid)

    image_format = 'jpeg'   # same as extention
    return convert_to_format_and_respond(fileid, image_format)

@app.route(API_ENDPOINT_URL+'/<int:imgid>/gif', methods=['GET'])
def convert_gif(imgid):
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

from werkzeug.utils import secure_filename

def check_security(original_filename):
    # checks if a filename is secure (not very long, etc)
    return True

# logging
def log(message):
    print("api server:", message)

def log_warn(message):
    print("api server WARNING:", message)

def log_err(message):
    print("api server ERROR:", message)


#def wrap_in_excp_cathcers():
#    pass

@app.route(API_ENDPOINT_URL+'/upload', methods=['PUT', 'GET', 'DELETE'])
def put_file():
    log("ERROR")
    #err = NotImplemented("PUT", moreinfo="Use DELETE and then POST, instead.)
    return make_response_jsonified({'error': "Use DELETE and then POST, instead."}, ERROR_404)


#from flask import Flask, flash, request, redirect, url_for
import hashlib
import struct

def do_actual_upload(original_clientside_filename, file_content_binary):

    print(type(file_content_binary))  # <class bytes>
    #os.path.join(app.config['UPLOAD_FOLDER'], filename)
    #image_id = [(fname, hashlib.sha256(file_as_bytes(open(fname, 'rb'))).digest()) for fname in fnamelst]
    #???????? file_content = file  # file_as_bytes(open(fname, 'rb'))
    file_content = file_content_binary
    image_sha256 = hashlib.sha256(file_content).digest()
    # b' .. ' -> sha256 -> hash object -> digest -> binary b'...'
    print(image_sha256)
    #image_id = image_sha256[:8]

    s_compiled = struct.Struct('<L')  # 4 bytes    #L 	unsigned long 	integer 	4
    hash_int_val = s_compiled.unpack_from(image_sha256)[0]  # 4 bytes
    #return {'hash val':hash_int_val}, "foldername"

    image_id = hash_int_val
    print("image_id image_id image_id:::",image_id)

    def manual_cleanup(folderhash, filename):
        #def manual_cleanup(local_filename, local_foldername):
        local_foldername = foldername_from_folderhash(folderhash)
        local_filename = local_foldername+'/'+filename
        metadata_filename = metadata_filename_from_folderhash(folderhash)

        # unsafe
        if os.path.exists(local_filename):
            os.remove(local_filename)
        if os.path.exists(metadata_filename):
            os.remove(metadata_filename)


        if os.path.exists(local_foldername):
            os.rmdir(local_foldername)


    # file_id is in fact folder_id
    #local_filename
    folderhash = file_id_from_imageid(image_id)  # i.e. imagehash
    local_foldername = foldername_from_folderhash(folderhash)
    local_filename = local_foldername+'/'+ORIGINAL_BIN_FILENAME
    manual_cleanup(folderhash, ORIGINAL_BIN_FILENAME)

    # clean
    assert not os.path.exists(local_foldername) #not os.path.isdir(local_foldername)
    os.makedirs(local_foldername, exist_ok=True)
    # has to be empty
    assert not os.path.exists(local_filename)

    with open(local_filename, "wb") as fl:
        #fl.save('./'+local_foldername+'/'+ORIGINAL_BIN_FILENAME)  #really? a 'file' object?
        fl.write(file_content_binary)
        log("WRITE successful: "+ local_filename)
    log("file closed.", )

    # no need for this! it is completely secure! We use a fixed name (ORIGINAL_BIN_FILENAME) to store the file.
    original_clientside_filename_secured = secure_filename(original_clientside_filename)
    del original_clientside_filename

    generate_metadata(folderhash, original_clientside_filename_secured)
    metadata = get_metadata_locally(folderhash)
    # actual_filename ='original.bin' is NOT metadata['orig-name']
    return metadata, local_foldername


# insomnia
@app.route(API_ENDPOINT_URL+'/upload', methods=['POST'])
def upload_file():
    log("UPLOAD using POST:")
    binary_data = request.data
    #after using BSON in client:  request.data: b'\x07\x02\x00\x00\x05binary_content\x00\xc3\x01\x00\x00\x00\xff\xd8\xff\xe0\x00\x10JFIF...'
    body = bson.loads(request.data)
    binary_content = body['binary_content']
    filename = body['filename']
    meta_data, folder_name = do_actual_upload(filename, binary_content)

    #content metadata (almost like a cache of one aspect of the contents: image format, and maybe width, height)
    response = make_response_jsonified({
        'metadata': meta_data,
    }, CODES.OK_CREATED)
    response.headers.set('Content-Type', JSON_MIME)
    return response


@app.route(API_ENDPOINT_URL+'/<int:imgid>', methods=['GET'])
def incorrect_usage1(imgid):
    return incorrect_usage_note()


if __name__ == '__main__':

    deployment_self_tests()

    app.run(debug=True)
