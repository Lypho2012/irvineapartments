from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup
from datetime import datetime

import base64
from email.message import EmailMessage

import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import os
from dotenv import load_dotenv

def get_latest_movein(url,plan,driver):
    driver.get(url)

    #click to expand plan
    try:
        expand_button = driver.find_element(By.CSS_SELECTOR,f"[aria-label='{plan}']")
        expand_button.click() 
    except:
        return "None"
    driver.implicitly_wait(10)
    driver.execute_script("window.scrollTo(0, 850)")

    #click apply
    apply_buttons = driver.find_elements(By.XPATH,"//*[contains(text(), 'APPLY NOW')]")
    days = set()
    for index,apply_button in enumerate(apply_buttons):
        try:
            apply_button.click()
            driver.implicitly_wait(10)
            soup = BeautifulSoup(driver.page_source, 'html5lib')
            results = soup.find_all("span", attrs = {'class':'flatpickr-day','tabindex':'-1'})
            for res in results:
                days.add(res['aria-label'])
        except:
            continue

        # click on expected movein
        try:
            movein_button = driver.find_element(By.CSS_SELECTOR,"[for='hold-form-leasedate']")
            movein_button.click()
            driver.implicitly_wait(10)
            driver.set_window_size(1280, 800)
            driver.maximize_window()
            driver.implicitly_wait(10)
        except:
            # print("Didn't click expected movein")
            pass

        #click to last month for movein date
        next_buttons = driver.find_elements(By.CLASS_NAME,"flatpickr-next-month")
        for next_button in next_buttons:
            try:
                next_button = WebDriverWait(driver, 15).until(EC.element_to_be_clickable(next_button))
                next_button.click()
                driver.implicitly_wait(10)
                soup = BeautifulSoup(driver.page_source, 'html5lib')
                results = soup.find_all("span", attrs = {'class':'flatpickr-day','tabindex':'-1'})
                for res in results:
                    days.add(res['aria-label'])
            except:
                # print("next button didn't work")
                continue

    days = list(days)
    days.sort(key=lambda x: datetime.strptime(x, "%B %d, %Y"))
    return days[-1] if len(days) > 0 else "None"

def gmail_send_message(content):
    """
    Google Cloud project ID: irvineapartments
    gcloud init
    gcloud auth application-default login
    https://cloud.google.com/docs/authentication/provide-credentials-adc#how-to 
    """
    # creds, _ = google.auth.default()
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", ["https://www.googleapis.com/auth/gmail.send"])
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "client_secret_1068627222746-5m9ojctormoh4s0mbi97657b2osoc9p2.apps.googleusercontent.com.json", 
                ["https://www.googleapis.com/auth/gmail.send"],
                redirect_uri="http://localhost:62314/"
            )
            creds = flow.run_local_server(port=62314)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    try:
        service = build("gmail", "v1", credentials=creds)
        message = EmailMessage()

        message.set_content(content)

        load_dotenv()
        email = os.getenv('EMAIL')

        message["To"] = email
        message["From"] = email
        message["Subject"] = "Irvine Company Apartments listing report"

        # encoded message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        create_message = {"raw": encoded_message}
        # pylint: disable=E1101
        send_message = (
            service.users()
            .messages()
            .send(userId="me", body=create_message)
            .execute()
        )
        print(f'Message Id: {send_message["id"]}')
    except HttpError as error:
        print(f"An error occurred: {error}")
        send_message = None
    return send_message
