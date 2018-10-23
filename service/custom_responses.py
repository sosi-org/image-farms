from flask import Flask

from flask import jsonify
from flask import abort
from flask import request

import json


#never call make_response. Always jsonify
from flask import make_response  # for 404

make_response_plain = make_response
make_response = "Uncallable! Never call make_response. Always jsonify."
def make_response_jsonified(content_dict, rest_code):
    if rest_code == 404:
        assert 'error' in content_dict
    return make_response_plain(jsonify(content_dict), rest_code)

def error404_response_image_notfound(imageid, exception=None):
    # abort(404)
    if exception is not None:
        return make_response_jsonified({'error': "image not found", "imageid": imageid, 'exception': repr(exception)}, 404)
    return make_response_jsonified({'error': "image not found", "imageid": imageid}, 404)
