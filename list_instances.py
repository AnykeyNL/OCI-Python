# Oracle OCI - Instance report script
# Version: 1.6 4-September 2018
# Written by: richard.garsthagen@oracle.com
#
# This script will create a CSV report for all compute instances in your OCI account,
# including predefined tags
#
# Instructions:
# - you need the OCI python API, this can be installed by running: pip install oci
# - you need the OCI CLI, this can be installed by running: pip install oci-cli
# - Make sure you have a user with an API key setup in the OCI Identity
# - Create a config file using the oci cli tool by running: oci setup config
# - In the script specify the config file to be used for running the report
# - You can specify any region in the config file, the script will query all enabled regions

import oci
import json
import shapes

# Script configuation ###################################################################################

configfile = "c:\\oci\\config"  # Define config file to be used. 
AllPredefinedTags = True        # use only predefined tags from root compartment or include all compartment tags as well
NoValueString = "n/a"           # what value should be used when no data is available
ReportFile = "C:\\oci\\report.csv"
EndLine = "\n"
# #######################################################################################################


def DisplayInstances(instances, compartmentName, instancetype):
  for instance in instances:
    privateips = ""
    publicips = ""
    instancetypename = ""
    tagtxt = ""
    OS = ""
 
    #print (instance)
    # Handle details for Compute Instances
    if instancetype=="Compute":
      OCPU, MEM, SSD = shapes.ComputeShape(instance.shape)
      response = ComputeClient.list_vnic_attachments(compartment_id = instance.compartment_id, instance_id = instance.id)
      vnics = response.data
      try:
        for vnic in vnics:
          responsenic = NetworkClient.get_vnic(vnic_id=vnic.vnic_id)
          nicinfo = responsenic.data
          privateips = privateips + nicinfo.private_ip + " "
          publicips = publicips + nicinfo.public_ip + " "
      except:
        privateips = NoValueString
        publicips = NoValueString
        
      instancetypename = "Compute"
      version = NoValueString
      namespaces = instance.defined_tags

      # Get OS Details
      try:
        response = ComputeClient.get_image(instance.source_details.image_id)
        imagedetails = response.data
        OS = imagedetails.display_name
      except:
        OS = NoValueString

      
      for customertag in customertags:
         try:
           tagtxt = tagtxt + "," + namespaces[customertag[0]][customertag[1]]
         except:
           tagtxt = tagtxt + "," + NoValueString

    # Handle details for Database Instances
    if instancetype=="DB":
      OCPU, MEM, SSD = shapes.ComputeShape(instance.shape)
      OCPU = instance.cpu_core_count # Overwrite Shape's CPU count, with DB enabled CPU count
      response = databaseClient.list_db_nodes(compartment_id = instance.compartment_id, db_system_id = instance.id)
      dbnodes = response.data
      try:
        for dbnode in dbnodes:
          responsenic = NetworkClient.get_vnic(vnic_id=dbnode.vnic_id)
          nicinfo = responsenic.data
          privateips = privateips + nicinfo.private_ip + " "
          publicips = publicips + nicinfo.public_ip + " "
      except:
          privateips = NoValueString
          publicips = NoValueString    
      
      instancetypename= "DB " + instance.database_edition
      
      version = instance.version

      # Check if defined tags are available
      try:     
        namespaces = instance.defined_tags
        for customertag in customertags:
          try:
             tagtxt = tagtxt + "," + namespaces[customertag[0]][customertag[1]]
          except:
             tagtxt = tagtxt + "," + NoValueString
      except:
        tagtxt = ""  # No Tags

      OS = "Oracle Linux 6.8"

    # Remove prefix from AD Domain
    prefix,AD = instance.availability_domain.split(":")
      
    line = "{},{},{},{},{},{},{},{},{},{},{},{},{}{}".format(instance.display_name, instance.lifecycle_state, instancetypename, version, OS, instance.shape, OCPU, MEM, SSD, compartmentName, AD, privateips, publicips, tagtxt)
    print (line)
    report.write(line + EndLine)    

#Do only once
report = open(ReportFile,'w')

customertags = []
header = "Name,State,Service,Version,OS,Shape,OCPU,MEMORY,SSD,Compartment,AD,PrivateIP,PublicIP"
config = oci.config.from_file(configfile)

identity = oci.identity.IdentityClient(config)
user = identity.get_user(config["user"]).data
RootCompartmentID = user.compartment_id
  
print ("Logged in as: {} @ {}".format(user.description, config["region"]))
print ("Querying Enabled Regions:")

response = identity.list_region_subscriptions(config["tenancy"])
regions = response.data

for region in regions:
  if region.is_home_region:
    home = "Home region"
  else:
    home = ""
  print ("- {} ({}) {}".format(region.region_name, region.status, home))


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

for region in regions:
  config = oci.config.from_file(configfile)
  config["region"] = region.region_name

  identity = oci.identity.IdentityClient(config)
  user = identity.get_user(config["user"]).data
  RootCompartmentID = user.compartment_id
 
  ComputeClient = oci.core.ComputeClient(config)
  NetworkClient = oci.core.VirtualNetworkClient(config)
  
  # Check instances for the root container
  try:
    response = ComputeClient.list_instances(compartment_id=RootCompartmentID)
    instances = response.data
    compartmentName = "Root"
    DisplayInstances(instances, compartmentName, "Compute")
  except:
    print ("API error getting Compute info (root)")
    

  try:
    databaseClient = oci.database.DatabaseClient(config)
    response = databaseClient.list_db_systems(compartment_id=RootCompartmentID)
    DisplayInstances(response.data, compartmentName, "DB")

  except:
    print ("API error getting DB info (root)")
  

  # Check instances for all the underlaying Compartments   
  response = identity.list_compartments(RootCompartmentID)
  compartments = response.data
  for compartment in compartments:
    compartmentName = compartment.name
    
    compartmentID = compartment.id
    try:
   
      response = ComputeClient.list_instances(compartment_id=compartmentID)
      instances = response.data
      DisplayInstances(instances, compartmentName, "Compute")
    except:
     print ("API error getting Compute info")
      

    try:
      databaseClient = oci.database.DatabaseClient(config)
      response = databaseClient.list_db_systems(compartment_id=compartmentID)
      DisplayInstances(response.data, compartmentName, "DB")
    except:
      print ("API error getting DB info")
    
print (" ")
print ("Done, report written to: {}".format(ReportFile))
report.close()




