import jwt, datetime, argparse, json

# Payload template example:
#
# { "sub": "admin", "iss": "/C=US/ST=Florida/L=Miami/O=Oracle/OU=OFSC COE/emailAddress=me@company.com,
# "aud": "ofsc:,instance_:_application_id_", "scope": "/REST", "exp": "<expiration timestamp>"
# }

def generate_assertion(key, payload):
    payload["exp"] = datetime.datetime.utcnow() + datetime.timedelta(minutes=60)
    encoded = jwt.encode(payload, private_key, algorithm='RS256')
    return encoded

parser = argparse.ArgumentParser(description='Create assertion key')
parser.add_argument ("key", help="RSA private key file")
parser.add_argument ("--payload", help="Payload template. Default: payload.sample", default="payload.sample")
parser.add_argument ("--subscriber", help="User. Default: admin")
args = parser.parse_args()

with open(args.key) as f:
    private_key = f.read()
with open(args.payload) as f:
    payload_template = json.load(f)
if args.subscriber:
    payload_template["sub"] = args.subscriber
assertion_key = generate_assertion(private_key, payload_template)
print("assertion: {}".format(assertion_key.decode("utf-8")))

print(payload_template)
