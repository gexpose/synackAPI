import ipaddress
from netaddr import IPNetwork
import requests
import os
import json
from pathlib import Path
import warnings
import operator
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
import configparser
import time
import pyotp
from urllib.parse import urlparse

warnings.filterwarnings("ignore")

class synack:
    codename = None
    def __init__(self):
        self.jsonResponse = []
        self.assessments = []
        self.tokenPath = "/tmp/synacktoken"
        self.token = ""
        self.url_registered_summary = "https://platform.synack.com/api/targets/registered_summary"
        self.url_activate_target = "https://platform.synack.com/api/launchpoint"
        self.url_assessments = "https://platform.synack.com/api/assessments"
        self.url_unregistered_slugs = "https://platform.synack.com/api/targets?filter%5Bprimary%5D=unregistered&filter%5Bsecondary%5D=all&filter%5Bcategory%5D=all&sorting%5Bfield%5D=dateUpdated&sorting%5Bdirection%5D=desc&pagination%5Bpage%5D="
        self.url_profile = "https://platform.synack.com/api/profiles/me"
        self.url_analytics = "https://platform.synack.com/api/listing_analytics/categories?listing_id="
        self.url_hydra = "https://platform.synack.com/api/hydra_search/search/"
        self.url_published_missions = "https://platform.synack.com/api/tasks/v1/tasks?status=PUBLISHED"
        self.url_logout = "https://platform.synack.com/api/logout"
        self.webheaders = {}
        self.configFile = str(Path.home())+"/.synack/synack.conf"
        self.config = configparser.ConfigParser()
        self.config.read(self.configFile)
        self.email = self.config['DEFAULT']['email']
        self.password = self.config['DEFAULT']['password']
        self.login_wait = int(self.config['DEFAULT']['login_wait'])
        self.login_url = self.config['DEFAULT']['login_url']
        self.authySecret = self.config['DEFAULT']['authy_secret']
        self.headless = False

## Set to 'True' for troubleshooting with Burp Suite ##
        self.Proxy = False
#########
    def getAuthy(self):
        totp = pyotp.TOTP(self.authySecret)
        totp.digits = 7
        totp.interval = 10
        totp.issuer = "synack"
        return(totp.now())

## Get Synack platform session token ##
    def getSessionToken(self):
        if Path(self.tokenPath).exists():
            with open(self.tokenPath, "r") as f:
                self.token = f.readline()
            f.close()
        else:
            raise IOError('No Synack token. Run the keepalive script.')
        self.webheaders = {"Authorization": "Bearer " + self.token}
        response = self.try_requests("GET", self.url_profile, 10)
        profile = response.json()
        self.webheaders['user_id'] = profile['user_id']

