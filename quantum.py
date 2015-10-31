import requests, json
import time

class API():
  def __init__(self):
    self.jwt = None
    self.account_id = None
    self.project_id = None
    
  def __set_header(self, jwt = None):
    headers = {'Content-Type': 'application/json'}
    if (jwt != None):
      headers['X-Auth-Token']=jwt
    return headers
  
  def __get_from_api(self, url, payload, jwt = None):
    headers = self.__set_header(jwt)
    dest_url = 'https://api.quantum.socialmetrix.com/{0}'.format(url)
    r = requests.get(dest_url, params=payload, headers=headers)
    result = r.json()
    if(r.status_code >= 200 and r.status_code < 300):
      return result
    else:
      raise Exception('Error: ' + json.dumps(result))

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
    
  def view_profiles(self, project_id = None):
    if(project_id == None and self.project_id == None):
      raise Exception('project_id must be provided')

    elif (project_id == None and self.project_id != None):
      project_id = self.project_id

    url = 'v1/accounts/{0}/projects/{1}'.format(self.account_id, project_id)
    return self.__get_from_api(url, None, self.jwt)

  def project_home_url(self):
    return 'https://quantum.socialmetrix.com/#/accounts/{0}/projects/{1}/facebook/profiles/'.format(self.account_id, self.project_id)