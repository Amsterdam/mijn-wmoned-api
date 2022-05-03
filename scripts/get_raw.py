from sys import argv
import json
from app.zorgned_service import get_persoonsgegevens, get_voorzieningen

bsn = argv[1]

response = get_voorzieningen(bsn)
# response = get_persoonsgegevens(bsn)

print("\n\n\nResponse.v2\n\n\n")
print(json.dumps(response, indent=4))
print("\n\n\nend.Response.v2\n\n\n")
