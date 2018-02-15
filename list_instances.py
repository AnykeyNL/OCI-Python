# Oracle OCI - Instance report script
# Version: 1.1 15-Feb 2018
# Written by: richard.garsthagen@oracle.com
#
# This script will create a CSV report for all compute instances in your OCI account,
# including predefined tags
#
# Instructions:
# - you need the OCI python API, this can be installed by running: pip install oci
# - you need the OCI CLI, this can be installed by running: pip install oci-cli
# - Make sure you have a user with an API key setup in the OCI Identity
# - Create per region a config file using the oci cli tool by running: oci setup config
# - In the script specify the config files to be used for running the report

import oci
import json

# Script configuation ###################################################################################

configs = ["c:\\oci\\config"] # Define config files to be used. You will need a seperate config file per region and/or account
AllPredefinedTags = True  # use only predefined tags from root compartment or include all compartment tags as well
NoValueString = "n/a"      # what data should be used when no data is available
ReportFile = "C:\\oci\\report.csv"
EndLine = "\n"
# #######################################################################################################


def DisplayInstances(instances, compartmentName, instancetype):
  for instance in instances:
    #print (instance)
    
    instancetypename = ""
    tagtxt = ""
    if instancetype=="Compute":
      instancetypename = "Compute"
      version = NoValueString
      namespaces = instance.defined_tags
      for customertag in customertags:
         try:
           tagtxt = tagtxt + "," + namespaces[customertag[0]][customertag[1]]
         except:
           tagtxt = tagtxt + "," + NoValueString
    if instancetype=="DB":
      instancetypename= instance.database_edition
      version = instance.version
      for customertag in customertags:
        tagtxt = tagtxt + "," + NoValueString  
      
    line = "{},{},{},{},{},{},{}{}".format(instance.display_name, instance.lifecycle_state, instancetypename, version, instance.shape, compartmentName, instance.availability_domain, tagtxt)
    print (line)
    report.write(line + EndLine)    

#Do only once
report = open(ReportFile,'w')

customertags = []
header = "Name,State,Shape,Compartment,AD"
config = oci.config.from_file(configs[0])

identity = oci.identity.IdentityClient(config)
user = identity.get_user(config["user"]).data
RootCompartmentID = user.compartment_id
   
print ("Logged in as: {} @ {}".format(user.description, config["region"]))
print (" ")


# Get all the predefined tags, so the initial header line can be created.
response = identity.list_tag_namespaces(RootCompartmentID)
tags_namespaces = response.data
for namespace in tags_namespaces:
  tagresponse = identity.list_tags(namespace.id)
  tags = tagresponse.data
  for tag in tags:
    customertags.append([namespace.name,tag.name])
    header = header + ",{}.{}".format(namespace.name,tag.name)

if AllPredefinedTags:
  response = identity.list_compartments(RootCompartmentID)
  compartments = response.data  
  for compartment in compartments:
    response = identity.list_tag_namespaces(compartment.id)
    tags_namespaces = response.data
    for namespace in tags_namespaces:
      tagresponse = identity.list_tags(namespace.id)
      tags = tagresponse.data
      for tag in tags:
        customertags.append([namespace.name,tag.name])
        header = header + ",{}.{}".format(namespace.name,tag.name)

print (header)
report.write(header+EndLine)


#Retrieve all instances for each config file (regions)
for c in configs:
  config = oci.config.from_file(c)

  identity = oci.identity.IdentityClient(config)
  user = identity.get_user(config["user"]).data
  RootCompartmentID = user.compartment_id
 
  ComputeClient = oci.core.ComputeClient(config)

  # Check instances for the root container
  response = ComputeClient.list_instances(compartment_id=RootCompartmentID)
  instances = response.data
  compartmentName = "Root"
  DisplayInstances(instances, compartmentName, "Compute")

  databaseClient = oci.database.DatabaseClient(config)
  response = databaseClient.list_db_systems(compartment_id=RootCompartmentID)
  DisplayInstances(response.data, compartmentName, "DB")
  

  # Check instances for all the underlaying Compartments   
  response = identity.list_compartments(RootCompartmentID)
  compartments = response.data
  for compartment in compartments:
    compartmentName = compartment.name
    
    compartmentID = compartment.id
    response = ComputeClient.list_instances(compartment_id=compartmentID)
    instances = response.data
    DisplayInstances(instances, compartmentName, "Compute")

    databaseClient = oci.database.DatabaseClient(config)
    response = databaseClient.list_db_systems(compartment_id=compartmentID)
    DisplayInstances(response.data, compartmentName, "DB")
    
print (" ")
print ("Done, report written to: {}".format(ReportFile))
report.close()




