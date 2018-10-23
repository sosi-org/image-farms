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

function test_upload(file_name) {
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

        hippie()
        //.json()
        .base(API_BASE)
        .post(API+'upload')
        .expectStatus(201)
        .end()
        /*.catch(function(){
            console.log("caught");
        })*/


    })
}

test_upload('./images/tiny_butterfly.jpg');

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
