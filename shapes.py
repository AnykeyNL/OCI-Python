# Oracle OCI - Instance report script - Shaped definition
# Version: 1.4 29-November 2018
# Written by: richard@oc-blog.com
#

def ComputeShape(name):
    # returns OCPU count, Memory in GB and Local Storage in TB
    if name == "VM.Standard1.1":
        return 1, 7, 0
    elif name == "VM.Standard.E2.1":
        return 1, 8, 0
    elif name == "VM.Standard2.1":
        return 1, 15, 0
    elif name == "VM.Standard1.2":
        return 2, 14, 0
    elif name == "VM.Standard2.2":
        return 2, 30, 0
    elif name == "VM.Standard.E2.2":
        return 2, 16, 0
    elif name == "VM.Standard1.4":
        return 4, 28, 0
    elif name == "VM.Standard2.4":
        return 4, 60, 0
    elif name == "VM.Standard.E2.4":
        return 4, 32, 0
    elif name == "VM.Standard1.8":
        return 8, 56, 0
    elif name == "VM.Standard2.8":
        return 8, 120, 0
    elif name == "VM.Standard.E2.8":
        return 8, 64, 0
    elif name == "VM.Standard1.16":
        return 16, 112, 0
    elif name == "VM.Standard2.16":
        return 16, 240, 0
    elif name == "VM.Standard2.24":
        return 24, 320, 0
    elif name == "VM.DenseIO1.4":
        return 4, 60, 3.2
    elif name == "VM.DenseIO1.8":
        return 8, 120, 6.4
    elif name == "VM.DenseIO2.8":
        return 8, 120, 6.4
    elif name == "VM.DenseIO1.16":
        return 16, 240, 12.8
    elif name == "VM.DenseIO2.16":
        return 16, 240, 12.8
    elif name == "VM.DenseIO2.24":
        return 24, 320, 25.6
    elif name == "VM.GPU2.1":
        return 12, 104, 0
    elif name == "BM.GPU2.2":
        return 28, 192, 0
    elif name == "VM.CPU3.1":
        return 6, 90, 0
    elif name == "VM.CPU3.2":
        return 12, 180, 0
    elif name == "VM.CPU3.4":
        return 24, 360, 0
    elif name == "BM.CPU3.8":
        return 52, 768, 0
    elif name == "BM.Standard1.36":
        return 36, 256, 0
    elif name == "BM.Standard2.52":
        return 52, 768, 0
    elif name == "BM.StandardE2.64":
        return 64, 512, 0
    elif name == "BM.HighIO1.36":
        return 36, 512, 12.8
    elif name == "BM.DenseIO1.36":
        return 36, 512, 28.8
    elif name == "BM.DenseIO2.52":
        return 52, 768, 51.2
    elif name == "BM.HPC2.36":
        return 36, 384, 0
    elif name == "BM.RACLocalStorage1.72":
        return 72, 1024, 64
    elif name == "Exadata.Quarter1.84":
        return 84, 1440, 84
    elif name == "Exadata.Half1.168":
        return 168, 2880, 168
    elif name == "Exadata.Full1.336":
        return 336, 5760, 336
    elif name == "Exadata.Quarter2.92":
        return 92, 1440, 106
    elif name == "Exadata.Half2.184":
        return 184, 2880, 212
    elif name == "Exadata.Full12.368":
        return 368, 5760, 424
    
    else:
        return 0,0,0
    

