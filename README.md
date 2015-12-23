# Socialmetrix Quantum Client Utility
This project contains a few useful functions to manage your Quantum's instance

##Usage
```
usage: quantum_cli [-h] [--secret SECRET] [--csv]
                   {add,view,view-projects,delete-project,limits,users,posts}
                   ...

Quantum Client Utility

positional arguments:
  {add,view,view-projects,delete-project,limits,users,posts}
                        commands
    add                 Add profiles to a project
    view                View profiles from a project
    view-projects       Show active projects
    delete-project      Delete a project including all profiles
    limits              Show account limits
    users               Show users on the account
    posts               Show posts that belongs to a profile (account)

optional arguments:
  -h, --help            show this help message and exit
  --secret SECRET       set the secret id
  --csv                 Switch output to CSV format
```

##Quantum_API module
You can use [quantum.py](quantum.py) on your own programs.

**IMPORTANT:** this is beta code, the module API is been heavily developed and interfaces may change.

###Usage
```
import os, quantum
# reload(quantum)

#reading secret from env
secret = os.environ.get('QUANTUM_SECRET')

api = quantum.API()
api.authenticate(secret)


profiles = api.view_profiles(23)


projects = api.list_projects()
for project in projects:
  print project['name']

posts = api.facebook_posts(24, '122531974426912', '2015-11-01', '2015-11-30', limit=5)

for post in posts['results']:
  print post['id']


pages_stats = api.facebook_pages_stats(25, '2015-11-01', '2015-11-30', '179903722029183', '178297347303')
for stats in pages_stats['results']:
    print stats['data']['current']
    
# invite a user to project(s)
api.invite_user('email@address.net', 'ANALYST', 25, 14, 16)

```

##Usage Examples

###Obtain posts stats
```
quantum_cli posts <project_id> <profile_id> <since> <until> [--limit]
  
quantum_cli posts 24 122531974426912 2015-11-01 2015-11-30 --limit 5

post_id                           created_time                 likes    comments    shares    interactions    engagement_rate  campaign_id    campaign_name
--------------------------------  -------------------------  -------  ----------  --------  --------------  -----------------  -------------  ---------------
122531974426912_1189775121035920  2015-11-30T20:41:00-02:00       37           1         2              40        0.000132063
122531974426912_1189773174369448  2015-11-30T17:37:01-02:00       45           1         6              52        0.000171682
122531974426912_1189747191038713  2015-11-30T10:43:00-02:00      192          24       104             320        0.0010565
122531974426912_1189779494368816  2015-11-29T18:12:00-02:00      691          59       134             884        0.00291859   549            Is Sponsored
122531974426912_1189594487720650  2015-11-30T11:13:00-02:00      286          12        65             363        0.00119847
````

###Obtain posts stats (as CSV)
Any command that outputs information, also accepts the parameter `--csv`. Running the above command with this parameter will output:
```
quantum_cli --csv posts 24 122531974426912 2015-11-01 2015-11-30 --limit 5

post_id,created_time,likes,comments,shares,interactions,engagement_rate,campaign_id,campaign_name
122531974426912_1189775121035920,2015-11-30T20:41:00-02:00,37,1,2,40,0.000132063,,
122531974426912_1189773174369448,2015-11-30T17:37:01-02:00,45,1,6,52,0.0001716819,,
122531974426912_1189747191038713,2015-11-30T10:43:00-02:00,192,24,104,320,0.001056504,,
122531974426912_1189779494368816,2015-11-29T18:12:00-02:00,691,59,134,884,0.0029185922,549,Is Sponsored
122531974426912_1189594487720650,2015-11-30T11:13:00-02:00,286,12,65,363,0.0011984718,,
```

