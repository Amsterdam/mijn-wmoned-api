from sys import argv

from api.zorgned.zorgned_connection import ZorgNedConnection

import api.zorgned.zorgned_connection


bsn = argv[1]
api.zorgned.zorgned_connection.log_raw = True

con = ZorgNedConnection()

cert_override = "./client.pem"
status, response = con.get_voorzieningen_v2(bsn, cert_override)

print(status, response)
