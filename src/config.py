from dotenv import load_dotenv
import os
import getpass

load_dotenv()

COUNTRY = os.getenv("COUNTRY", "United Kingdom")
SEARCH_TERM = os.getenv("SEARCH_TERM", "visa sponsorship")
USE_PERSISTENT_BROWSER = os.getenv("USE_PERSISTENT_BROWSER", "False") == "True"
BROWSER = os.getenv("BROWSER", "EDGE").upper()
WAIT_TIME = float(os.getenv("WAIT_TIME", 3))
DEBUG = os.getenv("DEBUG", "False") == "True"
FROM_AGE = int(os.getenv("FROM_AGE", 14))

CURRENT_USER = getpass.getuser()
BROWSER_PROFILE_PATH = f"C:/Users/{CURRENT_USER}/AppData/Local/RPA_Browser_Profile"
