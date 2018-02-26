# -*- coding: utf-8 -*-
import hashlib
import web
import lxml
import time
import os
import urllib2,json
from lxml import etree
from xiaohua import getxh
from tianqi import tqyb
from tuling import jqr
from getwxtoken import wxtoken
import md5
import pylibmc
import json

class WeixinInterface(object):
	def __init__(self):
		self.app_root = os.path.dirname(__file__)
		self.templates_root = os.path.join(self.app_root,'templates')
		self.render = web.template.render(self.templates_root)
		self.mylocation = pylibmc.Client()


	def getlocations(self):
		location = self.mylocation.get('mylocation')
		if location == None:
			return []
		else:
			return location

	def GET(self):
		try:
			data = web.input()
			if len(data) == 0:
				return 'hello,this is handle view'
			signature = data.signature
			timestamp = data.timestamp
			nonce = data.nonce
			echostr = data.echostr
			token = 'weixinlz'

			list = [token,timestamp,nonce]
			list.sort()
			sha1 = hashlib.sha1()
			map(sha1.update,list)
			hashcode = sha1.hexdigest()

			if hashcode == signature:
				return echostr
			else:
				return 'hello word'

		except Exception,Argument:
			try:
				data = web.input()
				if len(data) == 0:
					return 'hello,this is handle view'
				if str(data.type) == 'push':#接受
					latitude = data.latitude
					longitude = data.longitude
					address = data.address
					location = {'address':address, 'latitude':latitude, 'longitude':longitude}
					newlcoations = self.getlocations()
					newlcoations.append(location)
					self.mylocation.set('mylocation',newlcoations)
					return json.dumps(self.getlocations())
				elif str(data.type) == 'get':#获取
					return json.dumps(self.getlocations())
				elif str(data.type) == 'delete':#删除
					return self.mylocation.delete('mylocation')

			except :
				return 'chucuole'

			return 'chucuole'
		
			


	def POST(self):
		try:
			str_xml = web.data()
			xml = etree.fromstring(str_xml)
			content = xml.find('Content').text
			msgType = xml.find('MsgType').text
			fromUser = xml.find('FromUserName').text
			toUser = xml.find('ToUserName').text
			mc = pylibmc.Client() #初始化一个memcache实例用来保存用户的操作

			# wxt = wxtoken.getToken()
			# return self.render.reply_text(fromUser,toUser,int(time.time()),wxt)

			if mc.get(fromUser) == 'tqcx':
				if content == 'T' or content == 't':
					mc.delete(fromUser)
					return self.render.reply_text(fromUser,toUser,int(time.time()),u'退出天气查询')
				try:
					tqjg = tqyb.getTianQi(content)
					return self.render.reply_text(fromUser,toUser,int(time.time()),tqjg) 
				except:
					return self.render.reply_text(fromUser,toUser,int(time.time()),u'系统忙请稍后再试'+ '\n退出天气查询回复：t')
			elif mc.get(fromUser) == 'jqr':
				if content == 'T' or content == 't':
					mc.delete(fromUser)
					return self.render.reply_text(fromUser,toUser,int(time.time()),u'你已经退出图灵机器人')
				try:
					m1 = md5.new()
					m1.update(fromUser)
					jqrhf = jqr.getData(content,m1.hexdigest())
					if isinstance(jqrhf,dict):
						if jqrhf['type'] == 'text':
							return self.render.reply_text(fromUser,toUser,int(time.time()),jqrhf['text'])
						elif jqrhf['type'] == 'news':
							return self.render.reply_news(fromUser,toUser,int(time.time()),jqrhf['article'],jqrhf['icon'],jqrhf['detailurl'])
						else:
							return self.render.reply_text(fromUser,toUser,int(time.time()),jqrhf['url'])
					else:
						return self.render.reply_text(fromUser,toUser,int(time.time()),jqrhf)
				except:
					return self.render.reply_text(fromUser,toUser,int(time.time()),u'系统忙请稍后再试'+ '\n退出图灵机器人回复：t')

			if content.find(u'笑话')>-1:
				try:
					xh = getxh()
					return self.render.reply_text(fromUser,toUser,int(time.time()),xh)
				except:
					return self.render.reply_text(fromUser,toUser,int(time.time()),u'系统忙请稍后再试')
			elif content.find(u'天气')>-1:
				mc.set(fromUser,'tqcx')
				return self.render.reply_text(fromUser,toUser,int(time.time()),u'请输入你要查询的城市')
			elif content.find(u'图灵')>-1 or content.find(u'机器人')>-1:
				mc.set(fromUser,'jqr')
				return self.render.reply_text(fromUser,toUser,int(time.time()),u'你现在可以愉快的调戏图灵机器人了,退出图灵机器人回复：t')
			else:
				return self.render.reply_text(fromUser,toUser,int(time.time()),u'我现在还在开发中，只有以下功能回复以下关键字进入功能：\n1.笑话\n2.天气----退出回复：t\n3.图灵机器人----退出回复：t')
		except:
			print('error')
			return 'have error!'










