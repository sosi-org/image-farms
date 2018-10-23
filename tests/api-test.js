/*
To run tests:
node api-test.js

Setup steps:
# npm install hippie
# https://docs.npmjs.com/getting-started/using-a-package.json

npm init
npm install hippie
npm set init.author.email "sohale@gmail.com"
npm set init.author.name "sohale"
npm set init.license "unlicenced"

https://github.com/vesln/hippie
*/

var hippie = require('hippie');

var fetch = require('node-fetch');
// import fetch from 'node-fetch';

console.log("api-test.js .");



const API_BASE = 'http://localhost:5000'
const API = '/progimage.com/api/v1.0/'

hippie()
.json()
.base(API_BASE)
.get(API+'all-local')
.expectStatus(200)
//.expectHeader('Content-Type', 'application/json; charset=utf-8')
.end(function(err, res, body) {
  //console.log("body0",body);
  if (err) {
      console.log("Some error:");
      console.log(err);
      throw err;
  }
  //console.log("body",body);
  console.log("Fine");
  //process.exit(0);
});

/*
http://localhost:5000/progimage.com/api/v1.0/all-local
http://localhost:5000/progimage.com/api/v1.0/0/original
http://localhost:5000/progimage.com/api/v1.0/0/jpeg
http://localhost:5000/progimage.com/api/v1.0/0/gif
*/

"Test the preset image (imageid=0)";
hippie()
//.json()   // image files are not binary => don't use .json()
.base(API_BASE)
.get(API+'0/original')
.expectStatus(200)
.end(function(err, res, body) {
  if (err) {
      console.log("===========================");
      console.log("body2",body);
      console.log(err);
      throw err;
  }
});


hippie()
//.json()   // image files are not binary => don't use .json()
.base(API_BASE)
.get(API+'0/jpeg')
.expectStatus(200)
.end(function(err, res, body) {
  if (err) {
      console.log(err);
      throw err;
  }
});


hippie()
//.json()   // image files are not binary => don't use .json()
.base(API_BASE)
.get(API+'0/gif')
.expectStatus(200)
.end(function(err, res, body) {
  if (err) {
      //console.log("body2",body);
      throw err;
  }
});

const fs = require('fs');

function with_file_contents(file_name, content_callback) {
    if (!fs.existsSync(file_name)) {
        throw new Error('file does not exist: ' + file_name);
    }
    //File exists:
    fs.readFile(file_name, function read(err, data) {
        if (err) {
            console.log("body2",body);
            throw err;
        }

        content = data;  // <Buffer
        content_callback(content);
        //console.log(data);
    });
}


const BSON = require('bson');
//const data = BSON.serialize(doc);
//const doc = BSON.deserialize(data);

function test_upload(file_name) {
    with_file_contents(file_name,function(content){
        console.log("uploading content:", content);
        //var f = fetch(API_BASE+API+'upload');
        var body = {binary_content:content, filename:file_name};
        // binary content {'data': [255, 216, ...], 'type': 'Buffer'}

        //console.log(f);
        fetch(API_BASE+API+'upload', {
            method: 'POST',
            // todo: use simple binary content type? no.
            body: BSON.serialize(body),
            headers: { 'Content-Type': 'application/json' },
            })
        .then(
            (response_promise) => {
                //return response.json();
                console.log("OK! response:");
                //console.log(response_promise);
                //console.log(response_promise.json());   // prints: Promise(...)
                resp_text = response_promise.text();
                console.log("resp_text", resp_text);   // prints: Promise( <pending> )
                console.log("OK2");
                //return response_promise.json();
                return resp_text;
            },
            (rejection) => {
                console.log("REST sent ERROR(1):", rejection);
                return rejection;
            }
        )
        .then((json_string) => {
            console.log("ACTUAL JSON CONTENTS:");
            console.log(json_string);
            var image_info = JSON.parse(json_string);
            /*
            Example:
                {
                  "image-id": "1222777497",
                  "metadata": {
                    "mimetype": "image/jpeg",
                    "orig-name": "images_tiny_butterfly.jpg"
                  }
                }
            */
            global_image_hash = image_info['image-id'];
            var saved_fileformat = image_info['metadata']['mimetype'];
            var recovered_name = image_info['metadata']['orig-name'];
            console.log("saved file format = ", saved_fileformat);
            console.log("Remembered client-size name: ", recovered_name);
            //assertions:
            //if (recovered_name != file_name)
            //    throw Error("test failed: saved_fileformat != file_name: "+recovered_name+" != "+file_name)
            console.log("saved_fileformat versus file_name: ", recovered_name, " versus ", file_name)
        })
        .catch(
             (err) =>
            console.log("REST sent back Exception(2):", err)
            /*
            fetch:
                body used already for: http://localhost:5000/progimage.com/api/v1.0/upload
            */
        );
    })
}

test_upload('./images/tiny_butterfly.jpg');



//fetch('http://jsonplaceholder.typicode.com/posts/1')

/*
const fs = require('fs');
function test_upload(fs, file_name) {
    if (!fs.exists(file_name)) {
        throw new Error('file does not exist');
    }

    fs.readFile(file_name, function read(err, data) {
        if (err) {
            throw err;
        }

        content = data;


        hippie()
        .json()
        .base(API_BASE)
        .get(API+'upload')


        return request(app)
          .post('/api/v1/documentations/')

           // Attach the file with key 'file' which is corresponding to your endpoint setting.
          .attach('file', filePath)
          .then((res) => {
            const { success, message, filePath } = res.body;
            expect(success).toBeTruthy();
            expect(message).toBe('Uploaded successfully');
            expect(typeof filePath).toBeTruthy();

            // store file data for following tests
            testFilePath = filePath;
          })
          .catch(err => console.log(err));

    });
};
*/


NON_EXISTING_IMAGE_ID = '123123'

for (point in [
        API+NON_EXISTING_IMAGE_ID+'/original',
        API+NON_EXISTING_IMAGE_ID+'/gif',
        API+NON_EXISTING_IMAGE_ID+'/jpeg',
    ])
{
    hippie()
    .base(API_BASE)
    .get(API+NON_EXISTING_IMAGE_ID+'/original')
    .expectStatus(200)
    .end(function(err, res, body) {
      if (err) {
          console.log("correctly sent an exception:", typeof err);
      } else {
          throw new Exception("must have thrown error");
      }
    });
}

console.log("=====================");
console.log("A calm end.");
console.log("=====================");
console.log("");
