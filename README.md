# Socialmetrix Quantum Client Utility
This project contains a few useful functions to manage your Quantum's instance

## Install
```bash
git clone https://github.com/socialmetrix/quantum_cli.git
cd quantum_cli/

# if you use PIP
pip install -r requirements.txt

# if you use Anaconda
conda env create -f environment.yml
source activate quantum_cli
```

You must provide your API Secret in order to use this tool.
You can set it using `--secret` or setting an environment variable `QUANTUM_SECRET`, for example adding this line to your `.bashrc`:

```bash
export QUANTUM_SECRET=0220a22d27be69efffffffff54aa9840e5c4136e
```

## Usage
```
usage: quantum_cli [-h] [--secret SECRET] [--csv] [--api-url API_URL]
                   {add,view-projects,delete-project,limits,users,posts,view-profiles}
                   ...

Quantum Client Utility

positional arguments:
  {add,view-projects,delete-project,limits,users,posts,view-profiles}
                        commands
    add                 Add profiles to a project
    view-projects       Show active projects
    delete-project      Delete a project including all profiles
    limits              Show account limits
    users               Show users on the account
    posts               Show posts that belongs to a profile (account)
    view-profiles       Show profiles (accounts) with statistics from a
                        project

optional arguments:
  -h, --help            show this help message and exit
  --secret SECRET       set the api secret
  --csv                 Switch output to CSV format
  --api-url API_URL     Change the default api url
```

## Quantum_API module
You can use [quantum.py](quantum.py) on your own programs.

**IMPORTANT:** this is beta code, the module API is been heavily developed and interfaces may change.

### Usage
```python
import os, quantum
# import imp
# imp.reload(quantum)

# reading secret from env
secret = os.environ.get('QUANTUM_SECRET')

api = quantum.API()
api.authenticate(secret)

# profiles = api.view_profiles(23)

projects = api.list_projects()
# Sort projects by name
projects_sorted = sorted(projects, key=lambda project: project['name'])

for project in projects_sorted:
  print(project['name'], project['id'])

posts = api.facebook_posts(24, '122531974426912', '2015-11-01', '2015-11-30', limit=5)

for post in posts['results']:
  print(post['id'])

pages_stats = api.facebook_pages_stats(25, '2015-11-01', '2015-11-30', '179903722029183', '178297347303')
for stats in pages_stats['results']:
    print(stats['data']['current'])

# invite a user to project(s)
api.invite_user('email@address.net', 'ANALYST', 25, 14, 16)


# remove users from projects
users = api.users()
project_id = 43
user_ids = list(user['id'] for user in users if project_id in user['projectIds'])

for id in user_ids:
  print(id)
  api.delete_user(id)



```

## Usage Examples

### Obtain posts stats
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

### Obtain posts stats (as CSV)
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
