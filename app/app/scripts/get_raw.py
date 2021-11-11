from sys import argv

from app.zorgned.zorgned_connection import ZorgNedConnection

import app.zorgned.zorgned_connection


bsn = argv[1]
app.zorgned.zorgned_connection.log_raw = True

con = ZorgNedConnection()
status, response = con.get_voorzieningen(bsn)
