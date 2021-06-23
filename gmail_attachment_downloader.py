import os
from imbox import Imbox 
import traceback
import re
import requests
from bs4 import BeautifulSoup as bs
import datetime
# https://myaccount.google.com/lesssecureapps

host = "imap.gmail.com" #actual credentials below
username =
password =
download_folder = "H:\My Drive\_Brandons Carriers"
if not os.path.isdir(download_folder):
	os.makedirs(download_folder, exist_ok=True)

mail = Imbox(host, username=username, password=password, ssl=True, ssl_context=None, starttls=False)
#messages = mail.messages() # defaults to inbox
messages = mail.messages(sent_from='noreply@app.123formbuilder.com',date__gt=datetime.date(2021, 6, 15))
# date__lt = before and date__gt is after.

for (uid, message) in messages:
	#mail.mark_seen(uid) # optional, marks message as read
	txt = message.subject
	D = message.date
	M = message.sent_from
	fodder = txt.split('[mgmt] [xxBilling]') #weird cases from email
	fodderToStr = ' '.join(map(str,fodder))
	s = fodderToStr.split('Carrier Setup Package') #cuts out that word
	sToStr = ' '.join(map(str,s))
	t = sToStr.split('Carrier Setup\r\n Package')
	tToStr = ' '.join(map(str, t))
	u = tToStr.split('\r\n')
	cap =[i.upper()for i in u] #converts all to caps
	temp = [] 
	for element in cap:
		temp.append(element.strip()) # gets rid of weird cases
	captoStr = ' -'.join(map(str,temp))
	x = re.findall("[A-Z 0-9&]{3,}[^Carrier]",captoStr) 
	listtoStr = ' '.join(map(str,x))

	####DIRECTORY CREATION ####
	path = os.path.join(download_folder,listtoStr)
	mode = 0o777
	try:
		os.mkdir(path,mode)
		 # creates directory inside of folder based on name of email its "gaining"
	except:
		pass
		print(traceback.print_exc())

	####ATTACHMENT DOWNLOADER ####
	for idx, attachment in enumerate(message.attachments):
		try:
			att_fn = attachment.get('filename')
			download_path = f"{path}/{att_fn}"
			with open(download_path, "wb") as fp:
				fp.write(attachment.get('content').read())
		except:
			pass
			print(traceback.print_exc())
	
	####BODY READER ####
	links = [elem.strip().split('\r\n')for elem in message.body['html']]
	for index, b in enumerate(links):
		try:
			hyperlinks = re.findall("(?P<url>https?://[^\s]+)", str(b))
			filenames= re.findall("\w+\.pdf|\w+.jpg|\w+.png|\w+.jpeg",str(b))
			i = 0
			while (i < len(hyperlinks)):
				if i ==0:
					cut = re.findall("\.jpeg$|.pdf|.png|.jpg",str(filenames[i]))
					Coi= listtoStr + " _COI_ " +''.join(map(str,cut))
					download_link = f"{path}/{Coi}"
				if i == 1:
					cut = re.findall("\.jpeg$|.pdf|.png|.jpg",str(filenames[i]))
					Mca = listtoStr + "_Authority_" + ''.join(map(str,cut))
					download_link = f"{path}/{Mca}"
				if i == 2:
					cut = re.findall("\.jpeg$|.pdf|.png|.jpg",str(filenames[i]))
					W9 = listtoStr + "_W9_" + ''.join(map(str,cut))
					download_link = f"{path}/{W9}"
				if i == 3:
					cut = re.findall("\.jpeg$|.pdf|.png|.jpg",str(filenames[i]))
					Noa = listtoStr + "_NOA_" + ''.join(map(str,cut))
					download_link = f"{path}/{Noa}"
				r = requests.get(hyperlinks[i], allow_redirects=True)

				if r.status_code == 200:
					with open(download_link, 'wb') as fp:
						for data in r.iter_content(chunk_size=1024* 8):
							fp.write(data)
							fp.flush()
							os.fsync(fp.fileno())
				else:
					print("CANNOT DOWNLOAD FILE!! status code: {}\n{}".format(r.status_code,r.text))
				i += 1
		except:
			pass
			print(traceback.print_exc())

mail.logout()