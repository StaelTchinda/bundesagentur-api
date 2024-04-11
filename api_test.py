import requests
import json
import pandas as pd
import openpyxl

#not all parameters given at https://github.com/AndreasFischer1985/bewerberboerse-api/tree/main seem to work so here a list of parameters that do work:
#was=(beruf|kenntnisse|spracen|...)
#wo=(ort|plz|bundesland|land|...)
#angebotsart=(1|2|34|4) --1:arbeit, 2:selbstständig, 34:praktikum/trainee, 4:ausbildung
#size=\d --number of applicants to return, max is 1000
#arbeitszeit=(vz|tz|snw|ht|mj)
#berufserfahrung=(2|null|1)
#page=\d --page of $size entries starting at 0
api_url =  "https://rest.arbeitsagentur.de/jobboerse/bewerbersuche-service/pc/v1/bewerber?wo=81829&size=10&"
#api_url = "https://rest.arbeitsagentur.de/jobboerse/bewerbersuche-service/pc/v1/bewerberdetails/10000-1190328953-B"


auth = {'client_id':'919b0af7-6e5f-4542-a7f5-04268b8bae2e', 'client_secret':'93fce94c-5be2-4dc8-b040-c62818a4b003', 'grant_type':'client_credentials'}
response = requests.post("https://rest.arbeitsagentur.de/oauth/gettoken_cc", data=auth)
print(response, "(authentication)")
token = response.json().get("access_token")

response = requests.get(api_url, headers={'OAuthAccessToken':token})
print(response, "(query)")

with open('data.json', 'w', encoding='utf-8') as f:
    json.dump(response.json(), f, ensure_ascii=False, indent=4)

#data = json.load(open("data.json"))
#df = pd.DataFrame(data["bewerber"])
#df.to_excel("data.xlsx")