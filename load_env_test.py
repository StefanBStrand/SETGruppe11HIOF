import os
from dotenv import load_dotenv

# Eksplisitt last inn .env-filen
dotenv_path = os.path.join(os.getcwd(), '.env')
load_dotenv(dotenv_path)

# Test lesing av SECRET_KEY
secret_key = os.getenv("SECRET_KEY")
if secret_key:
    print(f"SECRET_KEY: {secret_key}")
else:
    print("SECRET_KEY not found!")

