from image_exceptions import *
import imageio
import os
import hashlib
import struct
import json


from werkzeug.utils import secure_filename


KILO = 1024
MEGA = KILO*KILO
GIGA = MEGA*KILO

# ************************************************************
# *  config

# direct access discouraged:
IMAGE_BASE = '../imagestore/'



# code-time constant
service_config = {

    'max-size': 100*MEGA,      # Maximum size of hte image file

    'max-width': 10000,        # Maximum dimension, either width or height

    'upload-replaces': True,
    # Whether you can upload an image that is already uploaded.
    # If True, first deletes the contents before doing the upload.
    # It should be False in production, but it is set to True for test purposes.
}

FIRST_DELETE_BEFORE_UPLOAD = service_config['upload-replaces']

# load-time (after deploy-time) constant
service_config_state = {
    'partition-id': 1,         # For future use.
}

# implementation consts

# used for download only
EXTENTIONS = {'image/gif': 'gif', 'image/jpeg':'jpeg', 'image/png':'png'}

#used for converted images:
MIME_LOOKUP = {'gif':'image/gif', 'jpeg':'image/jpeg', 'png':'image/png'}


#DEFAULT_IMAGE_NAME
FIXEDNAME_ORIGINALBINARY = "original.bin"
FIXEDNAME_METADATAJSON = "metadata.json"


# ************************************************************
# *  logic

#class ImagesService:
#    def __init__():
#        # It is stateless
#        pass


def service_deployment_test():
    # Makes sure we are running from the correct folder
    assert os.path.exists(IMAGE_BASE)


def invoices_listall():
    long_long_list = ['img1.png', 'img2.jpg']
    return {'images': long_long_list}


def fetchlocal_original_mimetype_fromcontent(folderhash):
    """ Uses image.io to get the File Format NOT from the extention. Directly from the contents."""
    filename = IMAGE_BASE + folderhash+"/"+FIXEDNAME_ORIGINALBINARY
    with imageio.get_reader(filename) as r:
        fileformat_md = r.get_meta_data()

        #
        graphics_fileformat = str(r.format.name)  # !
        assert type(graphics_fileformat) is str

        #print(fileformat_md)
        if 'version' in fileformat_md and fileformat_md['version'] == b'GIF87a':
            #log("GIF")
            """
            GIF:
            {'version': b'GIF87a', 'extension': (b'NETSCAPE2.0', 27), 'loop': 0, 'duration': 10}
            """
            return MIME_LOOKUP['gif']
        elif 'jfif_version' in fileformat_md or 'jfif' in fileformat_md:
            #log("JPEG")
            """
            JPEG:
                {'jfif_version': (1, 1), 'dpi': (72, 72), 'jfif': 257, 'jfif_unit': 1, 'jfif_density': (72, 72)}
            """
            return MIME_LOOKUP['jpeg']
        elif graphics_fileformat == 'PNG-PIL':
            return MIME_LOOKUP['png']
        else:
            log_err("unknown image type. (Could be PNG which is not implemented)")
            log_err("imageio output: "+json.dumps(fileformat_md)+"   format:"+graphics_fileformat)
            raise UnknownFileFormat(
                    imageid=repr(folderhash),
                    comment="ImageIO could not detect the original image type. ",
                    imageio_metadata=json.dumps(fileformat_md),
                    format=graphics_fileformat,
            )
        #return mimetype
    #throw image does not exist


def metadata_filename_from_folderhash(folderhash):
    return IMAGE_BASE + folderhash + "/" + FIXEDNAME_METADATAJSON


def get_metadata_locally(folderhash):
    # fetchlocal_metadata()
    metadata_filename = metadata_filename_from_folderhash(folderhash)
    meta_data_json = open(metadata_filename, "rt").read()
    metadata = json.loads(meta_data_json)
    return metadata


def generate_metadata(folderhash, original_name):
    """ from stored file.  original_name: uploaded name """
    metadata_filename = metadata_filename_from_folderhash(folderhash)
    mimetype = fetchlocal_original_mimetype_fromcontent(folderhash)

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
    #metadata = get_metadata_locally(folderhash)
    return


