# image-farms
A practie using REST

Continuous Integration state:
[![CircleCI](https://circleci.com/gh/sosi-org/image-farms.svg?style=svg)](https://circleci.com/gh/sosi-org/image-farms)

```
mkdir image-farms && cd image-farms
virtualenv -p /usr/bin/python3.5  ifarms
source ifarms/bin/activate
python --version
pip install flask
git clone git@github.com:sosi-org/image-farms.git
```

Steps for CI:
...

Then: Run the server:
```
./bin/start_service.sh
```
And run the test:
```
./bin/test_api.sh
```



Note that if original is gif, convertion to gif creates a separate (cached) image.

The original image maintains the gif animation but after convrering back to gif, the animation will be naturally lost.


The images are stored in "folderhashs" (created based on sha256). This can be useful for defining partitions for scaling.
The filenames are fixed. So that the storage will be secure.

The conversions to various image file formats are implemented. The converted files are cached (stored on disk).

Some tests are implemented using node.js.

This includes the upload test.

The upload will not receive the imageid

The defaiult imageid is 0, in which there is a preloaded image. For test purposes.
All other image-id s are hash codes.



Examples: (for imageid=0)
```
http://localhost:5000/progimage.com/api/v1.0/all-local

http://localhost:5000/progimage.com/api/v1.0/0/original
http://localhost:5000/progimage.com/api/v1.0/0/jpeg
http://localhost:5000/progimage.com/api/v1.0/0/gif

http://localhost:5000/progimage.com/api/v1.0/0/upload
```


Suggestion: Some manual testing can be also done using Insomnia.

Copyright Sohail S.  2018
