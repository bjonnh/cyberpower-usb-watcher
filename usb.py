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

class CyberPower:
    device = None
    def __init__(self, device):
        self.device = device

    def dict_status(self):

        return {
            "load": self.load(),
            "vin": self.vin(),
            "vout": self.vout(),
            "test": self.test(),
            "capacity": self.capacity(),
            "batterytype": self.batterytype(),
            "manufacturer": self.manufacturer(),
            "firmware": self.firmware(),
            "product": self.product(),
            **self.status(),
            **self.battery_runtime()
            }

    def iname(self):
        return self.device.get_feature_report(0x01,8)[1]

    def load(self):
        return self.device.get_feature_report(0x13,2)[1]
    def vout(self):
        return self.device.get_feature_report(0x12,3)[1]
    def vin(self):
        return self.device.get_feature_report(0x0f,3)[1]
    def test(self):
        return self.device.get_feature_report(0x14,2)[1]
    def battery_runtime(self):
        report = self.device.get_feature_report(0x08,6)
        return {"runtime":int((report[3]*256+report[2])/60),
                "battery": report[1]}

    def capacity(self):
        report = self.device.get_feature_report(0x18,6)
        return (report[2]*256+report[1])

    def product(self):
        return self.device.get_indexed_string(self.iname())

    def firmware(self):
        return self.device.get_indexed_string(2)

    def manufacturer(self):
        return self.device.get_indexed_string(3)

    def batterytype(self):
        return self.device.get_indexed_string(4)

    def status(self):
        status = self.device.get_feature_report(0x0b,3)[1]

        if status & 1:
            ac = True
        else:
            ac = False

        # Unclear if they can be together
        if status & 2:
            charge = True
        elif status & 4:
            charge = False
        else:
            charge = None

        belowcap = (status & 8) > 0
        full = (status & 16) > 0
        overtimelimit = (status & 16) > 0

        return {"ac": ac, "charge": charge, "belowcap": belowcap, "full": full,
                "overtimelimit": overtimelimit}
    def quick_status(self):
        read = self.device.read(1024)
        return {"battery": read[1], "runtime": int((read[3]*256+read[2])/60)}

def main():
    VENDOR_ID = 0x0764
    product_ids = [0x0501, 0x0601]
    for product_id in product_ids:
        device_list = hid.enumerate(VENDOR_ID, product_id)
        for device_item in device_list:
            device = hid.Device(path=device_item['path'])

            ups = CyberPower(device)
            # This crashes the hid library because some of these devices have no serial...
            #print("Serial Number: {}".format(device.))
            print(ups.dict_status())
            # If you just need the remaining time and battery charge
            # print(ups.quick_status())
            device.close()


if __name__ == "__main__":
    main()
