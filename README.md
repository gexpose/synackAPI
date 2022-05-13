# Library for interacting with Synack API 
This is a library and set of scripts that make SRT life a little easier when interacting with the platform from a linux commandline.
* Connect to platform
  * Stay connected to the platform
* Register available targets
* Connect to targets
* Download targets' scope
* Retrieve analytics from `Web Application` and `Host` targets
* Download hydra findings
* Retrieve target specific information:
  * Client names
  * Codenames
  * Slugs
  * Target types
* Enable mission-claiming bots
* Manage notifications

# Acknowledgements
Thank you Malcolm, Nicolas, and pmnh for making this better!

# Configuration requirements 
## Operating System
This has been developed on Linux. I have no idea if it will work on Windows. It might, but your mileage may vary. I do not use windows. If you do, and you want to test, please do. 

## Configuration Directories
The required directory is `~/.synack`.

## synack.conf
This is a required config file, and is expected to be in the directory ~/.synack/
```
[DEFAULT]
login_wait = 15
login_url = https://login.synack.com
email = your.email@domain.tld
password = your.synack.password
authy_secret = ABCDEFGHIJKLMNOPQRSTUVWXYZ======
webhook_url = https://hooks.slack.com/services/...
```
* login_wait
  * Number of seconds to wait for the platform's website to be loaded before attempting to log in. Can take a while.
* login_url
  * This should stay as is, unless Synack changes something
* email
  * The email address you use to log into the platform
* password
  * The password you use to log into the platform
