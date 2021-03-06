#!/usr/bin/env python
# -*- coding: utf8 -*-

import argparse
import csv
import os
import re
import sys
import time

from tabulate import tabulate

import quantum

###
# Global Var to hold the output format
#
output_format = "table"


###########################################################################
#
#

def main():
    parser = argparse.ArgumentParser(prog="quantum_cli", description="Quantum Client Utility")
    parser.add_argument("--secret", help="set the api secret")
    parser.add_argument("--csv", help="Switch output to CSV format", action="store_true")
    parser.add_argument("--api-url", help="Change the default api url. eg: http://localhost/api/v1")

    subparsers = parser.add_subparsers(help='commands', dest='command')

    # ADD PROFILE command
    add_parser = subparsers.add_parser('add', help='Add profiles to a project')
    add_parser.add_argument("file", help="path for the file containing profiles to add", type=argparse.FileType('R'))
    add_parser.add_argument("--project", help="the project id to insert", type=int)
    add_parser.add_argument("--project-name", help="use the given name when creating a new project")

    # VIEW PROFILES command
    # view_parser = subparsers.add_parser('view', help='View profiles from a project')
    # view_parser.add_argument("project", help="the id of the project you want to extract profiles", type=int)

    # VIEW PROJECTS command
    subparsers.add_parser('view-projects', help='Show active projects')

    # DELETE PROJECT command
    delete_parser = subparsers.add_parser('delete-project', help='Delete a project including all profiles')
    delete_parser.add_argument("project", help="the id of the project you want to delete", type=int)

    # ACCOUNT LIMITS command
    subparsers.add_parser('limits', help='Show account limits')

    # USERS ON ACCOUNT command
    subparsers.add_parser('users', help='Show users on the account')

    # Listing Posts from a Social Network
    posts_parser = subparsers.add_parser('posts', help="Show posts that belongs to a profile (account)")
    posts_parser.add_argument("project_id", help='Project ID that contains the profile', type=int)
    posts_parser.add_argument("profile_id", help='Profile ID is the ID of a fan page or account')
    posts_parser.add_argument("since", help='Begin of date range, format: YYYY-MM-DD')
    posts_parser.add_argument("until", help='End of date range, format: YYYY-MM-DD')
    posts_parser.add_argument("--limit", help='Quantity of records returned on each command. Default: 10', type=int,
                              default=10)

    # Listing Pages with Stats from a Social Network
    view_profiles_parser = subparsers.add_parser('view-profiles',
                                                 help="Show profiles (accounts) with statistics from a project")
    view_profiles_parser.add_argument("project_id", help='Project ID that contains the profile', type=int)
    view_profiles_parser.add_argument("since", help='Begin of date range, format: YYYY-MM-DD')
    view_profiles_parser.add_argument("until", help='End of date range, format: YYYY-MM-DD')

    try:
        if len(sys.argv) == 1:
            parser.print_help()
            sys.exit(1)

        args = parser.parse_args()
        api = build_api(args.secret, args.api_url)

        if args.csv:
            global output_format
            output_format = "csv"

        if args.command == 'add':
            add_profiles(api, args.file, args.project, args.project_name)

        # elif args.command == 'view':
        #     view_profiles(args.project, secret)

        elif args.command == 'view-projects':
            view_projects(api)

        elif args.command == 'delete-project':
            delete_project(api, args.project)

        elif args.command == 'limits':
            account_limits(api)

        elif args.command == 'users':
            account_users(api)

        elif args.command == 'posts':
            posts(api=api,
                  project_id=args.project_id,
                  profile_id=args.profile_id,
                  since=args.since,
                  until=args.until,
                  limit=args.limit)

        elif args.command == 'view-profiles':
            profiles_from_project(api=api,
                                  project_id=args.project_id,
                                  since=args.since,
                                  until=args.until)

    except Exception as msg:
        parser.error(msg)
        sys.exit(1)


################
#
#
#

def output(headers, data, mode="table"):
    if mode == "table":
        print(tabulate(data, headers))

    else:
        writer = csv.writer(sys.stdout)
        writer.writerows([headers])
        for line in data:
            writer.writerows([[item for item in line]])


def build_api(secret, api_url):
    if secret is None:
        secret = os.environ.get('QUANTUM_SECRET')
        if secret is None:
            print("Secret must be defined." +
                  "Please set a environment variable QUANTUM_SECRET or use the parameter --secret with your app secret")
            sys.exit(1)
    api = quantum.API(api_url)
    api.authenticate(secret)
    return api


def add_profiles(api, filename, project_id, project_name=None):
    if not project_name:
        project_name = 'quantum_cli-{0}'.format(int(time.time()))

    if project_id is None:
        print("Creating project ... {}".format(project_name))
        project_id = api.create_project(name=project_name)

    else:
        print("Using passed project_id: {}".format(project_id))
        api.project_id = project_id

    for line in filename:
        profile = line.rstriprint('\r\n')
        if profile.startswith('http'):
            print("\tAdding profile {0} to project {1}".format(profile, project_id))
            api.add_profile(profile)

    print("\n\nCheck the Project URL here: " + api.project_home_url())
    pass


