#  Copyright 2019 Jonathan Bisson
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import hid

#device = hid.device()

VENDOR_ID = 0x0764
PRODUCT_ID = 0x0601
device_list = hid.enumerate(VENDOR_ID, PRODUCT_ID)



# Report Descriptor bLength 9
# 1 descriptor of type 34, report
# Descriptor length = 656

def get_report(device, code):
    return device.read(code)

class CyberPower:
    device = None
    def __init__(self, device):
        self.device = device
    def load(self):
        return self.device.get_feature_report(0x13,2)[1]
    def vout(self):
        return self.device.get_feature_report(0x12,3)[1]
    def vin(self):
        return self.device.get_feature_report(0x0f,3)[1]
    def test(self):
        return self.device.get_feature_report(0x14,2)[1]
    def battery(self):
        return self.device.get_feature_report(0x08,6)[1]
    def runtime(self):
        report = self.device.get_feature_report(0x08,6)
        return int((report[3]*256+report[2])/60)
    def capacity(self):
        report = self.device.get_feature_report(0x18,6)
        return (report[2]*256+report[1])
    def status(self):
        status = self.device.get_feature_report(0x0b,3)[1]

        if status & 1:
            ac = "ON"
        else:
            ac = "OFF"

        # Unclear if they can be together
        if status & 2:
            charge = True
        elif status & 4:
            charge = False
        else:
            charge = None
        belowcap = (status & 8) > 0

        full = (status & 16) > 0
                
        return {"ac": ac, "charge": charge, "belowcap": belowcap, "full": full}


for device_item in device_list:
    print("Manufacturer: {}".format(device_item['manufacturer_string']))
    print("Product: {}".format(device_item['product_string']))

    device = hid.device()
    device.open_path(device_item['path'])
    ups = CyberPower(device)
    print(device.get_serial_number_string())
    print(" Status: {}".format(ups.status()))
    print(" Load: {}%".format(ups.load()))
    print(" Voltage: IN={}V OUT={}V".format(ups.vin(), ups.vout()))
    print(" Battery: {}% Runtime: {} min".format(ups.battery(), ups.runtime()))
    print(" Capacity: {} VA".format(ups.capacity()))
    device.close()
