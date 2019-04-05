#!/usr/bin/env python3

import unittest2 as unittest
from ecr2ecr.core import AuthData

class AuthDataProps_Tests(unittest.TestCase):

  auth_data =  AuthData([
      {
          "authorizationToken": "*",
          "expiresAt": 1554234159.187,
          "proxyEndpoint": "https://565289216568.dkr.ecr.us-west-2.amazonaws.com"
      }
  ])

  def username_test(self):
    self.assertEqual(auth_data.username, 'AWS')
    
  def password_test():
    pass
  
  def endpoint_test():
    pass
  
  def registry():
    pass

  def expiry_test():
    pass

  def base64_decode_test():
    pass
    
  def ecr_fqdn_test():
    pass


if __name__ == '__main__':
    unittest.main()