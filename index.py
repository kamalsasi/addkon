#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys,redis,re,time
reload(sys)
sys.setdefaultencoding("utf-8")
from telebot import TeleBot, types 

TOKEN = '403206452:AAGdunivaXO6ujyEsadcX5sbm_AqlOuD8mU' #yourbottokenkey
naji = 296805034 #yourid

bot = TeleBot(TOKEN,threaded=False)
redis = redis.StrictRedis(host='localhost', port=6379, db=9,  decode_responses=True)
bot_id = bot.get_me().id

def allowed(msg) :
	admin = bot.get_chat_member(msg.chat.id, msg.from_user.id)
	if admin.status == 'creator' or admin.status == 'administrator':
			return True
	elif msg.from_user.id == naji:
		return True
	elif int(redis.hget(msg.chat.id, msg.from_user.id) or 0) > int(redis.hget(msg.chat.id, "limit") or 1) :
		return True
	else:
		return False
		
def gp(msg) : 
	return msg.chat.type == 'supergroup' or msg.chat.type == 'group'
def pv(msg) : 
	return msg.chat.type == 'private'

@bot.message_handler(func=pv, content_types=['text', 'audio', 'document', 'gif', 'photo', 'sticker', 'video', 'voice', 'location', 'contact','game','video_note'])
def personal(msg):
	try:
		if msg.from_user.id == naji and msg.text:
			if re.match("/fwd", msg.text) and msg.reply_to_message:
				for i in redis.smembers("bot:all", msg.chat.id):
					try:
						bot.forward_message(i, msg.chat.id, msg.reply_to_message.id)
					except Exception as e:
						print(e)
						
			if re.match("/stats", msg.text):
				bot.send_message(msg.chat.id, "آمار\nگروه ها : {}\nخصوصی ها : {}".format(redis.scard("bot:gps"), redis.scard("bot:pvs")))
		else:
			bot.send_message(msg.chat.id,"رباتی برای افزایش اعضای گروه\nفقط کافیه به گروهت دعوتش کنی و ادمینش کنی")
			if not redis.sismember("bot:all", msg.chat.id):
				redis.sadd("bot:pvs", msg.chat.id)
				redis.sadd("bot:all", msg.chat.id)
			
	except Exception as e:
		print(e)
		pass
	
	
@bot.message_handler(func=gp, content_types=['text', 'audio', 'document', 'gif', 'photo', 'sticker', 'video', 'voice', 'location', 'contact','game','video_note'])
def main(msg):
	if not redis.sismember("bot:all", msg.chat.id):
		redis.sadd("bot:gps", msg.chat.id)
		redis.sadd("bot:all", msg.chat.id)
	try:
		if msg.text and re.match("^[!#/][Ss]etlimit", msg.text):
			admin = bot.get_chat_member(msg.chat.id, msg.from_user.id)
			max = re.search("(\d+)", msg.text).group(1)
			if (admin and admin.status == 'creator' or msg.from_user.id == naji) and max:
				redis.hset(msg.chat.id, "limit", int(max))
				bot.reply_to(msg, "🍃 افزودن {} عضو جهت رفع محدودیت در گفتوگو ثبت شد 🍃".format(max))
		
		if not allowed(msg):
			name = msg.from_user.last_name and msg.from_user.first_name + msg.from_user.last_name or msg.from_user.first_name
			try:
				if redis.hget(msg.from_user.id, msg.chat.id):
					try:
						bot.delete_message(msg.chat.id, redis.hget(msg.from_user.id, msg.chat.id))
					except Exception as e:
						print(e)
				bot.delete_message(msg.chat.id, msg.message_id)
			except Exception as e:
				print(e)
				return ""
			finally:
				pm = bot.send_message(msg.chat.id, "🌺 کاربر عزیز {} 🌺\nهر عضو گروه موظفه {} نفرو به گروه اضافه کنه تا بتونه چت کنه 😅\n\nتعداد اعضا افزوده شده توسط شما : 💫 {}💫".format(name, redis.hget(msg.chat.id, "limit") or 1, redis.hget(msg.chat.id, msg.from_user.id) or 0))
				redis.hset(msg.from_user.id, msg.chat.id, pm.message_id)
	except Exception as e:
		print(e)
		pass
		
@bot.message_handler(content_types=['new_chat_members', 'left_chat_member'])
def add(msg):
	if msg.left_chat_member:
		redis.hdel(msg.chat.id, msg.left_chat_member.id)
	elif msg.new_chat_members:
		for user in  msg.new_chat_members:
			if 'username' in user and user['username'].lower().endswith("bot"):
				return
			else:
				redis.hincrby(msg.chat.id, msg.from_user.id, 1)

bot.polling(none_stop=True)	