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
  if (err) {
      console.log("Some error:");
      console.log(err);
      throw err;
  }
  console.log("Fine");
  //process.exit(0);
});



const fs = require('fs');

function with_file_contents(file_name, content_callback) {
    if (!fs.existsSync(file_name)) {
        throw new Error('file does not exist: ' + file_name);
    }
    //File exists:
    fs.readFile(file_name, function read(err, data) {
        if (err) {
            throw err;
        }

        content = data;  // <Buffer
        content_callback(content);
        //console.log(data);
    });
}

function test_upload____failed_attempt(file_name) {
    with_file_contents(file_name,function(content){
        console.log("uploading content:", content);

        // incorrect call (upload using other than POST) should result in 404
        hippie()
        .json()
        .base(API_BASE)
        .get(API+'upload')
        .expectStatus(404)
        .end()
        // Not good practice:
        .catch(function(){
            console.log("caught");
        });

        // .auth('user', 'password')

        hippie()
        .json()
        .base(API_BASE)
        .send(content)
        /*.send({ files: {
            'binary_content': content,  // 'binary'
            'filename': file_name,  // 'original-filename'
        } })*/
        .post(API+'upload')
        .expectStatus(201)
        .end()
        .catch(function(ex) {
            console.log("Exception caught: "+ex);
        })


    })
}

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
            body: JSON.stringify(body),
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
        .then((json) => {
            console.log("ACTUAL JSONCONTENTS:");
            console.log(json);
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

console.log("=====================");
console.log("A calm end.");
console.log("=====================");
console.log("");
