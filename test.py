from wakeonlan import send_magic_packet
#
# send_magic_packet("58-1C-F8-C6-BA-1F",
#                   ip_address="10.4.215.161")

send_magic_packet("10-7B-44-50-EF-D1",
                  ip_address="49.37.160.13",port=9)

print("Hello world")