def __extract_username_from_instagram_url(url):
    p = re.compile(r'https://(www\.)?instagram\.com/([^/]+)')
    m = p.match(url)
    if m:
        return m.grouprint(2)
    else:
        return None


def __extract_username_name_from_profile(profile):
    source = profile['sourceType']
    if source == 'FACEBOOK':
        return profile['username'], profile['name']
    elif source == 'TWITTER':
        return profile['screenName'], profile['name']
    elif source == 'YOUTUBE':
        # TODO: FIX API. It is not exposing username
        return '', profile['name']
    elif source == 'INSTAGRAM':
        # TODO: FIX API. It is not exposing username
        username = __extract_username_from_instagram_url(profile['source']['url'])
        return username, profile['name']
    else:
        raise Exception('Unsupported source: ' + source)


def account_limits(api):
    raise Exception('Not Implemented Yet')
    pass


def delete_project(api, project_id):
    if project_id is None:
        raise Exception('project_id must be provided')

    # Deleting profiles
    profiles = api.view_profiles(project_id)
    for profile in profiles['brands']:
        print(u'Deleting profile {} ({})'.format(profile['source']['url'], profile['name']))
        api.delete_profile(profile_id=profile['id'], project_id=project_id)

    # Deleting project
    api.delete_project(project_id=project_id)
    pass


def view_projects(api):
    projects = api.list_projects()

    headers = ['id', 'name', 'qty_of_profiles']
    data = []
    for project in projects:
        data.append([
            project['id'],
            project['name'],
            len(project['brands'])
        ])

    output(headers, data, output_format)
    pass


def account_users(api):
    users = api.users()

    headers = ['name', 'email', 'role', 'last_login']
    data = []
    for user in users:
        data.append([
            user['firstName'] + ' ' + user['lastName'],
            user['email'],
            user['role'],
            user['lastLogin']
        ])

    output(headers, data, output_format)
    pass


def posts(api, project_id=None, profile_id=None, since=None, until=None, limit=10):
    posts_data = api.facebook_posts(project_id, profile_id, since, until, limit)

    # Getting posts metadata
    posts_metadata = {}
    for post in posts_data['results']:
        campaign_info = post['campaignInfo']
        if campaign_info is None:
            campaign_id = 0
            campaign_name = ''
        else:
            campaign_id = campaign_info['campaign']['id']
            campaign_name = campaign_info['campaign']['name']

        posts_metadata[post['id']] = [
            post['createdTime'],
            campaign_id,
            campaign_name
        ]

    # Getting posts stats
    posts_ids = posts_metadata.keys()
    stats = api.facebook_posts_stats(project_id, since, until, *posts_ids)

    stats_data = {}
    for stat in stats['results']:
        values = stat['currentTotal']

        stats_data[stat['id']] = [
            values['likes'],
            values['comments'],
            values['shares'],
            values['interactions'],
            values['engagementRate']
        ]

    # Joining posts metadata with posts stats
    data = []
    for post_id, post_metadata in posts_metadata.iteritems():
        data.append(
            # Build the line with relevant information, split the post_metadata array,
            # leaving campaign info to the end of line
            [post_id] + post_metadata[:1] + stats_data[post_id] + post_metadata[1:]
        )

    headers = ['post_id', 'created_time', 'likes', 'comments', 'shares', 'interactions', 'engagement_rate',
               'campaign_id', 'campaign_name']
    output(headers, data, output_format)
    pass


def profiles_from_project(api, project_id=None, since=None, until=None):
    """Create a table containing profiles with statistics from a project"""
    profiles = api.view_profiles(project_id)

    data = []
    profiles_metadata = {}
    for profile in profiles['brands']:
        source = profile['sourceType']

        if not profiles_metadata.has_key(source):
            profiles_metadata[source] = {}

        username, name = __extract_username_name_from_profile(profile)
        profile_id = profile['source']['id']

        profiles_metadata[source][profile_id] = [
            profile['sourceType'],
            profile['source']['id'],
            profile['source']['url'],
            username,
            name
        ]

    for source in profiles_metadata.keys():
        ids = profiles_metadata[source].keys()
        stats = api.pages_stats(project_id, source, since, until, *ids)

        for stat in stats['results']:
            metrics = stat['data']['current']

            if source == 'FACEBOOK' or source == 'INSTAGRAM':
                metric = metrics['totalFans']
            elif source == 'TWITTER':
                metric = metrics['totalFollowers']
            else:
                metric = metrics['totalSubscribers']

            data.append(profiles_metadata[source][stat['id']] + [metric])

    headers = ['kind', 'page_id', 'url', 'username', 'name', 'community_count']
    output(headers, data, output_format)
    pass


#####
# CALL MAIN
#

if __name__ == "__main__":
    main()
