# images-farm
A practie using REST

Continuous Integration:
[![CircleCI](https://circleci.com/gh/sosi-org/image-farms.svg?style=svg)](https://circleci.com/gh/sosi-org/image-farms)

## Instructions
Installation steps
```
mkdir image-farms && cd image-farms
virtualenv -p /usr/bin/python3.5  ifarms
source ifarms/bin/activate
python --version
#pip install flask
git clone git@github.com:sosi-org/image-farms.git
bin/reinstall.sh

```

Then: Run the server:
```
source ./bin/start_service.sh
```
Finally, run the test:
```
./bin/test_api.sh
```


## Notes

Note that if original is gif, convertion to gif creates a separate (cached) image.

The original image maintains the gif animation but after convrering back to gif, the animation will be naturally lost.


The images are stored in "folderhashs" (created based on sha256). This can be useful for defining partitions for scaling.
The filenames are fixed. So that the storage will be secure.

The conversions to various image file formats are implemented. The converted files are cached (stored on disk).

Some tests are implemented using node.js.

This includes the upload test.

The upload will not receive the imageid (i.e. folderhashs)

The default imageid is 0, in which there is a preloaded image. For test purposes.
All other image-id s are hash codes (folderhashs).

The upload is a simple POST method with a certainway of passing parameters.

The DELETE operation now works.


#### Examples

Examples: (for imageid=0)
```
http://localhost:5000/progimage.com/api/v1.0/all-local

http://localhost:5000/progimage.com/api/v1.0/0/original
http://localhost:5000/progimage.com/api/v1.0/0/jpeg
http://localhost:5000/progimage.com/api/v1.0/0/gif

http://localhost:5000/progimage.com/api/v1.0/0/upload
```


Suggestion: Some manual testing can be also done using Insomnia.

#### Future work

Next steps:
* A classic upload method that can be used with forms. The current upload can be renamed to <imagid>.
* Check both <imagid>/command and <imagid>/command/
* Swagger documents (and its tests)
* Software configuration using ENV variables.


Copyright Sohail S.  2018
