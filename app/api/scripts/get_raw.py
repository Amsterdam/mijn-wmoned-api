from sys import argv

from api.zorgned.zorgned_connection import ZorgNedConnection

import app.api.zorgned.zorgned_connection


bsn = argv[1]
app.api.zorgned.zorgned_connection.log_raw = True

con = ZorgNedConnection()
status, response = con.get_voorzieningen(bsn)