#################################################
## Function to attempt requests multiple times ##
#################################################

    def try_requests(self, func, URL, times, extra=None):
        http_proxy  = "http://127.0.0.1:8080"
        https_proxy = "http://127.0.0.1:8080"
        proxyDict = {
            "http" : http_proxy,
            "https" : https_proxy
        }

        url = urlparse(URL)
        scheme = url.scheme
        netloc = url.netloc
        path   = url.path
        port   = url.port
        platform = "platform.synack"

        if self.Proxy == True:
            for attempt in range(times):
                try:
                    if func == "PUT":
                        putData = json.dumps({"listing_id": extra})
                        newHeaders = dict(self.webheaders)
                        newHeaders['Content-Type'] = "application/json"
                        response = requests.put(URL, headers=newHeaders, data=putData, proxies=proxyDict, verify=False)
                        if response.status_code == 401 and platform in netloc:
                            self.connectToPlatform()
                            self.getSessionToken()
                        else:
                            return response
                    elif func == "GET":
                        if extra == None:
                            response = requests.get(URL, headers=self.webheaders, proxies=proxyDict, verify=False)
                            if response.status_code == 401 and platform in netloc:
                                self.connectToPlatform()
                                self.getSessionToken()
                            else:
                                return response
                        else:
                            parameters = {'page': extra}
                            response = requests.get(URL, headers=self.webheaders, params=parameters, proxies=proxyDict, verify=False)
                            if response.status_code == 401 and platform in netloc:
                                self.connectToPlatform()
                                self.getSessionToken()
                            else:
                                return response
                    elif func == "POST":
                        response = requests.post(URL, headers=self.webheaders, proxies=proxyDict, json=extra, verify=False)
                        if response.status_code == 401 and platform in netloc:
                            self.connectToPlatform()
                            self.getSessionToken()
                        else:
                            return response
                except Exception as err:
                    last_err = err
            raise last_err
        else:
            for attempt in range(times):
                try:
                    if func == "PUT":
                        putData = json.dumps({"listing_id": extra})
                        newHeaders = dict(self.webheaders)
                        newHeaders['Content-Type'] = "application/json"
                        response =requests.put(URL, headers=newHeaders, data=putData, verify=False)
                        if response.status_code == 401 and platform in netloc:
                            self.connectToPlatform()
                            self.getSessionToken()
                        else:
                            return response
                    elif func == "GET":
                        if extra == None:
                            response =requests.get(URL, headers=self.webheaders, verify=False)
                            if response.status_code == 401 and platform in netloc:
                                self.connectToPlatform()
                                self.getSessionToken()
                            else:
                                return response
                        else:
                            parameters = {'page': extra}
                            response = requests.get(URL, headers=self.webheaders, params=parameters, verify=False)
                            if response.status_code == 401 and platform in netloc:
                                self.connectToPlatform()
                                self.getSessionToken()
                            else:
                                return response
                    elif func == "POST":
                        response =  requests.post(URL, headers=self.webheaders, json=extra, verify=False)
                        if response.status_code == 401 and platform in netloc:
                            self.connectToPlatform()
                            self.getSessionToken()
                        else:
                            return response
                    else:
                        raise ValueError("Choose a real HTTP method.")
                except Exception as err:
                    last_err = err
            raise last_err


####################################################
## Function to find all occurrences of nested key ##
####################################################

    def findkeys(self, node, kv):
        if isinstance(node, list):
            for i in node:
                for x in self.findkeys(i, kv):
                    yield x
        elif isinstance(node, dict):
            if kv in node:
                yield node[kv]
            for j in node.values():
                for x in self.findkeys(j, kv):
                    yield x

##############################################
## Returns a JSON of all registered targets ##
## This must be the first call after object ##
## instantiation - it populates the json    ##
##############################################
    def getAllTargets(self):
        self.jsonResponse.clear()
        response = self.try_requests("GET", self.url_registered_summary, 10)
        self.jsonResponse[:] = response.json()
        return(response.status_code)


########################################
## Returns a list of web or host target codenames
## that are (mission only / not mission only)
## category: web || host || RE || mobile || sourceCode || harware
## mission_only: True || False
########################################
    def getCodenames(self, category, mission_only=False):
        if category.lower() == "web":
            category = "web application"
        if category.lower() == "re":
            category = "reverse engineering"
        if category.lower() == "sourceCode":
            category = "source code"
        targets = []
        for i in range (len(self.jsonResponse)):
            if mission_only == True:
                if self.jsonResponse[i]['vulnerability_discovery'] == False:
                    if self.jsonResponse[i]['category']['name'].lower() == category.lower():
                        targets.append(self.jsonResponse[i]['codename'])
                    else:
                        continue
                else:
                    continue
            elif mission_only == False:
                if self.jsonResponse[i]['vulnerability_discovery'] == True:               
                    if self.jsonResponse[i]['category']['name'].lower() == category.lower():
                        targets.append(self.jsonResponse[i]['codename'])
                    else:
                        continue
                else:
                    continue
        return(targets)

#########################################
## This returns the "slug" of a target ##
## based on the codename ##
#########################################

    def getTargetID(self, codename):
        for i in range (len(self.jsonResponse)):
            if self.jsonResponse[i]['codename'].lower() == codename.lower():
                return(self.jsonResponse[i]['id'])

