import time
import random
import json

import telebot
import requests
from pyqiwip2p import QiwiP2P

import config as cfg


def main():
	print('Run bot check_girl')

	bot = telebot.TeleBot(cfg.TELE_TOKEN)
	
	#кнопка пополнения счета
	top_up_button = telebot.types.InlineKeyboardMarkup()
	top_up_button.add(telebot.types.InlineKeyboardButton(text='Полполнить счет', callback_data='top_up'))

	keyboard_pay_one = telebot.types.InlineKeyboardMarkup()
	keyboard_pay_one.add(telebot.types.InlineKeyboardButton(text='Купить подписку', callback_data='buy_sub_callback'))
	keyboard_pay_one.add(telebot.types.InlineKeyboardButton(text='Купить фотографию', callback_data='buy_photo'))

	back_menu = telebot.types.InlineKeyboardMarkup()
	back_menu.add(telebot.types.InlineKeyboardButton(text='Главное меню', callback_data='main_menu'))


	@bot.callback_query_handler(func=lambda call: True)
	def call_get(call):
		if call.data == 'main_menu':
		
			menu1 = telebot.types.InlineKeyboardMarkup()
			menu1.add(telebot.types.InlineKeyboardButton(text='Проверить девушку', callback_data='check_girl_callback'))
			menu1.add(telebot.types.InlineKeyboardButton(text='Купить подписку', callback_data='buy_sub_callback'))

			with open("db.json", 'r') as json_file:
				js = json.load(json_file)
				
				for user in js:
					try:
						if str(user['user']) == str(call.message.chat.id):
							
							hello_text = f"Главное меню\n\nБаланс: {str(user['balance'])} руб"
							bot.send_message(call.message.chat.id, text=hello_text, reply_markup=menu1)
							vartf = True
							break
					except Exception as e:
						print(e)


		if call.data == 'protect':
			mess = bot.send_message(call.message.chat.id, "Введите ссылку на страницу")
			bot.register_next_step_handler(mess, prot_func)
		if "checkPay" in str(call.data):
			
			check_payment = str(call.data[8:])

			p2p = QiwiP2P(auth_key=cfg.QIWI_TOKEN)
			tf = p2p.check(bill_id=check_payment).status
			#tf = "PAID"
			if str(tf) == "WAITING":
				bot.send_message(call.message.chat.id, 'Вы еще не оплатили')
			
			if str(tf) == "PAID":
				
				key_1 = telebot.types.InlineKeyboardMarkup()
				key_1.add(telebot.types.InlineKeyboardButton(text='Раздел защиты', callback_data='protect'))
				bot.send_message(call.message.chat.id, 'Фото защищены, просмотр невозможен. Если вы хотите скрыть себя - перейдите в раздел защиты', reply_markup=key_1)

		if call.data == 'buy_photo':
			try:
				p2p = QiwiP2P(auth_key=cfg.QIWI_TOKEN)
				comment = "checkGirl:"+str(random.randint(100000, 999999))
				bill = p2p.bill(amount=10, lifetime=30, comment=comment)
				check_pay = telebot.types.InlineKeyboardMarkup()
				check_pay.add(telebot.types.InlineKeyboardButton(text='Проверить оплату', callback_data='checkPay'+str(bill.bill_id)))
				bot.send_message(call.message.chat.id, text="На оплату 10 руб\nСсылка для оплаты будет доступна 30 минут: "+str(bill.pay_url), reply_markup=check_pay)

			except Exception as e:
				print(e)
				bot.send_message(call.message.chat.id, text="Что-то пошло не так, возможно вы не правильно ввели сумму")

		if call.data == 'check_girl_callback':
			bot.send_message(call.message.chat.id, "Введите ссылку на страницу ВК девушки")

		if call.data == 'top_up':
			try:
				p2p = QiwiP2P(auth_key=cfg.QIWI_TOKEN)
				comment = "checkGirl:"+str(random.randint(100000, 999999))
				bill = p2p.bill(amount=20, lifetime=30, comment=comment)

				check_pay = telebot.types.InlineKeyboardMarkup()
				check_pay.add(telebot.types.InlineKeyboardButton(text='Проверить оплату', callback_data='checkPay'+str(bill.bill_id)))

				bot.send_message(call.message.chat.id, text="На оплату 20 руб\nСсылка для оплаты будет доступна 30 минут: "+str(bill.pay_url), reply_markup=check_pay)
			except Exception as e:
				print(e)
				bot.send_message(call.message.chat.id, text="Что-то пошло не так, возможно вы не правильно ввели сумму")

		if call.data == 'buy_sub_callback':
			with open("db.json", 'r') as json_file:
				js = json.load(json_file)
				for user in js:
					try:
						if str(user['user']) == str(call.message.chat.id):
							if user['balance'] >= 20:
								user['balance'] = user['balance'] - 20
								user['subscribe'] = True 
								with open("db.json", 'w') as js_file:
									json.dump(js, js_file, indent=4)
									bot.send_message(call.message.chat.id, 'Подписка оформлена')
							elif user['balance'] < 20:
								bot.send_message(call.message.chat.id, text='На вашем счете недостаточно средств\n', reply_markup=top_up_button)
					except:
						pass
	

	def prot_func(message):
		if "https://vk.com/" in str(message.text):
			bot.send_message(message.chat.id, 'Запрос принят. Удалим фото из базы в течение 10 рабочих дней', reply_markup=back_menu)
						
	#Старт клиента
	@bot.message_handler(commands=['start'])
	def sending(message):
		#кнопки
		menu1 = telebot.types.InlineKeyboardMarkup()
		menu1.add(telebot.types.InlineKeyboardButton(text='Проверить девушку', callback_data='check_girl_callback'))
		menu1.add(telebot.types.InlineKeyboardButton(text='Купить подписку', callback_data='buy_sub_callback'))

		vartf = False
		with open("db.json", 'r') as json_file:
			js = json.load(json_file)

			for user in js:
				try:
					if str(user['user']) == str(message.chat.id):
						hello_text = f"Здравствуйте, {message.from_user.username}\n\nБаланс: {str(user['balance'])} руб"
						bot.send_message(message.chat.id, text=hello_text, reply_markup=menu1)
						vartf = True
						break
				except:
					pass

		if vartf == False:
				
			js.append({"user": str(message.chat.id), "balance": 0, "subscribe": False})
				
			with open("db.json", 'w') as js_file:
				json.dump(js, js_file, indent=4)




	@bot.message_handler(content_types =['text'])
	def check_url(message):
		
		if "https://vk.com/" in message.text:
			
			req = requests.get(url=str(message.text))
			
			#проверка статус-кода
			if req.status_code == 200:
				
				rand = random.randint(1, 10)

				bot.send_message(message.chat.id, "Подождите, идет поиск")
				
				time.sleep(3)

				
				if rand > 5:
					
					randpic = random.randint(1, 6)
					pic = str(randpic) + '.png'

					pic = open('pics/'+pic, 'rb')
					text_for = "Фотография найдена\n У вас нет подписки, чтобы получить полную версию фотографии оплатите подписку (20руб) или одноразово получите фотографию (10руб)"
					bot.send_photo(message.chat.id, caption=text_for, photo=pic, reply_markup=keyboard_pay_one)   #если фото найдено

				
					
				elif rand < 5:

					bot.send_message(message.chat.id, "Фотография не найдена, попробуйте другую ссылку")   #если фото не найдено
					
			else:
				
				bot.send_message(message.chat.id, "Страница не найдена, попробуйте еще раз")	
		
		else:
			
			bot.send_message(message.chat.id, "Попробуйте ввести ссылку") #проверка валидности страницы (не верно введено)


	bot.polling()

if __name__ == "__main__":
	while True:
		try:
			main()
		except Exception as e:
			print(e)
