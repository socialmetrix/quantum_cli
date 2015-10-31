import quantum

def check_secret(secret):
  if(secret == None):
    secret = os.environ.get('QUANTUM_SECRET')
    if (secret == None):
      print("Secret must be defined. Please set a environment variable QUANTUM_SECRET or use the parameter --secret with your app secret")
      sys.exit(1)
  return secret

def add_profiles(file, project_id, secret):
  api = quantum.API()
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
  api = quantum.API()
  api.authenticate(secret)
  if(project_id == None):
    raise Exception('project_id must be provided')
  profiles = api.view_profiles(project_id)
  
  print('# profile_name: {}'.format(profiles['name']))
  print('#')
  for profile in profiles['brands']:
    print(profile['source']['url'])
  pass

def account_limits(secret):
  raise Exception('Not Implemented Yet')
  pass


###########################################################################
#
# Calling Main
#
from sys import argv
import os, sys
import argparse

def main(argv):
  parser = argparse.ArgumentParser(prog="quantum_cli", description="Quantum Client Utility")
  parser.add_argument("--secret", help="set the secret id")

  subparsers = parser.add_subparsers(help='commands', dest='command')

  # A list command
  add_parser = subparsers.add_parser('add', help='Add profiles to a project')
  add_parser.add_argument("file", help="path for the file containing profiles to add", type=file)
  add_parser.add_argument("--project", help="the project id to insert", type=int)

  # A view command
  view_parser = subparsers.add_parser('view', help='View profiles from a project')
  view_parser.add_argument("project", help="the id of the project you want to extract profiles")

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
