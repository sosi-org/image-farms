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


var problems = [];
function problem_appender(err, res, body) {
    if (err) {
        problems.push(err);
    }
}
function process_end(err, res, body) {
    problem_appender(err, res, body);
    if (err) {
        console.error("TYPEOF:**************", typeof(err));
    }
}

/*
// Problem: it is async
function report_problems() {
    console.log( "List of problems: " );
    for(let i in problems) {
        console.error( i + ": " + typeof (problems[i]) + "" );
    }

    console.log( "Full list of problems: " );
    for(let i in problems) {
        console.error(i, problems[i] );
    }
}
*/

/*
function default_end(self) {
}
*/
//function default_end(self) {
//}

/*
Client.prototype.end = function(end) {
  if (end) return this.prepare(end);

  var self = this;
  return new Promise(function(resolve, reject) {
    self.prepare(function(err, res, body) {
      if (err) return reject(err);
      resolve(res);
    });
  });
};
*/

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
  process_end(err, res, body);
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
  process_end(err, res, body);
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
    process_end(err, res, body);
    if (err) {
        console.log("Some problem: ", err);
    }

    if (err) {
        throw err;
    }
});


hippie()
//.json()   // image files are not binary => don't use .json()
.base(API_BASE)
.get(API+'0/gif')
.expectStatus(200)
.end(function(err, res, body) {
  process_end(err, res, body);
  if (err) {
      console.log("Some problem: ", err);

      //console.log("body2",body);
      throw err;
  }
});



const fs = require('fs');

function with_file_contents(file_name, content_callback1) {
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
        var r = content_callback1(content);
        /*
        //console.log(data);
        if (then_callback2){
            setTimeout( ()=>{
                then_callback2(r);
            },1000);
        }
        */
    });
}


const BSON = require('bson');
//const data = BSON.serialize(doc);
//const doc = BSON.deserialize(data);

var globalresult_image_hash = -1

function test_upload(file_name, then_callback) {
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
            var imagehash = image_info['image-id'];
            globalresult_image_hash = imagehash;
            var saved_fileformat = image_info['metadata']['mimetype'];
            var recovered_name = image_info['metadata']['orig-name'];
            console.log("   Saved file format: ", saved_fileformat);
            console.log("   Remembered client-size name: ", recovered_name);
            //assertions:
            //if (recovered_name != file_name)
            //    throw Error("test failed: saved_fileformat != file_name: "+recovered_name+" != "+file_name)
            //var basename = file_name.split('/').pop()
            console.log("Comparison:        ", recovered_name, " <> ", file_name);
            // success
            then_callback(imagehash);
        })
        .catch(
             (err) =>
            console.log("Upload: REST sent back Exception(2): ", err)
            /*
            fetch:
                body used already for: http://localhost:5000/progimage.com/api/v1.0/upload
            */
        );
    },
    0 //then_callback
    );
}

if (process.env.IMAGESTORE){
    var IMAGE_STORE = process.env.IMAGESTORE;
    if (IMAGE_STORE.slice(0,1) != '/')
        IMAGE_STORE = IMAGE_STORE + '/';
} else {
    //console.warn("IMAGESTORE env not set.");
    var IMAGE_STORE = "./imagestore/";
    if (! fs.existsSync(IMAGE_STORE) )
        var IMAGE_STORE = "../imagestore/";
    console.warn("IMAGESTORE env not set. Using default: ", IMAGE_STORE);
}
if (! fs.existsSync(IMAGE_STORE) )
    console.error("IMAGESTORE env not set.");

test_upload('./images/tiny_butterfly.jpg', (imagehash)=>{

    // Delay by 1000 to notice, by eye the FS creates and deletes an image.
    var DELAY_MSEC = 0;
    setTimeout(()=>{
    console.log("Just uploaded ", imagehash);

    var TEST_DELETE = true;
    if (TEST_DELETE)
    {
        if (!fs.existsSync(IMAGE_STORE+imagehash+"/original.bin")) {
            console.log("Just uploaded ", imagehash);
            throw new Error('Tester: File is not created on fs.');
        }
        console.log("The generated files exist in folder ", imagehash,". I just double-checked them.");

        // use(data)

        hippie()
        .base(API_BASE)
        .del(API+imagehash+'')
        .expectStatus(204)
        .end((err,res,body)=>{

            console.log("post-DELETION:");
            process_end(err, res, body);

            if (err) {
                console.log("Some problem: ", err);
            }
            // Othewise, it says nothing!

            if (
                fs.existsSync(IMAGE_STORE+imagehash+"/original.bin")
                ||
                fs.existsSync(IMAGE_STORE+imagehash+"/")
            ) {
                throw new Error('Was supposed to be DELETED from fs. It is not.');
            }
            console.log("The files in folder ", imagehash,"are cleared up. I just double-checked.");
        });
    }

    }, DELAY_MSEC);


});



// More uploads and DELETE s:


var TEST_IMAGES = ['./images/potato-block.png', ];
for (i in TEST_IMAGES) {
    test_upload(TEST_IMAGES[i], (imagehash)=>{

        // Delay by 1000 to notice, by eye the FS creates and deletes an image.
        var DELAY_MSEC = 500;
        setTimeout(()=>{
            console.log("Just uploaded ", imagehash);

            var TEST_DELETE = true;
            if (TEST_DELETE)
            {
                if (!fs.existsSync(IMAGE_STORE+imagehash+"/original.bin")) {
                    console.log("Just uploaded ", imagehash);
                    throw new Error('Tester: File is not created on fs.');
                }
                console.log("The generated files exist in folder ", imagehash,". I just double-checked them.");

                hippie()
                .base(API_BASE)
                .del(API+imagehash+'')
                .expectStatus(204)
                .end((err,res,body)=>{
                    console.log("post-DELETION:");
                    process_end(err, res, body);
                    if (err) {
                        console.log("Some problem: ", err);
                    }
                    // Othewise, it says nothing!

                    if (
                        fs.existsSync(IMAGE_STORE+imagehash+"/original.bin")
                        ||
                        fs.existsSync(IMAGE_STORE+imagehash+"/")
                    ) {
                        throw new Error('Was supposed to be DELETED from fs. It is not.');
                    }
                    console.log("The files in folder ", imagehash,"are cleared up. I just double-checked.");
                });
            }

        }, DELAY_MSEC);

    });
}



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
    //.end();
    //.end(process_end);
    .end(function(err, res, body) {
      if (err) {
          console.log("correctly received an exception:", typeof err);
          // dont print the contents of resp/error.
      } else {
          console.error("Something is/ wrong:");
          // FIXME: handle these negative errors.
          //console.error(res); // too long
          //throw new Exception("must have thrown error");
      }
    });
}



console.log("=====================");
console.log("A calm end.");
console.log("=====================");
console.log("");
