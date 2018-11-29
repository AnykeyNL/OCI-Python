# Oracle OCI - Auto Delete Instances
# Version: 1.8 22-November 2018
# Written by: richard@oc-blog.com
# More info see: www.oc-blog.com
#
# This script will auto delete instances that do not have pre-assigned mandatory tags
#

import oci
import json
import shapes
import logging

# Script configuation ###################################################################################

configfile = "c:\\oci\\config"  # Define config file to be used. 
AllPredefinedTags = True        # use only predefined tags from root compartment or include all compartment tags as well

# #######################################################################################################

#logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

class OCIobject(object):
    """__init__() functions as the class constructor"""
    def __init__(self, Service=None, OCID=None, Region=None, Name=None):
        self.Service = Service
        self.OCID = OCID
        self.Region = Region
        self.Name = Name

deleteList = []

def EvaluateInstances(instances, compartmentName, instancetype, regionname):
  print ("Checking " + instancetype + " instances in " + regionname + "-" + compartmentName)

  for instance in instances:
    
    tagtxt = "" 
    try:     
      namespaces = instance.defined_tags
      Tag1 = namespaces["Project"]["Owner"]
      Tag2 = namespaces["Project"]["OwnerEmail"]  
      # print (" --> OK Instance: " + instance.display_name)
    except:
      item = OCIobject(instancetype, instance.id, regionname, instance.display_name)
      deleteList.append(item)

customertags = []
config = oci.config.from_file(configfile)

identity = oci.identity.IdentityClient(config)
user = identity.get_user(config["user"]).data
RootCompartmentID = user.compartment_id
  
print ("Logged in as: {} @ {}".format(user.description, config["region"]))
print ("Querying Enabled Regions:")

response = identity.list_region_subscriptions(config["tenancy"])
regions = response.data


#Retrieve all instances for all enabled regions.

for region in regions:
  config = oci.config.from_file(configfile)
  config["region"] = region.region_name

  identity = oci.identity.IdentityClient(config)
  user = identity.get_user(config["user"]).data
  RootCompartmentID = user.compartment_id
 
  ComputeClient = oci.core.ComputeClient(config)
  NetworkClient = oci.core.VirtualNetworkClient(config)
  
  
  # Check instances for all the underlaying Compartments   
  response = oci.pagination.list_call_get_all_results(identity.list_compartments,RootCompartmentID,compartment_id_in_subtree=True)
  compartments = response.data

  # Insert (on top) the root compartment
  RootCompartment = oci.identity.models.Compartment()
  RootCompartment.id = RootCompartmentID
  RootCompartment.name = "root"
  RootCompartment.lifecycle_state = "ACTIVE"
  compartments.insert(0, RootCompartment)
  
  for compartment in compartments:
    compartmentName = compartment.name
    #print ("Checking : " + compartment.name)
    if compartment.lifecycle_state == "ACTIVE":
      compartmentID = compartment.id
      #try:
      response = oci.pagination.list_call_get_all_results(ComputeClient.list_instances,compartment_id=compartmentID)
      if len(response.data) > 0:
        EvaluateInstances(response.data, compartmentName, "Compute", region.region_name)
      #except:
      #  print ("Error?")

      databaseClient = oci.database.DatabaseClient(config)
      try:
        response = oci.pagination.list_call_get_all_results(databaseClient.list_db_systems,compartment_id=compartmentID)
        if len(response.data) > 0:
          EvaluateInstances(response.data, compartmentName, "DB", region.region_name)
      except:
        print ("Error?")

      try:
        response = oci.pagination.list_call_get_all_results(databaseClient.list_autonomous_data_warehouses,compartment_id=compartmentID)
        if len(response.data) > 0:
          EvaluateInstances(response.data, compartmentName, "ADW", region.region_name)
      except:
        print ("Error?")

      try:
        response = oci.pagination.list_call_get_all_results(databaseClient.list_autonomous_databases,compartment_id=compartmentID)
        if len(response.data) > 0:
          EvaluateInstances(response.data, compartmentName, "ATP", region.region_name)
      except:
        print ("Error?")
  break


    
print (" ")
print ("Instances that are missing mandatory tags:")
for i in deleteList:
  print (i.Name)

r = input ("Do you really want to delete these instances (y/n)?")

if r == "y" or r == "Y":
  print ("Starting delete process")
else:
  print ("Cancelled")










