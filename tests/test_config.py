import os
from dotenv import load_dotenv

# SBR Configuration
def test_sbr_config() -> None:
    # TODO: Complete this function to test if sessions can be created
    load_dotenv()
    SBR_WEBDRIVER = os.getenv('SBR_WEBDRIVER')