##################################
## This retuens the codemane of ##
## a target based on the slug   ##
##################################
    def getCodenameFromSlug(self, slug):
        for i in range(len(self.jsonResponse)):
            if self.jsonResponse[i]['id'].lower() == slug.lower():
                return(self.jsonResponse[i]['codename'])

#################################
## This private method returns ##
## the organization ID         ##
#################################
    def __getOrgID(self, codename):
        for i in range (len(self.jsonResponse)):
            if self.jsonResponse[i]['codename'].lower() == codename.lower():
                return(self.jsonResponse[i]['organization_id'])

######################################
## This returns the target category ##
######################################
    def getCategory(self, codename):
        for i in range (len(self.jsonResponse)):
            if self.jsonResponse[i]['codename'].lower() == codename.lower():
                return(self.jsonResponse[i]['category']['name'])

#####################################################
## This will connect you to the target by codename ##
#####################################################
    def connectToTarget(self, codename):
        slug = self.getTargetID(codename)
        response = self.try_requests("PUT", self.url_activate_target, 10, slug)
        time.sleep(5)
        return response.status_code

########################################################
## This just returns the "real" client name sometimes ##
########################################################
    def clientName(self, codename):
        for i in range (len(self.jsonResponse)):
            if self.jsonResponse[i]['codename'].lower() == codename.lower():
                return(self.jsonResponse[i]['name'])


################################
## This gets the target scope ##
################################

    def getScope(self, codename):
        category = self.getCategory(codename) 
        orgID = self.__getOrgID(codename)
        slug = self.getTargetID(codename)
        if category.lower() == "web application":
            scopeURL = "https://platform.synack.com/api/asset/v1/organizations/"+orgID+"/owners/listings/"+slug+"/webapps"
            allRules = []
            response = self.try_requests("GET", scopeURL, 10)
            jsonResponse = response.json()
            j = 0
            while j < len(jsonResponse):
                if jsonResponse[j]['status'] == "out":
                    j+=1
                    continue
                else:
                    tmpSet = set(self.findkeys(jsonResponse[j], 'rule'))
                    for thisURL in tmpSet:
                        url = urlparse(thisURL)
                        scheme = url.scheme
                        netloc = url.netloc
                        path   = url.path
                        port   = url.port
                        wildcard = False
                        if len(netloc) != 0:
                            subdomain = netloc.split('.')[0]
                            if subdomain == "*":
                                wildcard = True
                                netloc = ".".join(netloc.split('.')[1:])
                        else:
                            if len(path) != 0:
                                netloc = path.split('/')[0]
                                checkWildcard = netloc.split('.')[0]
                                if checkWildcard == "*":
                                    wildcard = True
                                    if ":" in netloc:
                                        port = netloc.split(':')[1]
                                        thisURL = netloc.split(':')[0]
                                        netloc = ".".join(thisURL.split('.')[1:])
                                    else:
                                        port = 443
                                        netloc = ".".join(netloc.split('.')[1:])
                                else:
                                    if ":" in netloc:
                                        port = netloc.split(':')[1]
                                        thisURL = netloc.split(':')[0]
                                        netloc = ".".join(thisURL.split('.')[0:])
                                    else:
                                        port = 443
                                        netloc = ".".join(netloc.split('.')[0:])
                                path = "/" + "/".join(path.split('/')[1:])
                            else:
                                continue
                        scopeDict = {
                                        'scheme' : scheme,
                                        'netloc': netloc,
                                        'path': path,
                                        'port': port,
                                        'wildcard': wildcard
                                    }
                    allRules.append(scopeDict)
                    j+=1
            return(list(allRules))
        if category.lower() == "host":
            scopeURL = "https://platform.synack.com/api/targets/"+slug+"/cidrs"
            cidrs = []
            x = 1
            response = self.try_requests("GET", scopeURL, 10, x)
            temp = json.dumps(response.json()['cidrs']).replace("[","").replace("]","").replace("\"","").replace(", ","\n").split("\n")
            cidrs.extend(temp)
            while len(temp) > 1:
                x += 1
                response = self.try_requests("GET", scopeURL, 10, x)
                if (response.json().get("cidrs")==None):
                    break
                else:
                    temp = json.dumps(response.json()['cidrs']).replace("[","").replace("]","").replace("\"","").replace(", ","\n").split("\n")
                    cidrs.extend(temp)
            cidrs = list(set(cidrs))
            return(cidrs)

