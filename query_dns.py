import dns
from dns import message, query
import pyshark
import sys

if not sys.argv[1:]:
    print("Sample Usage : "+sys.argv[0]+" <dns server> <server to query> <protocol> <iteration>")
    exit()

# Read the arguments from the user.
try:
    dns_server = sys.argv[1]
    server_to_query = sys.argv[2]
    protocol = sys.argv[3]
    iteration = int(sys.argv[4])

except Exception as e:
    print("Please check no of arguments.")
    exit()

qname = dns.name.from_text(server_to_query)

query_object = dns.message.make_query(qname,dns.rdatatype.A)

for i in range(0,iteration):
    if protocol == "udp":
        try:
            print("Using udp.")
            udp_response = dns.query.udp(query_object,dns_server,raise_on_truncation=True,timeout=10)
            print(udp_response)
        except Exception as e:
            print("Exception while running query ... " + str(e))
    else:
        try:
            print("using tcp.")
            tcp_response = dns.query.tcp(query_object,dns_server,timeout=10)
            print(tcp_response)
        except Exception as e:
            print("Exception while making tcp query ... " + str(e))

