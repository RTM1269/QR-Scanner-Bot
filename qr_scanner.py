# -*- coding: utf-8 -*-

# Telegram
from queue import Empty
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, Filters, MessageHandler, CallbackContext

# QR Code
from pyzbar.pyzbar import decode

# System libraries
import os
import json
from os import listdir
from os.path import isfile, join

from io import BytesIO
from PIL import Image
#  decode
import sys
import zlib
import pprint
import argparse

import PIL.Image
import pyzbar.pyzbar
import base45
import cbor2
from cose.messages import CoseMessage

#MongoDB
import pymongo


client = pymongo.MongoClient("mongodb+srv://userApp:ncqG7aQ5xUn9z5xY@trabajopython.1sosg.mongodb.net/TrabajoPython?retryWrites=true&w=majority", server_api=ServerApi('1'))
db = client.test


TOKEN = "5130549589:AAHSV6Hhp7SM68DYI47TQSu7qZ9h0U76dCE"

def decode_qr(update: Update, context: CallbackContext):
	chat_id = update.message.chat_id

	if update.message.photo:
		id_img = update.message.photo[-1].file_id
	else:
		return

	foto = context.bot.getFile(id_img)

	new_file = context.bot.get_file(foto.file_id)
	new_file.download('qrcode.png')
	print(new_file)
	try:
		result = decode(PIL.Image.open('qrcode.png'))
		
		cert = result[0].data.decode()
		# print(cert)
		# certificado = "{""dcc"":" + cert + "}"
		# certificado = "{"""+f'dcc"":{cert}' + "}"
		cert = cert.replace("HC1:", "")
		decoded = base45.b45decode(cert)
		decompressed = zlib.decompress(decoded)
		cose = CoseMessage.decode(decompressed)
		print(json.dumps(cbor2.loads(cose.payload), indent=2))

		b45data = cert.replace("HC1:", "")
		zlibdata = base45.b45decode(b45data)
		# print(zlibdata)
		cbordata = zlib.decompress(zlibdata)
		# print(cbordata)
		decoded = cbor2.loads(cbordata)
		print(len(json.dumps(cbor2.loads(cose.payload), indent=2))>0)
		# print(result[0].data)  ["-260"]["1"]["nam"]["fn"]
		if len(json.dumps(cbor2.loads(cose.payload), indent=2))>0 and json.dumps(cbor2.loads(cose.payload), indent=2).__contains__("ci"):
			context.bot.sendMessage(chat_id=chat_id, text="Su certificado es válido")
		else:
			# context.bot.sendMessage(chat_id=chat_id, text=result[0].data.decode("utf-8"))
			# context.bot.sendMessage(chat_id=chat_id, text=json.dumps(cbor2.loads(cose.payload), indent=2))
			context.bot.sendMessage(chat_id=chat_id, text="Su certificado no es correcto")

		os.remove("qrcode.png")
	except Exception as e:
		context.bot.sendMessage(chat_id=chat_id, text="Su código QR no es correcto")

# def verify():



def main():
	updater = Updater(TOKEN, request_kwargs={'read_timeout': 20, 'connect_timeout': 20}, use_context=True)
	dp = updater.dispatcher

	dp.add_handler(MessageHandler(Filters.photo, decode_qr))

	updater.start_polling()
	updater.idle()

if __name__ == '__main__':
	main()