########################################
## This converts CIDR list to IP list ##
## This is a much faster method, previous method was causing problems on large hosts ##
########################################
    def getIPs(self, cidrs):
        IPs = []
        for i in range(len(cidrs)):
            if cidrs[i] != "":
                for ip in ipaddress.ip_network(cidrs[i]):
                    IPs.append(str(ip))
        return(IPs)
    
##############################################
## This gets all of your passed assessments ##
##############################################
    def getAssessments(self):
        self.assessments.clear()
        response = self.try_requests("GET", self.url_assessments, 10)
        jsonResponse = response.json()
        for i in range(len(jsonResponse)):
            if jsonResponse[i]['written_assessment']['passed'] == True:
                self.assessments.append(jsonResponse[i]['category_name'])
            i+=1

##########################################################
## This gets endpoints from Web Application "Analytics" ##
##########################################################
    def getAnalytics(self, codename):
        slug = self.getTargetID(codename)
        url_analytics = self.url_analytics + slug
        response = self.try_requests("GET", url_analytics, 10)
        jsonResponse = response.json()
        analytics = []
        targetType = self.getCategory(codename)
        if targetType == "Web Application":
            if "value" in jsonResponse:
                for value in range(len(jsonResponse['value'])):
                    for exploitable_location in range(len(jsonResponse['value'][value]['exploitable_locations'])):
                        try:
                            URI = urlparse(str(jsonResponse['value'][value]['exploitable_locations'][exploitable_location]['value']))
                        except:
                            continue
                        scheme = URI.scheme
                        port = str(URI.port)
                        if port == "None":
                            if scheme == "http":
                                port = "80"
                            elif scheme == "https":
                                port = "443"
                        if len(jsonResponse['value'][value]['categories']) == 2:
                            analytics.append('"'
                                +codename
                                +'","'
                                +str(jsonResponse['value'][value]['categories'][0])
                                +'","'
                                +str(jsonResponse['value'][value]['categories'][1])
                                +'","URL","'
                                +str(scheme)
                                +'","'
                                +port
                                +'","'
                                +str(jsonResponse['value'][value]['exploitable_locations'][exploitable_location]['value'])
                                +'","'
                                +str(jsonResponse['value'][value]['exploitable_locations'][exploitable_location]['status'])
                                +'"'
                            )
                        elif len(jsonResponse['value'][value]['categories']) == 1:
                            analytics.append('"","'
                                +codename
                                +'","'
                                +str(jsonResponse['value'][value]['categories'][0])
                                +'","'
                                +str(jsonResponse['value'][value]['categories'][1])
                                +'","URL","'
                                +str(scheme)
                                +'","'
                                +port
                                +'","'
                                +str(jsonResponse['value'][value]['exploitable_locations'][exploitable_location]['value'])
                                +'","'
                                +str(jsonResponse['value'][value]['exploitable_locations'][exploitable_location]['status'])
                                +'"'
                            )
                        else:
                            next
            return analytics
        elif targetType == "Host":
            if "value" in jsonResponse:
                for value in range(len(jsonResponse['value'])):
                    for exploitable_location in range(len(jsonResponse['value'][value]['exploitable_locations'])):
                        if len(jsonResponse['value'][value]['categories']) == 2:
                            if jsonResponse['value'][value]['exploitable_locations'][exploitable_location]['type'] == "url":
                                URI = urlparse(str(jsonResponse['value'][value]['exploitable_locations'][exploitable_location]['value']))
                                scheme = URI.scheme
                                port = str(URI.port)
                                if port == "None":
                                    if scheme == "http":
                                        port = "80"
                                    elif scheme == "https":
                                        port = "443"
                                analytics.append('"'
                                    +codename
                                    +'","'
                                    +str(jsonResponse['value'][value]['categories'][0])
                                    +'","'
                                    +str(jsonResponse['value'][value]['categories'][1])
                                    +'","URL","'
                                    +str(scheme)
                                    +'","'
                                    +port
                                    +'","'
                                    +str(jsonResponse['value'][value]['exploitable_locations'][exploitable_location]['value'])
                                    +'","'
                                    +str(jsonResponse['value'][value]['exploitable_locations'][exploitable_location]['status'])
                                    +'"'
                                    )
                            elif jsonResponse['value'][value]['exploitable_locations'][exploitable_location]['type'] == "ip":
                                analytics.append('"'
                                    +codename
                                    +'","'
                                    +str(jsonResponse['value'][value]['categories'][0])
                                    +'","'
                                    +str(jsonResponse['value'][value]['categories'][1])
                                    +'","HOST","'
                                    +str(jsonResponse['value'][value]['exploitable_locations'][exploitable_location]['protocol'])
                                    +'","'
                                    +str(jsonResponse['value'][value]['exploitable_locations'][exploitable_location]['port'])
                                    +'","'
                                    +str(jsonResponse['value'][value]['exploitable_locations'][exploitable_location]['address'])
                                    +'","'
                                    +str(jsonResponse['value'][value]['exploitable_locations'][exploitable_location]['status'])
                                    +'"'
                                    )
                        elif len(jsonResponse['value'][value]['categories']) == 1:
                            if jsonResponse['value'][value]['exploitable_locations'][exploitable_location]['type'] == "url":
                                analytics.append('"","'
                                    +codename
                                    +'","'
                                    +str(jsonResponse['value'][value]['categories'][0])
                                    +'","URL","'
                                    +str(scheme)
                                    +'","'
                                    +str(port)
                                    +'","'
                                    +str(jsonResponse['value'][value]['exploitable_locations'][exploitable_location]['value'])
                                    +'","'
                                    +str(jsonResponse['value'][value]['exploitable_locations'][exploitable_location]['status'])
                                    +'"'
                                    )
                            elif jsonResponse['value'][value]['exploitable_locations'][exploitable_location]['type'] == "ip":
                                analytics.append('"","'
                                    +codename
                                    +'","'
                                    +str(jsonResponse['value'][value]['categories'][0])
                                    +'","HOST","'
                                    +str(jsonResponse['value'][value]['exploitable_locations'][exploitable_location]['protocol'])
                                    +'","'
                                    +str(jsonResponse['value'][value]['exploitable_locations'][exploitable_location]['port'])
                                    +'","'
                                    +str(jsonResponse['value'][value]['exploitable_locations'][exploitable_location]['address'])
                                    +'","'
                                    +str(jsonResponse['value'][value]['exploitable_locations'][exploitable_location]['status'])
                                    +'"'
                                    )
                        else:
                            next
            return analytics

