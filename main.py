#!/usr/bin/env python3

import base64
import boto3
import logging
import docker
import json
import argparse
import datetime
import sys

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d,%H:%M:%S')
logger = logging.getLogger(__name__)


docker_client = docker.from_env()


class AuthData:

  encoding = 'UTF-8'

  def __init__(self, auth_data):
    self.auth_data = auth_data[0]
  
  def __iter__(self):
    return self.__dict__.iteritems()

  @property
  def username(self):
    return self.base64_decode(self, self.auth_data['authorizationToken']).split(':')[0]
  
  @property
  def password(self):
    return self.base64_decode(self, self.auth_data['authorizationToken']).split(':')[1]
  
  @property
  def endpoint(self):
    return self.auth_data['proxyEndpoint']
  
  @property
  def repo_prefix(self):
    return self.auth_data['proxyEndpoint'].split('//')[1] + '/'

  @property
  def expiry(self):
    return dict(expiry=self.auth_data['expiresAt'].strftime('%s'))

  @staticmethod
  def base64_decode(self, string_b64):
    return str(base64.b64decode(string_b64).decode(self.encoding))
    
  def get_repository(self, image_name):
    return self.repo_prefix + image_name


def get_auth_data(aws_region):
  logger.info('fetching ecr creds from ' + aws_region)
  ecr_client = boto3.client('ecr', region_name=aws_region)
  return AuthData(ecr_client.get_authorization_token()['authorizationData'])


def docker_login(username, password, registry):
  try:
    logger.info('logging in to ' + registry)
    response = docker_client.login(username=username, password=password, registry=registry, dockercfg_path='$HOME/.docker/config.json')
    logger.info('login successful to ' + registry)
  except (docker.errors.APIError, docker.errors.TLSParameterError) as err:
    logger.error(err)
    sys.exit(1)


def pull_image(name, username, password, tag='latest'):
  auth_config = {'username': username, 'password': password }
  try:
   docker_client.images.pull(name, auth_config=auth_config)
  except (docker.errors.APIError) as err:
   logger.error(err)
   sys.exit(2)


def tag_image(current_tag, target_tag):
  try:
   image = docker_client.images.get(current_tag)
   image.tag(target_tag)
  except (docker.errors.APIError) as err:
   logger.error(err)
   sys.exit(3)


def push_image(name, username, password, tag='latest'):
  auth_config = {'username': username, 'password': password }
  try:
    docker_client.images.push(name, auth_config=auth_config)
  except (APIError, TLSParameterError) as err:
   logger.error(err)


def main():
  
  parser = argparse.ArgumentParser(description='AWS ECR docker image cross-region replicator.')

  parser.add_argument("-s", "--source-region", dest="source", help="ecr region where the image should be pulled from.", type=str, required=True)
  parser.add_argument("-d", "--destination-region", dest="destination", help="ecr region where the image will be pushed to." ,type=str, required=True)
  parser.add_argument("-n", "--image-name", dest="image_name", help="docker image name.", type=str, required=True)
  parser.add_argument("-t", "--image-tag", dest="image_tag", help="docker image tag default=latest.", default='latest', type=str)

  args = parser.parse_args()
  
  auth_data_source = get_auth_data(args.source)
  auth_data_target = get_auth_data(args.destination)

  docker_login(auth_data_source.username, auth_data_source.password, auth_data_source.endpoint)
  docker_login(auth_data_target.username, auth_data_target.password, auth_data_target.endpoint)

  image = args.image_name + ':' + args.image_tag

  pull_image(auth_data_source.get_repository(image), auth_data_source.username, auth_data_source.password, tag=args.image_tag)
  tag_image(auth_data_source.get_repository(image) ,  auth_data_target.get_repository(image))
  push_image(auth_data_target.get_repository(image), auth_data_target.username, auth_data_target.password, tag=args.image_tag)


if __name__== "__main__":  
  main()