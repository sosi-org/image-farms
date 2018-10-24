from flask import Flask

from flask import jsonify
from flask import abort
from flask import request

import json

from logger import *

#never call make_response. Always jsonify
from flask import make_response  # for 404

make_response_plain = make_response

make_response = "Uncallable! Never call make_response. Always jsonify."

JSON_MIME='application/json'

def make_response_jsonified(content_dict, rest_code):
    if rest_code == 404:
        if 'error' not in content_dict:
            log_err("The `error` field is missing in Exception. " + repr(content_dict))
            raise ImplementationError("Error field not set in "+repr(content_dict))
    log_highlight(repr(content_dict))
    resp = make_response_plain(jsonify(content_dict), rest_code)
    resp.headers.set('Content-Type', JSON_MIME)
    return resp

"""
#TODO: remove this?
def error404_response_image_notfound(imageid, exception=None):
    # abort(404)
    if exception is not None:
        return make_response_jsonified({'error': "image not found", "imageid": imageid, 'exception': repr(exception)}, 404)
    return make_response_jsonified({'error': "image not found", "imageid": imageid}, 404)
"""
