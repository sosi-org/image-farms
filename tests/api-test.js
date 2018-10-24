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
  console.info("Fine");
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
      //console.log("MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM", err);
      //FIXME
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
      console.log("MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM", err);

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

var globalresult_image_hash = -1

function test_upload(file_name) {
    return with_file_contents(file_name, function(binary_content_buffer) {
        // binary_content_buffer: <Buffer ...>
        // binary_content {'data': [255, 216, ...], 'type': 'Buffer'}
        var body = {binary_content: binary_content_buffer, filename:file_name};
        return fetch(API_BASE+API+'upload', {
            method: 'POST',
            body: BSON.serialize(body),
            headers: { 'Content-Type': 'application/json' },
            })
        .then(
            (response_promise) => {
                resp_text = response_promise.text();
                //console.log("resp_text", resp_text);   // <pending>
                return resp_text;
            },
            (rejection) => {
                console.log("REST sent ERROR(1):", rejection);
                return rejection;
            }
        )
        .then((json_string) => {
            //console.log("ACTUAL JSON CONTENTS:");
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
            globalresult_image_hash = image_info['image-id'];
            var saved_fileformat = image_info['metadata']['mimetype'];
            var recovered_name = image_info['metadata']['orig-name'];
            console.log("   Saved file format: ", saved_fileformat);
            console.log("   Remembered client-size name: ", recovered_name);
            //assertions:
            //if (recovered_name != file_name)
            //    throw Error("test failed: saved_fileformat != file_name: "+recovered_name+" != "+file_name)
            //var basename = file_name.split('/').pop()
            console.log("Comparison:        ", recovered_name, " <> ", file_name)
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

ua = [
        //API_BASE+
        API+NON_EXISTING_IMAGE_ID+'/original',
        API+NON_EXISTING_IMAGE_ID+'/gif',
        API+NON_EXISTING_IMAGE_ID+'/jpeg',
        API+NON_EXISTING_IMAGE_ID+'/png',
    ]

for (i in ua)
{
    point = ua[i]

    hippie()
    .base(API_BASE)
    .get(point)
    //.get(API+NON_EXISTING_IMAGE_ID+'/original')
    .expectStatus(404)  // correctly receive an error (REST error)
    .end();
    /*
    .end(function(err, res, body) {
      if (err) {
          console.log("correctly received an exception:", typeof err, err);
      } else {
          throw new Exception("must have thrown error");
      }
    });
    */
}

console.log("=====================");
console.log("A calm end.");
console.log("=====================");
console.log("");
