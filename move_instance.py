import oci
import time

configs = ["c:\\oci\\config_frankfurt","c:\\oci\\config_phoenix","c:\\oci\\config_ashburn"] # Define config files to be used. You will need a seperate config file per region and/or account

config = oci.config.from_file(configs[0])

identity = oci.identity.IdentityClient(config)
user = identity.get_user(config["user"]).data
RootCompartmentID = user.compartment_id
  
print ("Logged in as: {} @ {}".format(user.description, config["region"]))
print (" ")

CompartmentID = "ocid1.tenancy.oc1..aaaaaaaar75ibn2rpvcnfolldaicsvl24kew3455f7tvnotuabkq7wnlphaa"
#VMID = "ocid1.instance.oc1.eu-frankfurt-1.abtheljrclqn2alu3oftkykpxjtxpcrlxqtllplwy3anc2qt2mmvjhh3axda"
VMID = "ocid1.instance.oc1.eu-frankfurt-1.abtheljr5kai22sy542s5tbwclyru3hd6ovxojf6mdfq24axadxgbpvfzejq"


ComputeClient = oci.core.ComputeClient(config)

#imageDetails = oci.core.models.CreateImageDetails(compartment_id = CompartmentID, instance_id=VMID, display_name="TempOS2")
#response = ComputeClient.create_image(imageDetails)
#print (response.data)


#time.sleep(5)
#image_ocid = response.data.id
image_ocid = "ocid1.image.oc1.eu-frankfurt-1.aaaaaaaaxtqdfesp5veja6x2vbvxe3ufvyn6mhxnldtk2wp4trsbdzlbmcrq"
state = ""
while state != "AVAILABLE":
    response = ComputeClient.get_image(image_ocid)
    state = response.data.lifecycle_state
    print (response.data)
    time.sleep(5)

print ("DONE!")







#get_instance_response = oci.wait_until(client, client.get_instance(instance_ocid), 'lifecycle_state', 'RUNNING')





