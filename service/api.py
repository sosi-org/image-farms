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

import json
# used for download only
EXTENTIONS = {'image/gif': 'gif', 'image/jpeg':'jpeg'}

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
        print("IMAGE 0000000000000000000")
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
        except:
            # not really 404
            abort(404)

    else:
        abort(404)
# download  : as_attachment=True

if __name__ == '__main__':
    app.run(debug=True)
