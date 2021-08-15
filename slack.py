import requests
from pathlib import Path
import configparser

class Slack:

  def __init__(self):
    self.configFile = str(Path.home())+"/.synack/slack.conf"
    self.config = configparser.ConfigParser()
    self.config.read(self.configFile)
    self.mission_webhook_url = self.config['DEFAULT']['mission_webhook_url']

  def send_alert_for_mission(self, missionList):
    URL = self.mission_webhook_url
    for i in range(len(missionList)):
      target = missionList[i]["target"]
      payout = missionList[i]["payout"]
      claimed = missionList[i]["claimed"]
      if claimed == True:
        message = f"Claimed new mission!!\n*Mission: *{target}\n*Payout: *{payout}" # build your message
        requests.post(URL, json={"text": message})
      else:
        pass