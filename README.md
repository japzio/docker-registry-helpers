## Project

AWS ECR docker image cross-region replicator

## Requirements

* python3 and pip3
* boto3
* docker

### Usage

~~~
./main.py -s us-west-2 -t us-east-1 -in image-name -it latest
~~~

### Parameters

~~~
./main.py --help
~~~

## Author

@japzio

## Credits

TrustArc, Inc.

## License

Apache License
Version 2.0, January 2004
http://www.apache.org/licenses/
https://opensource.org/licenses/Apache-2.0