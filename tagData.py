import instanceMetadata
import oci
import json
import os


md = instanceMetadata.get_metadata()

print ("Instance ID: {}".format(md["displayName"]))
print ("Location   : {}".format(md["availabilityDomain"]))
print ("Region     : {}".format(md["canonicalRegionName"]))

print (" ")
print (md)
print (" ")


configfile = "~/config"
var_prefix = "oci_"

config = oci.config.from_file(configfile)
config["region"] = md["canonicalRegionName"]

identity = oci.identity.IdentityClient(config)
user = identity.get_user(config["user"]).data
RootCompartmentID = user.compartment_id

print ("Logged in as: {} @ {}".format(user.description, config["region"]))

try:
  ComputeClient = oci.core.ComputeClient(config)
  response = ComputeClient.get_instance(instance_id = md["id"] )
  print (response.data)
except:
  print ("Not a compute instance")


try:
  databaseClient = oci.database.DatabaseClient(config)
  response = databaseClient.get_db_system(db_system_id = md["displayName"])
  print (response.data)
except:
  print ("Not a database instance")


for def_tags in response.data.defined_tags:
  prefix = def_tags
  tags = response.data.defined_tags[def_tags]
  for tag in tags:
    varname =  var_prefix + prefix + "_" + tag
    varvalue = "\"" + tags[tag] + "\""
    os.environ[varname] = varvalue
    print (varname + " = " + varvalue)


print (os.environ)