* authy_secret
  * base32 secret for generating Authy tokens
  * Guillaume Boudreau provide a nice [walk through](https://gist.github.com/gboudreau/94bb0c11a6209c82418d01a59d958c93) for getting this secret
    * Follow the above to get Authy into debug mode, then use [THIS CODE](https://gist.github.com/louiszuckerman/2dd4fddf8097ce89594bb33426ab5e23#ok-thats-nice-but-i-want-to-get-rid-of-authy-now) to get your valid TOTP SECRET!
* webhook_url is the incoming webhook url for slack notifications.  This will be used from the bot.py to inform you about obtained missions in real time. To create one simply visit https://api.slack.com/apps?new_app=1 and create an app to add later an incoming webhook into it.  You can choose any workspace to do so.
* gecko true/false (default true) - if false, the `requests` module will be used for the login flow, instead of the geckodriver (works well on Windows)
* proxy true/false (default false) - if true, route requests through a local proxy for debugging
* proxyport (default 8080) - local proxy port used for debugging
* session_token_path (default /tmp/synacktoken) - location to store synack token
* notification_token_path (default /tmp/notificationtoken) - location to store notification token

## Installing as a python module
This can be installed as a python module named `synack` for easy integration with other python code. To install, you can enter the SynackAPI directory and run the following:
```
pip3 install -e .
```

## requirements.txt
Your best bet to have all required python3 modules is to run `pip3 install -r requirements.txt`. I cannot help troubleshoot any other modules.

## geckodriver
You must install [geckodriver](https://github.com/mozilla/geckodriver/) and it must be in your $PATH (note, this is currently true even if you have `gecko` set to `False` in the config file)

# Synack API python3 module

This python3 module provides a class to create objects for interacting with the Synack LP/LP+ platform.
<br>Basic use:
```
from synack import synack

s1 = synack()
s1.getSessionToken()
s1.getAllTargets()
```

# Console command
Once installed as a python module, you can use `synack` as a console command, specifying the name of a script in the `tools` directory. For example, to find the current target, you can run `synack currentTarget`. A CLI is available which wraps around most of the `synack` class functions, if you run `synack cli`.

## synack()
This method creates an object that can be used to interact with the LP/LP+ platform.

## connectToPlatform()
This method takes connects to the Synack platform and writes the session token to disk. It also stays connected by auto-clicking the alert.
### geckodriver
This method only been tested with geckodriver/Firefox. Chrome has not been tested. 
#### SSL Certificates
This method will create the directory `~/.synack/selenium.profile`. The first time connecting to the SRT Platform, you will be asked to install the cacert.crt file. This allows the cert to be permanently stored and used with geckodriver.
### Options
```
# Push all synack.py traffic through proxy
# assumes proxy is at http://127.0.0.1:8080
s1.Proxy = True || False

# Puts the browser in headless mode for use in a linux environment with no GUI
s1.headless = True || False
```

## getSessionToken()
This method reads a file disk location of `synack.tokenPath` and stores the file contents into the `synack.token` variable. If the file does not contain a valid Synack platform authentication token, the rest of this library will not work.

## getAllTargets()
This method pulls down a descriptive JSON on all targets. Most other methods rely on this JSON and should normally be the second function method called.

## getAssessments()
This method returns a list of all Synack assessments that have been completed.

## getCodenames(category, mission_only=False)
This method takes two parameters and returns a list of codenames.

### parameters:
* category `STRING` defines the type of target you're looking for and must be one of the following:
  * "web application"
  * "host"
  * "mobile"
  * "source code"
  * "reverse engineering"
  * "hardware"
* mission_only `BOOLEAN`
  * True: returns targets that only allow SV2M missions
  * False: returns targets that are NOT SV2M only.

## clientName(codename)
This method takes the target codename and returns the client's true name.

## connectToTarget(codename)
This method takes a target codename and connects to it.

## getCategory(codename)
This method takes a target codename and returns what type of assessment the target requires.

## getTargetID(codename)
This method takes a target codename and returns the project slug. This method is generally not used by end users, but rather supports other function methods.

## getCodenameFromSlug(slug)
This method takes a project slug and returns the target codename. This method is generally not used by end users, but rather supports other function methods.

## getCurrentTargetSlug()
This method returns the slug of whatever target you are connected to. If not connected to a target, this will return `None`.

## getScope(codename)
This method takes a codename and returns its scope as a list of dicts.
* `Host` targets return the CIDR notation ranges
* `Web Application` targets return the expanded list of rules:
  * scheme: (http || https)
  * netloc: the "domain" part of the url
  * path: the path of the url
  * wildcard: if the **subdomain** of the url is a wildcard, not the path

```
https://www.example.com/*
*.example.com/path/*

[
  {
    'scheme': 'https',
    'netloc': 'www.example.com',
    'path': '/*',
    'wildcard': False
  },
  {
    'scheme': '',
    'netloc': 'example.com',
    'path': '/path/*',
    'wildcard': True
  }
]
```

## registerAll()
This method registers all unregistered targets
<br>**Thanks Ozgur for most of the leg work :)**

## getAnalytics(codename, status)
This method takes a codename and status `accepted | rejected | in_queue | all` and returns a list of all endpoints reported in that target's `Analytics` tab.

## getHydra(codename)
This method takes a codename and returns a json of all hydra reported in that target's `Hydra` tab.

## getRoes(slug):
This method takes a target slug and returns any additional rules of engagement as a list.

## pollMissions()
This method polls the API for available missions and returns a json to send to `claimMission(missionJson)`

## claimMission(missionJson)
This method takes a json from the pollMission() function and attempts to claim available missions based on dollar value, highest to lowest. The return value is a list of dicts in the format:
```
[
  {
    'target': 'Target Name',
    'payout': '20',
    'claimed': False
  }
]
```

## getNotificationToken()
This method is used to obtain the bearer token used to authenticate to the notifications.synack.com API.

## markNotificationsRead()
This method marks all notifications as read.

## pollNotifications()
This method retrieves all unread notifications and returns a list of dicts with the following fields:
```
{
  "id": INT,                  # ID of the notifications
  "user_id": INT,             # Your synack ID (integer)
  "subject": "STRING",        # Codename, dollar amount of transfer, etc..
  "subject_type": "STRING",   # What is this? listing update, cashout, etc..
  "action": "STRING",         # What is the action: outage_starts, scope, etc..
  "url": "STRING",            # Relevant URL path
  "created_at": "DATETIME",
  "read": BOOL,               # true/false
  "meta": {
                              # All sorts of other stuff
  }
}
```

## Docker setup
There are few ways to run the module under docker, the fastest way will be to obtain it directly and run it using <br>
```docker run -d --name synackapi --dns 8.8.8.8 --rm -v ~/.synack:/root/.synack krasn/synackapi```<br>
The above will run the docker directly under the name synackapi and will use your synack.conf as it's configured per above instructions. The default mode of the docker will be to stay on the background and poll for new targets every hour which will accept.
<br>
To run the missions bot an idea will be to run the docker with the following method:<br>
```docker run -ti --name synackapi --dns 8.8.8.8 --rm -v ~/.synack:/root/.synack krasn/synackapi python3 bot.py```<br>
or if it's already running <br>
```docker exec -ti synackapi krasn/synackapi python3 bot.py```<br>
* Notes ** If would like to build the docker from scratch instructions are on Dockerfile, you will additionally need to modify synack.conf file and set `self.headless = True`
* To simply pull the docker image and do nothing you can always use ```docker pull krasn/synackapi```
