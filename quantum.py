import json

import requests


class API:
    def __init__(self, api_url=None, ui_url=None):
        self.jwt = None
        self.account_id = None
        self.project_id = None
        if api_url is None:
            self.api_url = 'https://api.quantum.socialmetrix.com/v1'
        else:
            self.api_url = api_url
        if ui_url is None:
            self.ui_url = 'https://quantum.socialmetrix.com'
        else:
            self.ui_url = ui_url

    @staticmethod
    def __set_header(jwt):
        headers = {'Content-Type': 'application/json'}
        if jwt is not None:
            headers['X-Auth-Token'] = jwt
        return headers

    def __build_api_url(self, url):
        return '{0}/{1}'.format(self.api_url, url)

    def __get_from_api(self, url, params=None, jwt=None):
        headers = self.__set_header(jwt)
        r = requests.get(self.__build_api_url(url), params=params, headers=headers)
        result = r.json()
        if 200 <= r.status_code < 300:
            return result
        else:
            print("WARN: " + json.dumps(result))
            return {}

    def __post_to_api(self, url, payload, jwt=None):
        headers = self.__set_header(jwt)
        r = requests.post(self.__build_api_url(url), data=json.dumps(payload),
                          headers=headers)
        result = r.json()
        if 200 <= r.status_code < 300:
            return result
        else:
            print("WARN: " + json.dumps(result))
            return {}

    def __delete_from_api(self, url, payload=None, jwt=None):
        headers = self.__set_header(jwt)
        r = requests.delete(self.__build_api_url(url), params=payload, data="{}", headers=headers)
        if not (200 <= r.status_code < 300):
            print("WARN: " + r.text)
            return {}
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
        data = self.__post_to_api(url='accounts/{0}/projects'.format(self.account_id),
                                  payload=payload,
                                  jwt=self.jwt)

        self.project_id = data['id']
        return self.project_id

    def list_projects(self):
        url = 'accounts/{}/projects'.format(self.account_id)
        return self.__get_from_api(url, None, self.jwt)

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
        url = 'accounts/{0}/projects/{1}/{2}/profiles'.format(self.account_id, self.project_id, network)
        payload = {'url': profile}
        return self.__post_to_api(url, payload, self.jwt)

    def view_profiles(self, project_id=None):
        project_id = self.__get_project_id(project_id)

        url = 'accounts/{0}/projects/{1}'.format(self.account_id, project_id)
        return self.__get_from_api(url, None, self.jwt)

    def delete_profile(self, profile_id, project_id=None):
        project_id = self.__get_project_id(project_id)

        network = self.__detect_network(profile_id)
        url = 'accounts/{0}/projects/{1}/{2}/profiles/{3}'.format(self.account_id, project_id, network, profile_id)
        self.__delete_from_api(url, jwt=self.jwt)
        pass

    def delete_project(self, project_id=None):
        project_id = self.__get_project_id(project_id)

        url = 'accounts/{0}/projects/{1}'.format(self.account_id, project_id)
        self.__delete_from_api(url, jwt=self.jwt)
        pass

    def project_home_url(self):
        return '{0}/#/accounts/{1}/projects/{2}/facebook/profiles/'.format(self.ui_url, self.account_id,
                                                                           self.project_id)

    def facebook_posts(self, project_id=None, profile=None, since=None, until=None, limit=10):
        project_id = self.__get_project_id(project_id)
        self.__required(profile, "profile is not set")
        self.__required(since, "since is not set")
        self.__required(until, "until is not set")

        url = 'accounts/{}/projects/{}/facebook/profiles/{}/posts'.format(
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
        p_id = self.__get_project_id(project_id)
        self.__required(since, "since is not set")
        self.__required(until, "until is not set")

        # if len(profiles) == 0:

        url = 'accounts/{}/projects/{}/facebook/profiles/posts-interactions/count/date'.format(
            self.account_id,
            p_id)

        ids = ','.join(list(profiles))

        params = {
            'since': since,
            'until': until,
            'ids': ids
        }

        return self.__get_from_api(url, params, self.jwt)

    def pages_stats(self, project_id=None, network='facebook', since=None, until=None, *profiles):
        project_id = self.__get_project_id(project_id)
        self.__required(since, "since is not set")
        self.__required(until, "until is not set")

        url = 'accounts/{}/projects/{}/{}/profiles/stat-summary'.format(
            self.account_id,
            project_id,
            network.lower())

        ids = ','.join(list(profiles))

        params = {
            'since': since,
            'until': until,
            'ids': ids
        }

        return self.__get_from_api(url, params, self.jwt)

    def users(self):
        url = 'accounts/{}/users'.format(self.account_id)
        return self.__get_from_api(url, jwt=self.jwt)

    def invite_user(self, email, first_name, last_name, role='MANAGER', projects=list()):
        if role == 'ANALYST' and len(projects) == 0:
            raise Exception("ANALYST role needs to be invited to at least one project")

        payload = {'accountId': self.account_id, 'email': email,
                   'firstName': first_name, 'lastName': last_name,
                   'role': role, 'projectIds': projects}
        data = self.__post_to_api(url='accounts/{0}/users'.format(self.account_id),
                                  payload=payload,
                                  jwt=self.jwt)
        return data

    def delete_user(self, user_id):
        url = 'accounts/{0}/users/{1}'.format(self.account_id, user_id)
        return self.__delete_from_api(url=url, jwt=self.jwt)
