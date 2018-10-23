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
from flask import abort
from flask import request



import datetime
import json
import imageio

from image_exceptions import *

JSON_MIME='application/json'

class CODES:
    OK_CREATED = 201
    OK_FINE = 200
    ERROR_404 = 404

KILO = 1024
MEGA = KILO*KILO
GIGA = MEGA*KILO

#never call make_response. Always jsonify
from flask import make_response  # for 404

make_response_plain = make_response
make_response = "Uncallable! Never call make_response. Always jsonify."
def make_response_jsonified(content_dict, rest_code):
    if rest_code == 404:
        assert 'error' in content_dict
    return make_response_plain(jsonify(content_dict), rest_code)

# ************************************************************
# *  config

API_ENDPOINT_URL = "/progimage.com/api/v1.0"



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
    return make_response_jsonified({'error':"Incorrect usage."}, 404)


@app.route('/')
def index():
    return usage_note()


@app.errorhandler(404)
def not_found404(error):
    return make_response_jsonified({'error': 'Not found..'}, 404)


# Not recommended in production. For test only
@app.route(API_ENDPOINT_URL+'/all-local', methods=['GET'])
def invoices_listall():
    long_long_list = ['img1.png', 'img2.jpg']
    return jsonify({'images': long_long_list})




def fetchlocal_original_mimetype_fromcontent(fileid):
    # todo: use imageio.get_reader()
    # get_meta_data()

    #metadata_filename = "imagestore/"+fileid+"/"+"original.bin"
    filename = "imagestore/"+fileid+"/"+"original.bin"
    with imageio.get_reader(filename) as r:
        md = r.get_meta_data()
        #md = get_metadata(fileid)
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
    #throw image does not exist

"""
Test: metadata of nonexistant image
Test: metadata generation called only after (uploaded) file saved

"""

def metadata_filename_from_fileid(fileid):
    return "imagestore/"+fileid+"/"+"metadata.json"

def get_metadata(fileid):
    # fetchlocal_metadata()
    metadata_filename = metadata_filename_from_fileid(fileid)
    meta_data_json = open(metadata_filename, "rt").read()
    metadata = json.loads(meta_data_json)
    return metadata


def generate_metadata(fileid, original_name):
    """ from stored file.  original_name: uploaded name """
    metadata_filename = metadata_filename_from_fileid(fileid)
    mimetype = fetchlocal_original_mimetype_fromcontent(fileid)

    metadata = {'orig-name':original_name, 'mimetype': mimetype}
    #with file(metadata_filename, "wt") as f:
    #    f.save(json.dumps(metadata))
    #    f.close()
    with open(metadata_filename, "wb") as file:
        file.write(
            json.dumps(metadata)
        )


    #metadata = get_metadata(fileid)

# fetchlocal_mimetype
def fetchlocal_original_mimetype_fromjson(fileid, key='mimetype'):
    DEFAULT_MIMETYPE = "image/jpeg"
    #DEFAULT_EXTENTION = "jpeg"
    # todo: use imageio.get_reader()
    # get_meta_data()
    try:
        metadata = get_metadata(fileid)
        fieldname = key
        mimetype = metadata[fieldname]
        return mimetype #, EXTENTIONS[mimetype]
    except:
        return DEFAULT_MIMETYPE #, EXTENTIONS[DEFAULT_MIMETYPE]


def fetchlocal_binary(fileid):
    filename = "imagestore/"+fileid+"/"+"original.bin"
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
        #abort(404)
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
        #make_response_jsonified({'error': repr(uierr), 'comment':"MIME type information could not be found from the orignal image file."}, 404)

    except Exception as err:
        # not really 404
        #abort(404)
        return make_response_jsonified({'error': repr(err)}, 404)


# download  : as_attachment=True


