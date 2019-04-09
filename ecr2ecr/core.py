#!/usr/bin/env python3

import base64
import boto3
import logging
import docker
import json
import argparse
import datetime
import sys
import io


logger = logging.getLogger(__name__)


class AuthData:
  """
  Object to represent aws ecr authentication data and resusable properties
  """
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
  def registry(self):
    return self.auth_data['proxyEndpoint'].split('//')[1]

  @property
  def expiry(self):
    return dict(expiry=self.auth_data['expiresAt'].strftime('%s'))

  @staticmethod
  def base64_decode(self, string_b64):
    return str(base64.b64decode(string_b64).decode(self.encoding))
    
  def ecr_fqdn(self, image_name):
    return self.registry + '/' + image_name


def get_auth_data(aws_region):
  """
  Get authentication data from specified aws ecr region.
  Parameters
  __________
  aws_region: str
    AWS Region to authenticate to
  Returns
  _______
  AuthData - authentication data representation
  """
  logger.info('fetching ecr creds from ' + aws_region)
  ecr_client = boto3.client('ecr', region_name=aws_region)
  return AuthData(ecr_client.get_authorization_token()['authorizationData'])


def docker_login(username, password, registry):
  """
  Performs docker login to a specified ecr region.
  Parameters
  __________
  username: str
    Docker registry username
  password: str
    Docker registry password
  registry: AuthData.registry
    AWS Region to authenticate to.
  """
  docker_client = docker.from_env()
  try:
    logger.info('logging in to ' + registry)
    response = docker_client.login(username=username, password=password, registry=registry, dockercfg_path='$HOME/.docker/config.json')
    logger.info('login successful to ' + registry)
  except (docker.errors.APIError, docker.errors.TLSParameterError) as err:
    logger.error(err)
    sys.exit(1)


def pull_image(auth_data, repository):
  """
  Performs pulling if images from aws ecr
  Parameters
  __________
  auth_data: AuthData
    Docker registry username
  repository: str
    Docker image repository
  """
  docker_client = docker.from_env()
  auth_config = {'username': auth_data.username, 'password': auth_data.password }
  try:
   for stream in docker_client.pull(auth_data.ecr_fqdn(repository), auth_config=auth_config, stream=True, decode=True):
      response = stream
      if ( 'status' in response):
        logger.info(response['status'])
      elif ( 'errorDetail' in response):
        raise Exception(response['errorDetail']['message'], auth_data.registry)
  except (docker.errors.APIError) as err:
   logger.error(err)
   sys.exit(2)


def tag_image(current_tag, target_tag):
  """
  Performs pulling if images from aws ecr
  Parameters
  __________
  current_tag: str
    Docker image tag on current local docker registry.
  target_tag: str
    New image tag to be added.
  """
  docker_client = docker.from_env()
  try:
    if ( current_tag ==  target_tag ):
      raise Exception('Tagging {} with {} does not make any sense!'.format(current_tag, target_tag))
    #image = docker_client.images.get(current_tag)
    is_successful = docker_client.tag(current_tag, target_tag)
    if is_successful:
      logger.info('tagging {} with {} successful!'.format(current_tag, target_tag))
  except (docker.errors.APIError, Exception) as err:
   logger.error(err)
   sys.exit(3)


def push_image(auth_data, repository):
  """
  Performs pushing if images to aws ecr
  Parameters
  __________
  auth_data: AuthData
    Docker registry username
  repository: str
    Docker image repository
  """
  docker_client = docker.from_env()
  auth_config = {'username': auth_data.username, 'password': auth_data.password }
  try:
    for stream in docker_client.push(auth_data.ecr_fqdn(repository), auth_config=auth_config, stream=True, decode=True):
      response = stream
      if ( 'status' in response):
        logger.info(response['status'])
      elif ( 'errorDetail' in response):
        raise Exception(response['errorDetail']['message'], auth_data.registry)
  except (docker.errors.APIError, docker.errors.DockerException, Exception) as err:
    logger.error(err)
    sys.exit(4)


def logger_config(level=logging.INFO):
  """
  Customize root logger according to format intended
  Parameters
  __________
  level: logging.LEVEL
    just limited to INFO and DEBUG for now
  """
  logging.basicConfig(
    level=level, 
    format='%(asctime)s.%(msecs)d - %(name)s - %(levelname)s - %(message)s', 
    datefmt='%Y-%m-%dT%H:%M:%S%Z'
  )


def main():
  
  parser = argparse.ArgumentParser(description='AWS ECR docker image cross-region replicator.')

  parser.add_argument("-s", "--source-region", dest="source", help="ecr region where the image should be pulled from.", type=str, required=True)
  parser.add_argument("-d", "--dest-region", dest="dest", help="ecr region where the image will be pushed to." ,type=str, required=True)
  parser.add_argument("-n", "--image-name", dest="image_name", help="ecr image:tag format", type=str, required=True)
  parser.add_argument("-t", "--image-tag", dest="image_tag", help="ecr image:tag format", type=str, required=True)
  parser.add_argument("-v", "--verbose", dest="verbose", help="log verbosity", action='store_true')
  
  args = parser.parse_args()
  
  logger_config(level=logging.DEBUG if args.verbose else logging.INFO)

  auth_data_source = get_auth_data(args.source)
  auth_data_target = get_auth_data(args.dest)

  docker_login(auth_data_source.username, auth_data_source.password, auth_data_source.endpoint)
  docker_login(auth_data_target.username, auth_data_target.password, auth_data_target.endpoint)

  image_name = args.image_name + ':' + args.image_tag

  pull_image(auth_data_source, image_name)

  tag_image(auth_data_source.ecr_fqdn(image_name), auth_data_target.ecr_fqdn(image_name))

  push_image(auth_data_target, image_name)


if __name__== "__main__":  
  main()