import requests, json
import time

class QuantumApi():
  def __init__(self):
    self.jwt = None
    self.account_id = None
    self.project_id = None
    
  def __set_header(self, jwt = None):
    headers = {'Content-Type': 'application/json'}
    if (jwt != None):
      headers['X-Auth-Token']=jwt
    return headers
  
  def __post_to_api(self, url, payload, jwt = None):
    headers = self.__set_header(jwt)
    r = requests.post('https://api.quantum.socialmetrix.com/{0}'.format(url), data=json.dumps(payload), headers=headers)
    result = r.json()
    if(r.status_code >= 200 and r.status_code < 300):
      return result
    else:
      raise Exception('Error: ' + json.dumps(result))

  # Login / Get a valid JWT and User's Account ID
  def authenticate(self, secret):
    payload = { "method":"API-SECRET", "secret": secret }
    data = self.__post_to_api(url = 'login', payload = payload)
  
    self.jwt = data['jwt']
    self.account_id = data['user']['accountId']
  
    return {
      "account_id": self.account_id,
      "jwt": self.jwt
    }

  # Create a new project
  def create_project(self, name = 'auto-import-{0}'.format(int(time.time()))):
    payload = {'name': name}
    data = self.__post_to_api(url = 'v1/accounts/{0}/projects'.format(self.account_id),
     payload = payload,
     jwt = self.jwt)
  
    self.project_id = data['id']  
    return self.project_id

  def __detect_network(self, content):
    if ('facebook.com' in content):
      return 'facebook'
    elif ('twitter.com' in content):
      return 'twitter'
    elif ('youtube.com' in content):
      return 'youtube'
    elif ('instagram.com' in content):
      return 'instagram'
    else:
      raise Exception('Unsupported link: ' + content)

  # Add new profile
  def add_profile(self, profile):
    network = self.__detect_network(profile)
    url = 'v1/accounts/{0}/projects/{1}/{2}/profiles'.format(self.account_id, self.project_id, network)
    payload = {'url': profile}
    return self.__post_to_api(url, payload, self.jwt)
    
  def project_home_url(self):
    return 'https://quantum.socialmetrix.com/#/accounts/{0}/projects/{1}/facebook/profiles/'.format(self.account_id, self.project_id)
    
    
  # def delete_profile(self, profile):
  #   curl 'https://api.quantum.socialmetrix.com/v1/accounts/790/projects/15/instagram/profiles/INSTAGRAM_249105088' -X DELETE -H 'Origin: https://quantum.socialmetrix.com' -H 'Accept-Encoding: gzip, deflate, sdch' -H 'Accept-Language: en-US,en;q=0.8,es-419;q=0.6,es;q=0.4,pt-BR;q=0.2,pt;q=0.2' -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36' -H 'Content-Type: application/json' -H 'Accept: application/json, text/plain, */*' -H 'Referer: https://quantum.socialmetrix.com/' -H 'X-Auth-Token: eyJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJTTVgiLCJpYXQiOjE0NDYxNzA5MDIsImV4cCI6MTQ0Nzg5ODkwMiwicmVxdWVzdCI6eyJ1c2VySWQiOiI4MDZkNjQyYjRhNjFmYTA1NWE5MzdkOGY5ZDFiMjM0ZiIsIm1ldGhvZCI6IkZhY2Vib29rTG9naW4ifX0.R6ISgJiPSkFkiMj9cM4kYIkiA-iFbW1U_Yr7VWRGeiM' -H 'Connection: keep-alive' -H 'DNT: 1' --data-binary '{}' --compressed
  #
  #   curl 'https://api.quantum.socialmetrix.com/v1/accounts/790/projects/15/facebook/profiles/FACEBOOK_119679161426981' -X DELETE -H 'Origin: https://quantum.socialmetrix.com' -H 'Accept-Encoding: gzip, deflate, sdch' -H 'Accept-Language: en-US,en;q=0.8,es-419;q=0.6,es;q=0.4,pt-BR;q=0.2,pt;q=0.2' -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36' -H 'Content-Type: application/json' -H 'Accept: application/json, text/plain, */*' -H 'Referer: https://quantum.socialmetrix.com/' -H 'X-Auth-Token: eyJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJTTVgiLCJpYXQiOjE0NDYxNzA5MDIsImV4cCI6MTQ0Nzg5ODkwMiwicmVxdWVzdCI6eyJ1c2VySWQiOiI4MDZkNjQyYjRhNjFmYTA1NWE5MzdkOGY5ZDFiMjM0ZiIsIm1ldGhvZCI6IkZhY2Vib29rTG9naW4ifX0.R6ISgJiPSkFkiMj9cM4kYIkiA-iFbW1U_Yr7VWRGeiM' -H 'Connection: keep-alive' -H 'DNT: 1' --data-binary '{}' --compressed


def check_secret(secret):
  if(secret == None):
    secret = os.environ.get('QUANTUM_SECRET')
    if (secret == None):
      print("Secret must be defined. Please set a environment variable QUANTUM_SECRET or use the parameter --secret with your app secret")
      sys.exit(1)
  return secret


def add_profiles(file, project_id, secret):
  api = QuantumApi()
  
  print("Authenticating ...")
  api.authenticate(secret)
  
  if(project_id == None):
    print("Creating random project ...")
    project_id = api.create_project()
  else:
    print("Using passed project_id: {}".format(project_id))
    api.project_id = project_id

  for line in file:
    profile = line.rstrip('\r\n')
    print("\tAdding profile {0} to project {1}".format(profile, project_id))
    api.add_profile(profile)
  
  print("\n\nCheck the Project URL here: " + api.project_home_url())
  pass


def view_profiles(project_id, secret):
  print("App secret is {0}".format(secret))
  print("view_profiles from project: " + project_id)
  pass

def account_limits(secret):
  raise Exception('Not Implemented')
  pass

from sys import argv
import os, sys
import argparse

def main(argv):
  parser = argparse.ArgumentParser(description="Quantum Client Utility")
  parser.add_argument("--secret", help="set the secret id")

  subparsers = parser.add_subparsers(help='commands', dest='command')

  # A list command
  add_parser = subparsers.add_parser('add', help='Add profiles to a project')
  add_parser.add_argument("file", help="path for the file containing profiles to add", type=file)
  add_parser.add_argument("--project", help="the project id to insert", type=int)

  # A view command
  view_parser = subparsers.add_parser('view', help='View project profiles')
  view_parser.add_argument("project", help="project id")

  # A account limits command
  limit_parser = subparsers.add_parser('limits', help='Show account limits')

  try:
      args = parser.parse_args()
      secret = check_secret(args.secret)
      
      if (args.command == 'add'):
        add_profiles(args.file, args.project, secret)
        
      elif (args.command == 'view'):
        view_profiles(args.project, secret)
        
      elif (args.command == 'limits'):
        account_limits(secret)
      
  except IOError, msg:
    parser.error(str(msg))
    sys.exit(1)

if __name__ == "__main__":
  main(sys.argv)
