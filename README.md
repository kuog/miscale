Parse Xiaomi Mi Scale BLE protocol and provide access to stored weight data.

To get base device information:
```
usage: miscale_info.py [-h] [-b BTADDR] [-d DEVICE] [-l]

MI_SCALE base info

optional arguments:
  -h, --help            show this help message and exit
  -b BTADDR, --btaddr BTADDR
                        target BTADDR in XX:XX:XX:XX:XX:XX format
  -d DEVICE, --device DEVICE
                        hci device name (e.g. hci0)
  -l, --listen          listen to advertises
```

Analyze BLE pcap file captures with Ubertooth:
```
usage: miscale_analyzer.py [-h] [-u USER_ID] [-c PCAP_FILE]

BLE MI_SCALE protocol analyzer

optional arguments:
  -h, --help            show this help message and exit
  -u USER_ID, --user USER_ID
                        user id
  -c PCAP_FILE, --capture PCAP_FILE
                        pcap file
```

To read weight data from the scale:
```
usage: miscale_poll.py [-h] [-u USER_ID] [-d DEVICE_MAC]

MI_SCALE requester

optional arguments:
  -h, --help            show this help message and exit
  -u USER_ID, --user USER_ID
                        user id
  -d DEVICE_MAC, --device DEVICE_MAC
                        target MAC address
```
