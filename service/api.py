#!ifarms/bin/python

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
    eurl = API_ENDPOINT_URL + "/all"
    return \
        "Welcome to ProgImage.com API.<br/>"+ \
        "See https://github.com/sosi-org/image-farms/blob/master/README.md<br/>"+ \
        "For full list: try: <a href=\""+ eurl + "\"> "+eurl+"</a>."

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found (Sosi)'}), 404)


# Not recommended in production. For test only
@app.route(API_ENDPOINT_URL+'/all', methods=['GET'])
def invoices_listall():
    long_long_list = ['img1.png', 'img2.jpg']
    return jsonify({'images': long_long_list})




if __name__ == '__main__':
    app.run(debug=True)
