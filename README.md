## Project

AWS ECR docker image cross-region replicator

## Requirements

* python3
* boto3
* docker-py

### Installation 

~~~
pip3 install ecr2ecr==1.2
~~~

### Usage

~~~
ecr2ecr -s us-west-2 -d us-east-1 -n image-name -t latest
~~~

### Arguments

*  -s SOURCE      --source-region      ecr region where the image should be pulled from.
*  -d DESTINATION --destination-region ecr region where the image will be pushed to.
*  -n IMAGE_NAME  --image-name         ecr image:tag format
*  -t IMAGE_TAG   --image-tag          ecr image:tag format

## Author

@japzio

## Credits

TrustArc, Inc.

## License

Apache License
Version 2.0, January 2004
http://www.apache.org/licenses/
https://opensource.org/licenses/Apache-2.0