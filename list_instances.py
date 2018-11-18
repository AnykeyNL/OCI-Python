# Oracle OCI - Instance report script
# Version: 1.8 18-November 2018
# Written by: richard.garsthagen@oracle.com
#
# This script will create a CSV report for all compute and DB instances (including ADW and ATP)
# in your OCI account, including predefined tags
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
import logging

# Script configuation ###################################################################################

configfile = "c:\\oci\\config"  # Define config file to be used. 
AllPredefinedTags = True        # use only predefined tags from root compartment or include all compartment tags as well
NoValueString = "n/a"           # what value should be used when no data is available
FieldSeperator = ","            # what value should be used as field seperator
ReportFile = "C:\\oci\\report.csv"
EndLine = "\n"

# #######################################################################################################


#logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

def DisplayInstances(instances, compartmentName, instancetype, regionname):
  for instance in instances:
    privateips = ""
    publicips = ""
    instancetypename = ""
    tagtxt = ""
    OS = ""
    LicenseIncluded = ""
 
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

      shape = instance.shape

      # Get OS Details
      try:
        response = ComputeClient.get_image(instance.source_details.image_id)
        imagedetails = response.data
        OS = imagedetails.display_name
      except:
        OS = NoValueString
      
      prefix,AD = instance.availability_domain.split(":")
      LicenseIncluded = "BYOL"

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
          
      if instance.license_model == "LICENSE_INCLUDED":
        LicenseIncluded = "YES"
      else:
        LicenseIncluded = "BYOL"
      
      instancetypename= "DB " + instance.database_edition
      version = instance.version
      OS = "Oracle Linux 6.8"
      shape = instance.shape
      prefix,AD = instance.availability_domain.split(":")

    # Handle details for Autonomous Database (ATP)
    if instancetype == "ATP":
      OCPU = instance.cpu_core_count
      MEM = NoValueString
      SSD = instance.data_storage_size_in_tbs
      instancetypename = "ATP"
      version = NoValueString
      OS = NoValueString
      shape = "ATP"
      AD = regionname.upper()
      privateips = NoValueString
      publicips = NoValueString
      if instance.license_model == "LICENSE_INCLUDED":
        LicenseIncluded = "YES"
      else:
        LicenseIncluded = "BYOL"

    # Handle details for Autonomous Database (ADW)
    if instancetype == "ADW":
      OCPU = instance.cpu_core_count
      MEM = NoValueString
      SSD = instance.data_storage_size_in_tbs
      instancetypename = "ADW"
      version = NoValueString
      OS = NoValueString
      shape = "ADW"
      AD = regionname.upper()
      privateips = NoValueString
      publicips = NoValueString
      if instance.license_model == "LICENSE_INCLUDED":
        LicenseIncluded = "YES"
      else:
        LicenseIncluded = "BYOL"
    
    try:     
      namespaces = instance.defined_tags
      for customertag in customertags:
        try:
           tagtxt = tagtxt + FieldSeperator + namespaces[customertag[0]][customertag[1]]
        except:
           tagtxt = tagtxt + FieldSeperator + NoValueString
    except:
      tagtxt = ""  # No Tags
      

    #line = "{},{},{},{},{},{},{},{},{},{},{},{},{},{}{}".format(instance.display_name, instance.lifecycle_state, instancetypename, LicenseIncluded, version, OS, shape, OCPU, MEM, SSD, compartmentName, AD, privateips, publicips, tagtxt)
    line =   "{}{}".format(      instance.display_name,    FieldSeperator)
    line = "{}{}{}".format(line, instance.lifecycle_state, FieldSeperator)
    line = "{}{}{}".format(line, instancetypename,         FieldSeperator)
    line = "{}{}{}".format(line, LicenseIncluded,          FieldSeperator)
    line = "{}{}{}".format(line, version,                  FieldSeperator)
    line = "{}{}{}".format(line, OS,                       FieldSeperator)
    line = "{}{}{}".format(line, shape,                    FieldSeperator)
    line = "{}{}{}".format(line, OCPU,                     FieldSeperator)
    line = "{}{}{}".format(line, MEM,                      FieldSeperator)
    line = "{}{}{}".format(line, SSD,                      FieldSeperator)
    line = "{}{}{}".format(line, compartmentName,          FieldSeperator)
    line = "{}{}{}".format(line, AD,                       FieldSeperator)
    line = "{}{}{}".format(line, privateips,               FieldSeperator)
    line = "{}{}".format(line, publicips)
    line = "{}{}".format(line, tagtxt)
    print (line)
    report.write(line + EndLine)    

#Do only once
report = open(ReportFile,'w')

customertags = []
header = "Name,State,Service,Licensed,Version,OS,Shape,OCPU,MEMORY,SSD TB,Compartment,AD,PrivateIP,PublicIP".replace(",", FieldSeperator)
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
    header = header + FieldSeperator +  "{}.{}".format(namespace.name,tag.name)

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
        header = header + FieldSeperator + "{}.{}".format(namespace.name,tag.name)

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
  
  
  # Check instances for all the underlaying Compartments   
  response = identity.list_compartments(RootCompartmentID,compartment_id_in_subtree=True)
  compartments = response.data

  # Insert (on top) the root compartment
  RootCompartment = oci.identity.models.Compartment()
  RootCompartment.id = RootCompartmentID
  RootCompartment.name = "root"
  compartments.insert(0, RootCompartment)
  
  for compartment in compartments:
    compartmentName = compartment.name
    print ("Compartment:" + compartmentName)
    compartmentID = compartment.id
    try:
      response = ComputeClient.list_instances(compartment_id=compartmentID)
      if len(response.data) > 0:
        DisplayInstances(response.data, compartmentName, "Compute", region.region_name)
    except:
      print ("Error?")

    databaseClient = oci.database.DatabaseClient(config)
    try:
      response = databaseClient.list_db_systems(compartment_id=compartmentID)
      if len(response.data) > 0:
        DisplayInstances(response.data, compartmentName, "DB", region.region_name)
    except:
      print ("Error?")

    try:
      response = databaseClient.list_autonomous_data_warehouses(compartment_id=compartmentID)
      if len(response.data) > 0:
        DisplayInstances(response.data, compartmentName, "ADW", region.region_name)
    except:
      print ("Error?")

    try:
      response = databaseClient.list_autonomous_databases(compartment_id=compartmentID)
      if len(response.data) > 0:
        DisplayInstances(response.data, compartmentName, "ATP", region.region_name)
    except:
      print ("Error?")

    
print (" ")
print ("Done, report written to: {}".format(ReportFile))
report.close()




