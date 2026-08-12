import os
required = ["API_ID","API_HASH","SESSION_STRING","OWNER_ID"]
missing = [x for x in required if not os.getenv(x)]
print("Missing: "+", ".join(missing) if missing else "Required environment variables are present.")
