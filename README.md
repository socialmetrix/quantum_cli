# Socialmetrix Quantum Client Utility
This project contains a few useful functions to manage your Quantum's instance

##Usage
```
usage: quantum_cli [-h] [--secret SECRET] {add,delete-project,limits,view} ...

Quantum Client Utility

positional arguments:
  {add,delete-project,limits,view}
                        commands
    add                 Add profiles to a project
    view                View profiles from a project
    delete-project      Delete profiles from a project
    limits              Show account limits

optional arguments:
  -h, --help            show this help message and exit
  --secret SECRET       set the secret id
```


##Quantum_API module

###Usage
```
import os, quantum

#reading secret from env
secret = os.environ.get('QUANTUM_SECRET')

api = quantum.API()
api.authenticate(secret)

projects = api.list_projects()

campaigns = api.campaign_posts(project_id=24, 
  since='2015-11-01', 
  until='2015-11-30', 
  campaign_id=549)

for campaign in campaigns['results']:
  print campaign['id']
```
