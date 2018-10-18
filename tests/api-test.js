/*
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

hippie()
.json()
.base('http://localhost:5000')
.get('/progimage.com/api/v1.0/all-local')
.expectStatus(200)
.end(function(err, res, body) {
  if (err) {
      console.log("Some error:");
      console.log(err);
      throw err;
  }
  console.log("Fine");
  process.exit(0);
});
