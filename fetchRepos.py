import json
import re
import requests
import sys
import subprocess
import urllib.parse

username = sys.argv[1]
password = sys.argv[2]

print("Fetching repositories of {}...".format(username))

url = "https://api.bitbucket.org/2.0/repositories/{}?pagelen=100".format(username)
repositories = []

with requests.get(url, auth=(username, password)) as response:
  content = response.json()

  header = [ "Repository:", "URL:", "Type:" ]
  print(f"{header[0]:30} | {header[1]:80} | {header[2]}")
  for value in content['values']:
    repoName = value['name']
    repoLink = value['links']['clone'][0]['href']
    if repoLink.endswith(".git"):
      repoType = "Git"
    else:
      repoType = "Hg"

    print(f"{repoName:30} | {repoLink:80} | {repoType}")
    repositories.append([ repoName, repoLink, repoType ])

print("\n\n")
try:
  for repo in repositories:
    name = repo[0]
    link = repo[1]
    repoType = repo[2]
  
    match = re.match("(https://)(.*)(@)(.*)", link)
    newLink = "https://{}:{}@{}".format(username, urllib.parse.quote(password), match[4])
  
    print("Fetching {} repository {}...".format(repoType, name))

    status = None
    if repoType == "Git":
      status = subprocess.run([ "git", "clone", newLink, name ])
    else:
      status = subprocess.run([ "hg", "clone", newLink, name ])
      
    if status != None and status.returncode != 0:
      raise Exception("Failed to fetch {}, aborting.".format(name))

except Exception as e:
  print(e)

