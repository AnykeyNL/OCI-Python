import oci
import json



config = oci.config.from_file("c:\\oci\\config_frankfurt")

identity = oci.identity.IdentityClient(config)
user = identity.get_user(config["user"]).data
RootCompartmentID = user.compartment_id
  
print ("Logged in as: {} @ {}".format(user.description, config["region"]))
print (" ")

imageid = "ocid1.image.oc1.eu-frankfurt-1.aaaaaaaawpcm5l4noy5krzivbarnmeoyys6y2rzvjbursyshnkw6x2g5qvba"
desturl = "https://objectstorage.us-phoenix-1.oraclecloud.com/p/NGzKrpuDI6i00VwZYEJJGp4zJse-0WYCB2AYGyDAKOE/n/pi3dscan/b/MyBucketUS/o/test2"

ComputeClient = oci.core.ComputeClient(config)

imagedetail = oci.core.models.export_image_via_object_storage_uri_details
imagedetail.ExportImageViaObjectStorageUriDetails.destination_uri = desturl

result = ComputeClient.export_image(imageid, imagedetail)









                                      


                                       