# fetchlocal_mimetype
def fetchlocal_original_mimetype_fromjson(folderhash, key='mimetype'):
    DEFAULT_MIMETYPE = "image/jpeg"
    #DEFAULT_EXTENTION = "jpeg"
    # todo: use imageio.get_reader()
    # get_meta_data()
    try:
        metadata = get_metadata_locally(folderhash)
        fieldname = key
        mimetype = metadata[fieldname]
        return mimetype #, EXTENTIONS[mimetype]
    except:
        return DEFAULT_MIMETYPE #, EXTENTIONS[DEFAULT_MIMETYPE]



def fetchlocal_binary(folderhash):
    assert type(folderhash) is str
    filename = IMAGE_BASE + folderhash +"/"+FIXEDNAME_ORIGINALBINARY
    if not os.path.exists(filename): #IMAGE_BASE + str(folderhash)):
        raise ImageIdNotFound(folderhash)
    try:
        return open(filename, "rb").read()
    except FileNotFoundError:
        raise ImageIdNotFound(folderhash)



def retrieve_original(folderhash):
    #folderhash = folderhash_from_imageid(imageid_int)
    """
    if imageid_int == 0:
        print("Default image requested.")
        #def get_image(pid):
        #image_binary = read_image(pid)
        #bytes_read

        # image_id
        folderhash = "sample0000"
    else:
        #raise ImageIdNotFound(imageid_int)
        folderhash = str(imageid_int)
    """
    try:
        #original_mimetype = fetchlocal_original_mimetype_fromjson(folderhash)
        # FIXME: We don't need to create this again. We can use the cached vertion.
        #   Idea: use a @cache decorator
        original_mimetype = fetchlocal_original_mimetype_fromcontent(folderhash)
        log("Retrieving original image. Original mimetype: " + original_mimetype)
        #extention = EXTENTIONS[original_mimetype]

        image_binary = fetchlocal_binary(folderhash)
        if False:
            orig_filename = get_metadata_locally(folderhash)['orig-name']  # not always asked for
        else:
            orig_filename = "unused"
        return image_binary, original_mimetype, orig_filename
    except FileNotFoundError:
        raise ImageIdNotFound(folderhash)
    """
    response = make_response_plain(image_binary)
    response.headers.set('Content-Type', original_mimetype)

    download = False
    if download:
        response.headers.set('Content-Disposition', 'attachment', filename=orig_filename)

    return response
    """


class data_invariants:
    #data_consistency_invariants
    @staticmethod
    def consistency_invariance02(local_filename, local_foldername):
        #consistency_check02
        return (os.path.exists(local_filename) and  os.path.exists(local_foldername)) or (not os.path.exists(local_filename) and not os.path.exists(local_foldername))

class data_consistency_checks:
    @staticmethod
    def check02(local_filename, local_foldername):
        """ If the original.bin is not there, there should be nothing there. In fact there should be no folder!. Already rmdir()ed."""
        return
        if not data_invariants.consistency_invariance02(local_filename, local_foldername):
            raise ImplementationError("consistency: "+repr((local_filename, local_foldername)))
        #if filesize(FIXEDNAME_ORIGINALBINARY) == 0:
        #    raise DataConsistencyError

    @staticmethod
    def image_id(folderhash):
        assert type(folderhash) is str
        local_foldername = IMAGE_BASE + folderhash
        local_filename = local_foldername+'/'+FIXEDNAME_ORIGINALBINARY
        data_consistency_checks.check02(local_filename, local_foldername)

def all_cached_filenames(folderhash, cached_ones=True, essential_ones=False):
    assert type(folderhash) is str
    if essential_ones:
        yield FIXEDNAME_ORIGINALBINARY
        yield FIXEDNAME_METADATAJSON
    if cached_ones:
        for image_format in MIME_LOOKUP:
            yield folderhash + "." + image_format

"""
def delete_cached_transformations(folderhash):
    #def delete_everything_else(folderhash):
    assert type(folderhash) is str
    local_foldername = IMAGE_BASE + folderhash

    for filename in all_cached_filenames(folderhash):
        local_filename = local_foldername+'/'+filename
        "local_filename = local_foldername+'/'+filename"
        if os.path.exists(local_filename):
            os.remove(local_filename)
"""


