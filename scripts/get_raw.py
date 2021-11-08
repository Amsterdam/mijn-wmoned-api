from sys import argv

from app.server import get_voorzieningen


bsn = argv[1]

status, response = get_voorzieningen(bsn)

print("Response.v2", status)
print(response)
