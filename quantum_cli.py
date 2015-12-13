#!/usr/bin/env python
# -*- coding: utf8 -*-

import argparse
import csv
import os
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
    parser.add_argument("--secret", help="set the secret id")
    parser.add_argument("--csv", help="Switch output to CSV format", action="store_true")

    subparsers = parser.add_subparsers(help='commands', dest='command')

    # ADD PROFILE command
    add_parser = subparsers.add_parser('add', help='Add profiles to a project')
    add_parser.add_argument("file", help="path for the file containing profiles to add", type=file)
    add_parser.add_argument("--project", help="the project id to insert", type=int)

    # VIEW PROFILES command
    view_parser = subparsers.add_parser('view', help='View profiles from a project')
    view_parser.add_argument("project", help="the id of the project you want to extract profiles", type=int)

    # VIEW PROJECTS command
    subparsers.add_parser('view-projects', help='Show active projects')

    # DELETE PROJECT command
    delete_parser = subparsers.add_parser('delete-project', help='Delete a project including all profiles')
    delete_parser.add_argument("project", help="the id of the project you want to delete", type=int)

    # ACCOUNT LIMITS command
    subparsers.add_parser('limits', help='Show account limits')

    # USERS ON ACCOUNT command
    subparsers.add_parser('users', help='Show users on the account')

    # Listing posts of a campaign
    # campaign_posts_parser = subparsers.add_parser('campaign-posts', help="Show posts that belongs to the campaign")
    # campaign_posts_parser.add_argument("project_id", help='Project ID that contains the campaign', type=int)
    # campaign_posts_parser.add_argument("campaign_id", help='Campaign ID', type=int)
    # campaign_posts_parser.add_argument("since", help='Begin of date range, format: YYYY-MM-DD')
    # campaign_posts_parser.add_argument("until", help='End of date range, format: YYYY-MM-DD')
    # campaign_posts_parser.add_argument("--offset", help='Offset from the beginning of the list. Default: 0', type=int, default=0)
    # campaign_posts_parser.add_argument("--limit", help='Quantity of records returned on each command. Default: 10', type=int,  default=10)

    # Listing Posts from a Social Network
    posts_parser = subparsers.add_parser('posts', help="Show posts that belongs to a profile (account)")
    posts_parser.add_argument("project_id", help='Project ID that contains the profile', type=int)
    posts_parser.add_argument("profile_id", help='Profile ID is the ID of a fan page or account')
    posts_parser.add_argument("since", help='Begin of date range, format: YYYY-MM-DD')
    posts_parser.add_argument("until", help='End of date range, format: YYYY-MM-DD')
    posts_parser.add_argument("--limit", help='Quantity of records returned on each command. Default: 10', type=int,
                              default=10)

    try:
        args = parser.parse_args()
        secret = check_secret(args.secret)

        if args.csv:
            global output_format
            output_format = "csv"

        if args.command == 'add':
            add_profiles(args.file, args.project, secret)

        elif args.command == 'view':
            view_profiles(args.project, secret)

        elif args.command == 'view-projects':
            view_projects(secret)

        elif args.command == 'delete-project':
            delete_project(args.project, secret)

        elif args.command == 'limits':
            account_limits(secret)

        elif args.command == 'users':
            account_users(secret)

        # elif (args.command == 'campaign-posts'):
        #   campaign_posts(secret = secret,
        #                  project_id = args.project_id,
        #                  since = args.since,
        #                  until = args.until,
        #                  campaign_id = args.campaign_id,
        #                  offset = args.offset,
        #                  limit = args.limit)

        elif args.command == 'posts':
            posts(secret=secret,
                  project_id=args.project_id,
                  profile_id=args.profile_id,
                  since=args.since,
                  until=args.until,
                  limit=args.limit)

    except IOError, msg:
        parser.error(str(msg))
        sys.exit(1)


################
#
#
#
def p(content):
    print unicode(content).encode("utf-8")


def output(headers, data, mode="table"):
    if mode == "table":
        p(tabulate(data, headers))

    else:
        writer = csv.writer(sys.stdout)
        writer.writerows([headers])
        for line in data:
            writer.writerows([[unicode(item).encode('utf-8') for item in line]])


def check_secret(secret):
    if secret is None:
        secret = os.environ.get('QUANTUM_SECRET')
        if secret is None:
            p("Secret must be defined." +
              "Please set a environment variable QUANTUM_SECRET or use the parameter --secret with your app secret")
            sys.exit(1)
    return secret


def add_profiles(filename, project_id, secret):
    api = quantum.API()
    api.authenticate(secret)

    if project_id is None:
        p("Creating random project ...")
        project_id = api.create_project(name='quantum_cli-{0}'.format(int(time.time())))
    else:
        p("Using passed project_id: {}".format(project_id))
        api.project_id = project_id

    for line in filename:
        profile = line.rstrip('\r\n')
        if profile.startswith('http'):
            p("\tAdding profile {0} to project {1}".format(profile, project_id))
            api.add_profile(profile)

    p("\n\nCheck the Project URL here: " + api.project_home_url())
    pass


def view_profiles(project_id, secret):
    api = quantum.API()
    api.authenticate(secret)
    if project_id is None:
        raise Exception('project_id must be provided')
    profiles = api.view_profiles(project_id)
    p(u'# profile_name: {}'.format(profiles['name']))
    p('#')
    for profile in profiles['brands']:
        p(profile['source']['url'])
    pass


def account_limits(secret):
    raise Exception('Not Implemented Yet')
    pass


def delete_project(project_id, secret):
    api = quantum.API()
    api.authenticate(secret)
    if project_id is None:
        raise Exception('project_id must be provided')

    # Deleting profiles
    profiles = api.view_profiles(project_id)
    for profile in profiles['brands']:
        p(u'Deleting profile {} ({})'.format(profile['source']['url'], profile['name']))
        api.delete_profile(profile_id=profile['id'], project_id=project_id)

    # Deleting project
    api.delete_project(project_id=project_id)
    pass


def view_projects(secret):
    api = quantum.API()
    api.authenticate(secret)
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


def account_users(secret):
    api = quantum.API()
    api.authenticate(secret)
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


# def campaign_posts(secret, project_id = None, since = None, until = None, campaign_id = None, offset = 10, limit = 10):
#   api = quantum.API()
#   api.authenticate(secret)
#   campaigns = api.campaign_posts(project_id, since, until, campaign_id, offset, limit)
#
#   headers = ['post_id', 'created_time', 'likes', 'comments', 'shares', 'interactions', 'engagement_rate']
#   data = []
#   for camp in campaigns['results']:
#     data.append([
#       camp['id'],
#       camp['createdTime'],
#       camp['stats']['likes'],
#       camp['stats']['comments'],
#       camp['stats']['shares'],
#       camp['stats']['interactions'],
#       camp['stats']['engagementRate']
#     ])
#
#   output(headers, data, output_format)
#   pass


def posts(secret, project_id=None, profile_id=None, since=None, until=None, limit=10):
    api = quantum.API()
    api.authenticate(secret)
    posts_data = api.facebook_posts(project_id, profile_id, since, until, limit)

    # Getting posts metadata
    posts_metadata = {}
    for post in posts_data['results']:
        campaign_info = post['campaignInfo']
        if campaign_info is None:
            campaign_id = ''
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


#####
# CALL MAIN
#

if __name__ == "__main__":
    main()