def manual_cleanup(folderhash, delete_cached=False):
    #def manual_cleanup(local_filename, local_foldername):
    filename=FIXEDNAME_ORIGINALBINARY
    assert type(folderhash) is str
    local_foldername = IMAGE_BASE + folderhash

    local_filename = local_foldername+'/'+filename
    metadata_filename = metadata_filename_from_folderhash(folderhash)

    delete_essentials = True
    if delete_essentials:
        # unsafe
        if os.path.exists(local_filename):
            os.remove(local_filename)
        if os.path.exists(metadata_filename):
            os.remove(metadata_filename)

    if delete_cached:
        #delete_cached_transformations(folderhash)
        for filename in all_cached_filenames(folderhash, cached_ones=True, essential_ones=False):
            local_filename = local_foldername+'/'+filename
            """local_filename = local_foldername+'/'+filename"""
            if os.path.exists(local_filename):
                os.remove(local_filename)


    if os.path.exists(local_foldername):
        os.rmdir(local_foldername)

    if os.path.exists(local_foldername):
        #raise InternalDataConsistencyError()
        raise ImplementationError("consistency: folder cannot be removed. Possibly non-empty.")
        # i.e. check if all_cached_filenames() covers all possible files.

def do_actual_upload(original_clientside_filename, file_content_binary, pre_delete=FIRST_DELETE_BEFORE_UPLOAD):

    print(type(file_content_binary))  # <class bytes>
    #os.path.join(app.config['UPLOAD_FOLDER'], filename)
    #image_id = [(fname, hashlib.sha256(file_as_bytes(open(fname, 'rb'))).digest()) for fname in fnamelst]
    #???????? file_content = file  # file_as_bytes(open(fname, 'rb'))
    file_content = file_content_binary
    image_sha256 = hashlib.sha256(file_content).digest()
    # b' .. ' -> sha256 -> hash object -> digest -> binary b'...'
    log("sha256 hash="+str(image_sha256))
    #image_id = image_sha256[:8]

    s_compiled = struct.Struct('<L')  # 4 bytes    #L 	unsigned long 	integer 	4
    hash_int_val = s_compiled.unpack_from(image_sha256)[0]  # 4 bytes
    #return {'hash val':hash_int_val}, "foldername"

    hash_int_val = hash_int_val
    log("Uploading: hash_int_val:::"+str(hash_int_val))



    #data_consistency_checks.check02(local_filename, local_foldername)


    # file_id is in fact folder_id
    #local_filename
    #folderhash = folderhash_from_imageid(hash_int_val)  # i.e. imagehash
    folderhash = str(hash_int_val)

    data_consistency_checks.image_id(folderhash)

    # if allow overwriting using POST (i.e. "upload")
    if pre_delete:
        #local_foldername = foldername_from_folderhash(folderhash)
        assert type(folderhash) is str
        local_foldername = IMAGE_BASE + folderhash

        manual_cleanup(folderhash, delete_cached=True)

        data_consistency_checks.image_id(folderhash)
        #data_consistency_checks.check02(local_filename, local_foldername)



    local_filename = local_foldername+'/'+FIXEDNAME_ORIGINALBINARY

    # Invariant: Has to be empty here. (Either manually using `pre_delete`, or not to exist beforehand)
    # clean
    if os.path.exists(local_filename) or \
        os.path.exists(local_foldername): #not os.path.isdir(local_foldername):
        raise ImageAlreadyExists(original_clientside_filename, folderhash)

    os.makedirs(local_foldername, exist_ok=True)

    with open(local_filename, "wb") as fl:
        #fl.save('./'+local_foldername+'/'+FIXEDNAME_ORIGINALBINARY)  #really? a 'file' object?
        fl.write(file_content_binary)
        log("WRITE successful: "+ local_filename)
    log("file closed.", )

    # no need for this! it is completely secure! We use a fixed name (FIXEDNAME_ORIGINALBINARY) to store the file.
    original_clientside_filename_secured = secure_filename(original_clientside_filename)
    del original_clientside_filename

    generate_metadata(folderhash, original_clientside_filename_secured)
    metadata = get_metadata_locally(folderhash)
    # actual_filename ='original.bin' is NOT metadata['orig-name']
    return metadata, folderhash


def ignore(x):
    pass