def error404_response_image_notfound(imageid, exception=None):
    # abort(404)
    if exception is not None:
        return make_response_jsonified({'error': "image not found", "imageid": imageid, 'exception': repr(exception)}, 404)
    return make_response_jsonified({'error': "image not found", "imageid": imageid}, 404)

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
        response = make_response_plain(converted_binary)
        response.headers.set('Content-Type', converted_mimetype)
        return response

    except ImageHasNoMask as ihnm:
        return ihnm.response404() #make_response_jsonified({'error': "image not found", "imageid": imageid}, 404)

    except ImageNotFound as imexc:
        return imexc.response404() #error404_response_image_notfound(fileid, imexc)

    except Exception as err:
        #abort(404)
        #return make_response_jsonified({'error': repr(err)}, 404)
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
        response = make_response_plain(converted_binary)
        response.headers.set('Content-Type', converted_mimetype)

        return response

    except ImageNotFound as imexc:
        return error404_response_image_notfound(fileid, imexc)

    except Exception as err:
        #abort(404)
        #return make_response_jsonified({'error': repr(err)}, 404)
        # error	"OSError('JPEG does not support alpha channel.',)"
        return error404_response_image_notfound(fileid, err)

"""
file_id:  an <int>
imageid:  foldername
"""

def file_id_from_imageid(imgid):
    if imgid == 0:
        fileid = "sample0000"
        return fileid
    elif imgid == 12:
        file_id = "00012"
        return file_id
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

from werkzeug.utils import secure_filename

def check_security(original_filename):
    # checks if a filename is secure (not very long, etc)
    return True

def log(message):
    print("API server:", message)

#def wrap_in_cathcers():
#    pass

@app.route(API_ENDPOINT_URL+'/upload', methods=['PUT', 'GET', 'DELETE'])
def put_file():
    log("ERROR")
    #err = NotImplemented("PUT", moreinfo="Use DELETE and then POST, instead.)
    #return err.response404()
    #abort(404)
    return make_response_jsonified({'error': "Use DELETE and then POST, instead."}, 404)


#from flask import Flask, flash, request, redirect, url_for
import hashlib

# insomnia
@app.route(API_ENDPOINT_URL+'/upload', methods=['POST'])
def upload_file():
    log("UPLOAD using POST")
    log("====================================")

    print("req:::::::::::::", request)
    print(dir(request))
    print(request.files)
    #print(dir(request.files))

    #import ipdb
    #ipdb.set_trace(context=5)

    #print(dir(request.lists))

    # check if the post request has the file part
    if 'file' not in request.files:

        #flash('No file part')
        #return redirect(request.url)
        return make_response_jsonified({'error': "NO 'file' section in request."}, 404)
    print("FILE:::::::::::::1", file)

    file = request.files['file']
    # if user does not select file, browser also
    # submit an empty part without filename
    print("FILE:::::::::::::2")

    if file.filename == '':
        #flash('No selected file')
        #return redirect(request.url)
        return make_response_jsonified({'error':"no filename"}, 404)

    print("FILE:::::::::::::3")

    if not file:
        return make_response_jsonified({'error':"no file"}, 404)

    print("FILE:::::::::::::4")

    if not allowed_file(file.filename):
        #return
        return make_response_jsonified({'error': "bad filename"}, 404)

    print("FILE:::::::::::::5")

    filename = secure_filename(file.filename)
    #os.path.join(app.config['UPLOAD_FOLDER'], filename)
    #image_id = [(fname, hashlib.sha256(file_as_bytes(open(fname, 'rb'))).digest()) for fname in fnamelst]
    #???????? file_content = file  # file_as_bytes(open(fname, 'rb'))
    file_content = file.binary_content
    image_sha256 = hashlib.sha256(file_content).digest()
    image_id = image_sha256[:8]
    print(image_id)
    filename = file_id_from_imageid(image_id)
    #filename = file_id_from_sha256(image_sha256)
    file.save(filename)  #really? a 'file' object?
    #return redirect(url_for('uploaded_file',
    #                        filename=filename))
    #return "API UPLOADED"  # FIXME

    def generate_metadata(file_content):
        # see get_metadata(fileid)
        pass

    #content metadata (almost like a cache of one aspect of the contents: image format, and maybe width, height)
    response = make_response_jsonified({
        'metadata': meta_data,
    }, CODES.OK_CREATED)
    #{'ContentType': JSON_MIME}
    response.headers.set('Content-Type', JSON_MIME)


    # http://flask.pocoo.org/docs/1.0/patterns/fileuploads/
    # maximum number
    # global counter
    #https://pythonhosted.org/Flask-Uploads/
    pass


@app.route(API_ENDPOINT_URL+'/<int:imgid>', methods=['GET'])
def incorrect_usage1(imgid):
    return incorrect_usage_note()


if __name__ == '__main__':
    app.run(debug=True)
