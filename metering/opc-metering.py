# https://docs.oracle.com/en/cloud/get-started/subscriptions-cloud/meter/

import requests

IDname = "<ID Domain Name>"
username = "<username>"
password = "<password>"
IDCS   = "idcs-<id>"
CACCT = "cacct-<id>"

baseurl = "https://itra.oraclecloud.com"
entitlementurl = "{}/itas/{}/myservices/api/v1/serviceEntitlements".format(baseurl,IDCS)

# Query Service Entitlements
s = requests.Session()
s.auth = (username,password)
s.headers.update({'X-ID-TENANT-NAME': IDname})
response = s.get(entitlementurl)

print (entitlementurl)

if (response.status_code == 200):
    data = response.json()
    for item in data['items']:
        #print (item)
        try:
            print ("{} - {} - {} - {}".format(item['serviceDefinition']['name'],item['status'], item['cloudAccount']['id'], item['purchaseEntitlement']['id']))
        except:
            print ("{} - {}".format(item['serviceDefinition']['name'],item['status']))
       # print (item['serviceDefinition']['canonicalLink'])
        
    
else:
    print ("error")


# Query Metering API

EntitlementID = "<entitlementID>" # Get this from the previous Service Entitlements

#meteringurl = "{}/metering/api/v1/usagecost/{}?startTime=2018-06-10T23:00:00.000&endTime=2018-06-21T00:00:00.000&usageType=TOTAL&timeZone=Europe/London&dcAggEnabled=Y&computeTypeEnabled=Y".format(baseurl,CACCT)
meteringurl = "{}/metering/api/v1/cloudbucks/{}?entitlementIds={}".format(baseurl,CACCT,EntitlementID)
    
print (meteringurl)

s1 = requests.Session()
s1.auth = (username,password)
s1.headers.update({'X-ID-TENANT-NAME': IDname})
response = s1.get(meteringurl)

print (response.text)





    










