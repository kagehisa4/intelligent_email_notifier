#import useful libraries
import imaplib
import email
from email.header import decode_header, make_header
import pandas as pd
import re
#import time

#This is optional only if you want to know the time requried to loop through the process.
#start = time.time()

# Input credentials to log into your email.
EMAIL= str(input('Enter your EMAIL: '))
PASSWORD = str(input('Enter your 16 letter IMAP login code: '))
SERVER = 'imap.gmail.com'

# Standard IMAP output is UTF-8 ENCODED.
# Use decode_text() to ASCII standrd text.
def decode_text(text):
    if not text:
        return ""
    return str(make_header(decode_header(text)))

#This decodes the sender as it is not present in HEADER.
def clean_sender(sender):
    match = re.search(r'<(.+?)>', sender)
    return match.group(1) if match else sender


#CONNECT TO IAMP SERVER VIA SECURE SOCKETS LAYER (YOU CAN ALSO USE HTTPS)
mail = imaplib.IMAP4_SSL(SERVER)

# LOGS INTO YOUR EMAIL ACCOUNT VIA CLI
mail.login(EMAIL, PASSWORD)


#To read only from inbox use this: mail.select('inbox')
#I need to fetch ALL Mail from Gmail to train the model so use this command to fetch All Emails.
mail.select('"[Gmail]/All Mail"')

#
status, data = mail.search(None, 'ALL')
mail_ids = data[0].split()


rows = []

print("Login successfull")
print(f"Total mails: {len(mail_ids)} ")

for i in mail_ids:
    status, msg_data = mail.fetch(i, '(BODY.PEEK[HEADER.FIELDS (FROM SUBJECT)] FLAGS)')

    for response_part in msg_data:
        if isinstance(response_part,tuple):
            msg = email.message_from_bytes(response_part[1])

            subject = decode_text(msg['subject'])
            sender = clean_sender(decode_text(msg['from']))

            # check if email is starred (flagged)
            #flags = msg.get('Flags', '')
            flags = response_part[0].decode()
            #print(str(flags))
            label = 1 if '\\Flagged' in str(flags) else 0
            #print(label)

            rows.append({
            "subject": subject,
            "sender": sender,
            "label": label
            })

mail.logout()
# create data Frame
df = pd.DataFrame(rows)
df.to_csv("emails_dataset.csv", index = False)
end = time.time()

#print(f'Time elapsed: {end-start:.2f}')
