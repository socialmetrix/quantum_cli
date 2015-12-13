import requests
import json


class API:
    def __init__(self):
        self.jwt = None
        self.account_id = None
        self.project_id = None

    @staticmethod
    def __set_header(jwt):
        headers = {'Content-Type': 'application/json'}
        if jwt is not None:
            headers['X-Auth-Token'] = jwt
        return headers

    def __get_from_api(self, url, params, jwt=None):
        headers = self.__set_header(jwt)
        target_url = 'https://api.quantum.socialmetrix.com/{0}'.format(url)
        r = requests.get(target_url, params=params, headers=headers)
        result = r.json()
        if 200 <= r.status_code < 300:
            return result
        else:
            raise Exception('Error: ' + json.dumps(result))

    def __post_to_api(self, url, payload, jwt=None):
        headers = self.__set_header(jwt)
        r = requests.post('https://api.quantum.socialmetrix.com/{0}'.format(url), data=json.dumps(payload),
                          headers=headers)
        result = r.json()
        if 200 <= r.status_code < 300:
            return result
        else:
            raise Exception('Error: ' + json.dumps(result))

    def __delete_from_api(self, url, payload=None, jwt=None):
        headers = self.__set_header(jwt)
        target_url = 'https://api.quantum.socialmetrix.com/{0}'.format(url)
        r = requests.delete(target_url, params=payload, data="{}", headers=headers)
        if not (200 <= r.status_code < 300):
            raise Exception('Error: ' + r.text)
        pass

    def __get_project_id(self, project_id):
        if project_id is None and self.project_id is None:
            raise Exception('project_id must be provided')

        elif project_id is None and self.project_id is not None:
            return self.project_id

        else:
            return project_id

    @staticmethod
    def __required(value, message=None):
        if value is None:
            if message is None:
                raise Exception("value can't be None")
            else:
                raise Exception(message)

    # Login / Get a valid JWT and User's Account ID
    def authenticate(self, secret):
        payload = {"method": "API-SECRET", "secret": secret}
        data = self.__post_to_api(url='login', payload=payload)

        self.jwt = data['jwt']
        self.account_id = data['user']['accountId']

        return {
            "account_id": self.account_id,
            "jwt": self.jwt
        }

    # Create a new project
    def create_project(self, name):
        payload = {'name': name}
        data = self.__post_to_api(url='v1/accounts/{0}/projects'.format(self.account_id),
                                  payload=payload,
                                  jwt=self.jwt)

        self.project_id = data['id']
        return self.project_id

    def list_projects(self):
        url = 'v1/accounts/{}/projects'.format(self.account_id)
        data = self.__get_from_api(url, None, self.jwt)
        return data

    @staticmethod
    def __detect_network(content):
        if 'facebook.com' in content or 'FACEBOOK_' in content:
            return 'facebook'
        elif 'twitter.com' in content or 'TWITTER_' in content:
            return 'twitter'
        elif 'youtube.com' in content or 'YOUTUBE_' in content:
            return 'youtube'
        elif 'instagram.com' in content or 'INSTAGRAM_' in content:
            return 'instagram'
        else:
            raise Exception('Unsupported link: ' + content)

    # Add new profile
    def add_profile(self, profile):
        network = self.__detect_network(profile)
        url = 'v1/accounts/{0}/projects/{1}/{2}/profiles'.format(self.account_id, self.project_id, network)
        payload = {'url': profile}
        return self.__post_to_api(url, payload, self.jwt)

    def view_profiles(self, project_id=None):
        project_id = self.__get_project_id(project_id)

        url = 'v1/accounts/{0}/projects/{1}'.format(self.account_id, project_id)
        return self.__get_from_api(url, None, self.jwt)

    def delete_profile(self, profile_id, project_id=None):
        project_id = self.__get_project_id(project_id)

        network = self.__detect_network(profile_id)
        url = 'v1/accounts/{0}/projects/{1}/{2}/profiles/{3}'.format(self.account_id, project_id, network, profile_id)
        self.__delete_from_api(url, jwt=self.jwt)
        pass

    def delete_project(self, project_id=None):
        project_id = self.__get_project_id(project_id)

        url = 'v1/accounts/{0}/projects/{1}'.format(self.account_id, project_id)
        self.__delete_from_api(url, jwt=self.jwt)
        pass

    def project_home_url(self):
        return 'https://quantum.socialmetrix.com/#/accounts/{0}/projects/{1}/facebook/profiles/'.format(self.account_id,
                                                                                                        self.project_id)

    def users(self):
        url = 'v1/accounts/{}/users'.format(self.account_id)
        return self.__get_from_api(url, None, self.jwt)

    # def campaign_posts(self, project_id = None, since = None, until = None, campaign_id = None, offset = 10, limit = 10):
    #   project_id = self.__get_project_id(project_id)
    #   self.__required(since, "since is not set")
    #   self.__required(until, "until is not set")
    #
    #   url = 'v1/accounts/{}/projects/{}/facebook/campaigns/{}/posts'.format(
    #     self.account_id,
    #     project_id,
    #     campaign_id)
    #
    #   params = {
    #     'since': since,
    #     'until': until,
    #     'offset': offset,
    #     'limit': limit
    #   }
    #
    #   return self.__get_from_api(url, params, self.jwt)

    def facebook_posts(self, project_id=None, profile=None, since=None, until=None, limit=10):
        project_id = self.__get_project_id(project_id)
        self.__required(profile, "profile is not set")
        self.__required(since, "since is not set")
        self.__required(until, "until is not set")

        url = 'v1/accounts/{}/projects/{}/facebook/profiles/{}/posts'.format(
            self.account_id,
            project_id,
            profile)

        # TODO: Implement field => offset:{"datetime":"2015-11-28T11:02:05-02:00","entity":"125812234121863_904218426281236"}
        # TODO: Implement field owner (admin or user)
        # TODO: Implement field type (status,link,video,photo)
        params = {
            'since': since,
            'until': until,
            'limit': limit,
            'owner': 'admin',
            'type': 'status,link,video,photo'
        }

        return self.__get_from_api(url, params, self.jwt)

    def facebook_posts_stats(self, project_id=None, since=None, until=None, *profiles):

        url = 'v1/accounts/{}/projects/{}/facebook/profiles/posts-interactions/count/date'.format(
            self.account_id,
            project_id)

        ids = ','.join(list(profiles))

        params = {
            'since': since,
            'until': until,
            'ids': ids
        }

        return self.__get_from_api(url, params, self.jwt)