#############################################
## This registers all unregistered targets ##
#############################################

    def registerAll(self):
        self.getAssessments()
        pageNum = 1
        next_page = True
        unregistered_slugs = []
        while next_page:
            url_slugs = self.url_unregistered_slugs + str(pageNum)
            response = self.try_requests("GET", url_slugs, 10)
            jsonResponse = response.json()
            if (len(jsonResponse)!=0):
                for i in range (len(jsonResponse)):
                    if jsonResponse[i]["category"]["name"] in self.assessments:
                        unregistered_slugs.append(str(jsonResponse[i]["slug"]))
                pageNum += 1
            else:
                next_page = False
                pageNum += 1
        for i in range (len(unregistered_slugs)): 
            url_register_slug = "https://platform.synack.com/api/targets/"+unregistered_slugs[i]+"/signup"
            data='{"ResearcherListing":{"terms":1}}'
            response = self.try_requests("POST", url_register_slug, 10, data)
            slug = unregistered_slugs[i]
        self.getAllTargets()
        for i in range(len(unregistered_slugs)):
            codename = self.getCodenameFromSlug(unregistered_slugs[i])
            if codename == None:
                print("Error registerring "+unregistered_slugs[i]+"!")
            else:
                print("Successfully registered "+str(codename))

###############
## Keepalive ##
###############
    def connectToPlatform(self):
        options = Options()
        if self.headless == True:
            options.headless = True
        else:
            options.headless = False
        driver = webdriver.Firefox(options=options)
        driver.get(self.login_url)
        assert "Synack" in driver.title
        ## Fill in the email address ##
        email_path = '/html/body/div[2]/div/div/div[2]/form/fieldset/div[1]/input'
        driver.find_element_by_xpath(email_path).click()
        driver.find_element_by_xpath(email_path).send_keys(self.email)
        ## Fill in the password ##
        password_path = '/html/body/div[2]/div/div/div[2]/form/fieldset/div[2]/input'
        driver.find_element_by_xpath(password_path).click()
        driver.find_element_by_xpath(password_path).send_keys(self.password)
        ## Click the login button ##
        login_path = '/html/body/div[2]/div/div/div[2]/form/fieldset/div[3]/button'
        driver.find_element_by_xpath(login_path).click()
        time.sleep(5)
        ## Hope the authy works! ##
        authy_path = '/html/body/div[2]/div/div/div[2]/form/fieldset/div[1]/input'
        driver.find_element_by_xpath(authy_path).click()
        driver.find_element_by_xpath(authy_path).send_keys(self.getAuthy())
        authy_submit_path = '/html/body/div[2]/div/div/div[2]/form/fieldset/div[2]'
        driver.find_element_by_xpath(authy_submit_path).click()
        while True:
            session = driver.execute_script("return sessionStorage.getItem('shared-session-com.synack.accessToken')")
            if isinstance(session, str):
                break
