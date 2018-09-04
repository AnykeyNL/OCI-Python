import instanceMetadata

md = instanceMetadata.get_metadata()

print ("Instance ID: {}".format(md["id"]))
print ("Location   : {}".format(md["availabilityDomain"]))


