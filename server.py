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

from usb import CyberPower
import hid
from http.server import HTTPServer, BaseHTTPRequestHandler


def catch():
    output = ""
    VENDOR_ID = 0x0764
    PRODUCT_ID = 0x0601
    device_list = hid.enumerate(VENDOR_ID, PRODUCT_ID)
    for device_item in device_list:
        device = hid.Device(path=device_item['path'])
        ups = CyberPower(device)
        res = ups.dict_status()
        firmware = res["firmware"]
        for key,value in res.items():
            if value in [True,False]:
                value = int(value == True)
            if isinstance(value, int):
                output += "ups_{}{{firmware=\"{}\"}} {}\n".format(key, firmware, value)
        device.close()
    return output.encode("ascii")

class CatchHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/metrics":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(catch())

def run(server_class=HTTPServer, handler_class=CatchHandler):
    server_address = ('127.0.0.1', 9500)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()

if __name__ == "__main__":
    run()