## Write the session token to /tmp/synacktoken ##
        with open('/tmp/synacktoken',"w") as f:
            f.write(session)
        f.close()
        print("Connected to platform.")
        if self.headless == True:
            driver.quit()
        return(0)

###########
## Hydra ##
###########

    def getHydra(self, codename):
        slug = self.getTargetID(codename)
        pageNum = 1
        hydraResults = []
        while True:
            url_hydra = self.url_hydra +"?page=" +str(pageNum)+"&listing_uids="+slug+"&q=%2Bport_is_open%3Atrue"
            response = self.try_requests("GET", url_hydra, 10)
            hydraResponse = response.json()
            if len(hydraResponse) == 0:
                break
            else:
                hydraResults = hydraResults + hydraResponse
                pageNum += 1
        return hydraResults

###################
## Mission stuff ##
###################

## Poll for missions ##

    def pollMissions(self):
        response = self.try_requests("GET", self.url_published_missions, 10)
        try:
            jsonResponse = response.json()
        except:
            jsonResponse = {}
        try:
            return jsonResponse
        except NameError:
            jsonResponse = {}
        return jsonResponse

####################
## CLAIM MISSIONS ##
####################
    def claimMission(self, missionJson):
        dollarValue = {}
        claim = {'type': 'CLAIM'}
################
## Sort missions by dollar amount high to low
################
        for i in range(len(missionJson)):
            dollarValue[i] = missionJson[i]["payout"]["amount"]
        sorted_tuples = sorted(dollarValue.items(), key=operator.itemgetter(1), reverse=True)
        sorted_dict = {k: v for k, v in sorted_tuples}
################
        i = len(sorted_dict.keys())
        missionList = []
        for key in sorted_dict.keys():
            i-= 1
            campaign = missionJson[key]["campaign"]["title"]
            campaignID = missionJson[key]["campaign"]["id"]
            orgID = missionJson[key]["organization"]["id"]
            listingID = missionJson[key]["listing"]["id"]
            taskID = missionJson[key]["id"]
            payout = str(missionJson[key]["payout"]["amount"])
            url_claimPath = "https://platform.synack.com/api/tasks/v1/organizations/" + orgID + "/listings/" + listingID + "/campaigns/" + campaignID + "/tasks/" + taskID + "/transitions"
            claimResponse = self.try_requests("POST", url_claimPath, 10, claim)
            if claimResponse.status_code == 201:
                claimed = True
            else:
                claimed = False
            missionDict = {"target": campaign, "payout": payout, "claimed": claimed}
            missionList.append(missionDict)
        return(missionList)
            
