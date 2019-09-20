#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import keyring
from lxml import html, etree


s = requests.session()

PERSON_CODE = "12345678" # Your person code
KC_ITM = "" # keychain item name for password (see below)
LOGIN = "https://aunicalogin.polimi.it/aunicalogin/aunicalogin/controller/IdentificazioneUnica.do?&jaf_currentWFID=main&polij_step=0&__pj0=0&__pj1=761e118900a1cef3835f8ba99c60c308"
SERVICE_URL = "https://servizionline.polimi.it/portaleservizi/portaleservizi/controller/preferiti/Preferiti.do?evn_srv=evento&idServizio=1156"

# Simulate the workflow of a human user so that Aunica doesn't get mad at us
s.get("https://www.polimi.it/servizionline")
s.post(LOGIN, data={
    "login": PERSON_CODE,
    "password": keyring.get_password(KC_ITM, PERSON_CODE), # Or just use getpass
    "evn_conferma": ""})
r = s.get(SERVICE_URL)

# There are probably much better ways of senting a form but who cares, this works
page = html.fromstring(r.text)
redir_url = page.xpath('//*[@id="automaticaRedirectForm"]/@action')[0]
sso_login = page.xpath('//*[@id="automaticaRedirectForm"]/input[1]/@value')[0]
matricola = page.xpath('//*[@id="automaticaRedirectForm"]/input[2]/@value')[0]
cookie = page.xpath('//*[@id="automaticaRedirectForm"]/input[3]/@value')[0]
impersonificato = page.xpath('//*[@id="automaticaRedirectForm"]/input[4]/@value')[0]
resta_connesso = page.xpath('//*[@id="automaticaRedirectForm"]/input[5]/@value')[0]
device = page.xpath('//*[@id="automaticaRedirectForm"]/input[6]/@value')[0]

r = s.post("https://aunicalogin.polimi.it/aunicalogin/" + redir_url, data={
    "SSO_LOGIN": sso_login,
    "MATRICOLA_SCELTA": matricola,
    "COOKIE_HCSS": cookie,
    "impersonificato": impersonificato,
    "RESTA_CONNESSO": resta_connesso,
    "polij_device_category": device})

page = html.fromstring(r.text)
info = page.xpath('/html/body/div/table[1]/tr/td[2]/form/table[6]')[0]
new_data = etree.tostring(info)

with open("data.html", "rb") as f:
    old_data = f.read()

if old_data != new_data:
    print("DATA UPADTED!") # Maybe replace with some logging
    # Do something with new_data...
    with open("data.html", "wb") as f:
        f.write(new_data)
else:
    print("No updates")
