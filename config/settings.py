import os
from dotenv import load_dotenv

load_dotenv()

NAUKRI_EMAIL = os.getenv("NAUKRI_EMAIL")
NAUKRI_PASSWORD = os.getenv("NAUKRI_PASSWORD")

JOB_KEYWORDS = os.getenv("JOB_KEYWORDS", "automation architect")
JOB_LOCATION = os.getenv("JOB_LOCATION", "Bengaluru")
JOB_EXPERIENCE = os.getenv("JOB_EXPERIENCE", "10")