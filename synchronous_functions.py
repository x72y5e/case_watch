import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from bs4 import BeautifulSoup as BS
import json
import re


def get_links(text):
    soup = BS(text, "html5lib")
    return set([x['href'] for x in soup.find_all('a')][10:30])  # TODO: change this


def get_extracts(text):
    pattern = re.compile(".*\[\d\d\d\d\].*")  # TODO: only capture a few sentences
    return re.findall(pattern, text)

def score_case(text):
    try:
        with open("config.json", "r") as f:
            terms = json.load(f)["terms"]
    except FileNotFoundError:
        print("error: configuration file not found.")
        return 0
    ext = get_extracts(text)
    print(ext)
    return sum([1 if term in text else 0 for term in terms]), get_extracts(text)


def get_urls():
    try:
        with open("config.json", "r") as f:
            urls = json.load(f)["url_list"]
            return set(urls)
    except FileNotFoundError:
        print("list of urls not found.")


def send_email(list_of_urls):
    try:
        with open("config.json", "r") as f:
            config = json.load(f)["email"]
            frm, to, server, pwd = config["from"], config["to"], config["server"], config["pwd"]
    except FileNotFoundError:
        print("Config file not found. Cannot send email.")
        return

    print("sending email...")

    sbj = "{} new case(s)".format(len(list_of_urls.split()))
    server = smtplib.SMTP(server[0], server[1])
    try:
        server.starttls()
        server.login(frm, pwd)  #"cywGTauk3LT4JC")
        msg = MIMEMultipart()
        msg['From'], msg['To'], msg['Subject'] = frm, to, sbj
        msg.attach(MIMEText(list_of_urls, "plain"))
        text = msg.as_string()
        server.sendmail(frm, to, text)
        server.quit()
        print("sent")
    except:
        print("{} error sending email".format(time.strftime(
            "%H:%M:%S", time.gmtime())))
        with open("failed.txt", "a") as f:
            f.write(list_of_urls)
