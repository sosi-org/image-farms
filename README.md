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

Manual testing can be also done using Insomnia: https://insomnia.rest/download/#linux

Examples:
http://localhost:5000/progimage.com/api/v1.0/all-local
http://localhost:5000/progimage.com/api/v1.0/0/original
http://localhost:5000/progimage.com/api/v1.0/0/jpeg
http://localhost:5000/progimage.com/api/v1.0/0/gif

Note that if original is gif, convertion to gif is a different image.
