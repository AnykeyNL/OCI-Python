# OCI - Berametal Database Scaling Script
# Written by: Richard Garsthagen - richard@oc-blog.com
# Version 1.0 - September 5th 2018
#
# More info see: www.oc-blog.com

import instanceMetadata
import oci
import json
import datetime
import time

DayOfWeekString = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

md = instanceMetadata.get_metadata()

systemID = md["displayName"]
Region = md["canonicalRegionName"]

configfile = "~/config"

config = oci.config.from_file(configfile)
config["region"] = Region

identity = oci.identity.IdentityClient(config)
user = identity.get_user(config["user"]).data
RootCompartmentID = user.compartment_id

print ("Logged in as: {} @ {}".format(user.description, config["region"]))

databaseClient = oci.database.DatabaseClient(config)
DbSystem = oci.database.models.DbSystem()
response = databaseClient.get_db_system(db_system_id = md["displayName"])
DbSystem = response.data

DayOfWeek = datetime.datetime.today().weekday()
Day = DayOfWeekString[DayOfWeek]
print ("Day of week: {}".format(Day))

Schedule = ""

for def_tags in DbSystem.defined_tags:
  if def_tags == "Schedule":
    schedTags = DbSystem.defined_tags["Schedule"]
    try:
      Schedule = schedTags["AnyDay"]
    except:
      print ("No anyday record")
    if (DayOfWeek < 5):  # Weekday
      try:
        Schedule = schedTags["WeekDay"]
      except:
        print ("No Weekday record")
    else:  # Weekend
      try:
        Schedule = schedTags["Weekend"]
      except:
        print ("No Weekend record")
    try:  # Check Day specific record
       Schedule = schedTags[Day]
    except:
       print ("No day specific record found")

try:
  HourCoreCount = Schedule.split(",")
except:
  HourCoreCount = ""

if (len(HourCoreCount) == 24):  # Check if schedule contains 24 hours.
  CurrentHour = datetime.datetime.now().hour
  print ("Current hour: {}".format(CurrentHour))
  print ("Current Core count:   {}".format(DbSystem.cpu_core_count))
  print ("Scheduled Core count: {}".format(HourCoreCount[CurrentHour]))

  if (int(DbSystem.cpu_core_count) < int(HourCoreCount[CurrentHour])):
    print ("System needs to scale up!")
    tries = 0
    while (tries < 5):
      if (DbSystem.lifecycle_state == "AVAILABLE"):
        print ("System is available for scaling up")
        DbSystemDetails = oci.database.models.UpdateDbSystemDetails(cpu_core_count = int(HourCoreCount[CurrentHour]))
        response = databaseClient.update_db_system(db_system_id = systemID, update_db_system_details = DbSystemDetails)
        print (response.data)
        print ("System is re-scaling")
        break
      else:
        print ("System is not available for scaling... attempt: {}".format(tries))
        time.sleep(60)
        response = databaseClient.get_db_system(db_system_id = systemID)
        DbSystem = response.data
        tries = tries + 1
  else:
    print ("No Action needed")