def kill_image(folderhash, ownership_proof):
    """
    @param ownership_proof: An authentification & ownership proof or image idetinfication where there is right to access (and delete).
    Can be a publickey + owner_id. Use metadata to store and check this.
    """
    ignore(ownership_proof)
    data_consistency_checks.image_id(folderhash)
    manual_cleanup(folderhash)
    data_consistency_checks.image_id(folderhash)
    #return 1



def extract_mask(folderhash):
    print("===========================================::")
    original_image_binary = fetchlocal_binary(folderhash)
    im = imageio.imread(original_image_binary)

    mask_image_format = 'png'
    converted_mimetype = MIME_LOOKUP[mask_image_format]

    #local_filename
    local_cached_filename = IMAGE_BASE + folderhash+"/mask."+mask_image_format


    # remove alpha channel
    if im.shape[2] >3:
        mask = im[:,:,3]
    else:
        raise ImageHasNoMask(folderhash)

    imageio.imwrite(local_cached_filename, mask)
    #todo: add metadata

    converted_binary = open(local_cached_filename, "rb").read()
    return converted_binary, converted_mimetype


def convert_to_format_and_respond(folderhash, image_format):
    assert type(folderhash) is str
    log("fetching binary file: "+ folderhash + " for: " + image_format)

    """ Note: I dont cache here. It is up to the browser and server to cache it."""

    #original_mimetype = fetchlocal_original_mimetype_fromjson(folderhash)

    #converted_mimetype = MIME_LOOKUP.get(image_format, "UNKNOWN1")
    #converted_mimetype = MIME_LOOKUP[image_format]
    converted_mimetype = MIME_LOOKUP.get(image_format, None)
    assert converted_mimetype is not None

    log("converting to: mimetype: " + converted_mimetype)

    original_image_binary = fetchlocal_binary(folderhash)

    im = imageio.imread(original_image_binary)
    #print(im)
    log("image read: " + repr(im.shape))

    #if converted_mimetype != original_mimetype:

    if True:
        # do the conversion

        #local_filename
        local_cached_filename = IMAGE_BASE + folderhash+"/"+folderhash+"."+image_format
        #cached_name = ""+"."+image_format
        log("writing: local_cached_filename:" + local_cached_filename)


        # remove alpha channel
        im = im[:,:,:3]
        imageio.imwrite(local_cached_filename, im)
        # assumption: exntention, type, and imageio's extention are the same
        log("imwrite() finished.")
    else:
        pass

    converted_binary = open(local_cached_filename, "rb").read()
    log("read binary converted file.")
    return converted_binary, converted_mimetype




"""
file_id:  an <int>
imageid:  foldername
"""

"""
def folderhash_from_imageid(imageid_int):
    # assert int
    assert (imageid_int+2)/2 == (imageid_int)/2+1, repr(imageid_int)

    if imageid_int == 0:
        folderhash = "sample0000"
        return folderhash
    #elif imageid_int == 12:
    #    file_id = "00012"
    #    return file_id

    #else:
    #    #return error404_response_image_notfound(imageid_int)
    #    raise ImageIdNotFound(imageid_int)
    return str(imageid_int)
"""


#def foldername_from_folderhash(folderhash):
#    local_foldername = IMAGE_BASE + str(folderhash)
#    return local_foldername


"""
def convert_jpeg(imageid_int):

    print("convertion requested.")
    folderhash = folderhash_from_imageid(imageid_int)

    image_format = 'jpeg'   # same as extention
    return convert_to_format_and_respond(folderhash, image_format)


def convert_gif(imageid_int):
    folderhash = folderhash_from_imageid(imageid_int)

    image_format = 'gif'   # same as extention
    return convert_to_format_and_respond(folderhash, image_format)


def convert_png(imageid_int):
    folderhash = folderhash_from_imageid(imageid_int)
    image_format = 'png'   # same as extention
    return convert_to_format_and_respond(folderhash, image_format)
"""

def extract_mask_api(folderhash):
    #print("imageid_int",imageid_int)
    #folderhash = folderhash_from_imageid(imageid_int)
    #print("imageid_int",imageid_int)
    image_format = 'png'   # same as extention
    return extract_mask(folderhash)
    #return convert_to_format_and_respond(folderhash, image_format)


# use class? or the module as namespace? (ans remove @staticmethod_)
