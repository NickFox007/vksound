# -*- coding: utf-8 -*-
v='5.121'
import settings

import vk_api
from vk_api import audio
from vk_api.audio import VkAudio
from vk_api import audio
from vk_api import VkApi
import collections
import requests,vk_audio
import lxml

                #albums = vkaudio.get(owner_id=31309714)[0]
                #print(albums)
                #for audio in vkaudio.get(owner_id=73031829):
                #    print(audio['artist'] ,audio['title'] , audio['url']  )
                #    #3:20 ОН ОБРАБАТЫВАЕТ 1100 ЗАПИСЕЙ

from flask import Flask,render_template,request, url_for,redirect , session
app = Flask(__name__)
app.secret_key = settings.app_secret_key
mass = []
code_auth = []

# Строка является ли числом

def isNumeric(s):
    try:
        val = int(s)
        return True
    except:
        return False



vk_session = vk_api.VkApi(
            settings.app_username, settings.app_password,
            # функция для обработки двухфакторной аутентификации
             #auth_handler=auth_handler
        )

def vkAuth():

    global vk_session
    vk_session.auth()
    global vk2
    vk2 = vk_session.get_api()



# Спарсить ID пользователя в автоматическом режиме

def parseuserid(name):
    if isNumeric(name):
        #return vk2.method('users.get', { 'user_ids':name})[0]['id']    
        #return vk2.users.get(user_ids=name)[0]['id']
        return name
        
    if name[0]=='@' or name[0]=='*':
        name_new=name
        name_new.pop(0)
        #return vk2.method('users.get', { 'user_ids':name_new})[0]['id']
        return vk2.users.get(user_ids=name_new)[0]['id']
    
    if name.find('vk.com/')>-1:
        offset=name.find('vk.com/')+7
        name_new=name[offset:]
        #obj = vk2.method('utils.resolveScreenName', { 'screen_name':name_new})
        obj = vk2.utils.resolveScreenName(screen_name = name_new, v=v)
        if obj['type']=='user':
            return obj['object_id']
        else:
            return str(int(obj['object_id'])*-1)
			#return vk2.users.get(user_ids=name_new)[0]['id']
    if name[0]=='[' and name[-1]==']' and name.find('|',1,len(name)-1):
        name_new=name.split('|')[0][3:]
        print(name_new)
        #return vk2.method('users.get', { 'user_ids':name_new})[0]['id']
        return vk2.users.get(user_ids=name_new)[0]['id']
    return vk2.users.get(user_ids=name)[0]['id']

def getDuration(i):
	min = int(i) // 60
	sec = int(i) % 60
	
	str_sec = str(sec)
	if len(str_sec)<2:
		str_sec="0"+str_sec
	
	return str(min)+":"+str_sec


@app.route('/auth/' , methods=["GET", "POST"])
def auth_handler():
    if request.method == 'POST':
        kluch = request.form.get('code')
        print(kluch)
        key = input(kluch)
        print(key)
        remember_device = True
    return key, remember_device




@app.route('/')
def hello_world():
    if 'username' in session:
        return redirect("/login/")
    else:
        return render_template("login.html")




@app.route('/about')
def about():
    if 'username' in session:
        return redirect("/login/")
    else:
        return render_template("about.html")


@app.route('/help')
def help():
    return render_template("help.html")

@app.route('/update')
def update():
    if 'username' in session:
        return redirect("/login/")
    else:
        return render_template("update.html")

@app.route('/nahleb')
def nahleb():
    if 'username' in session:
        return redirect("/login/")
    else:
        return render_template("nahleb.html")

# @app.route('/code', methods=["GET", "POST"])
# def codeinput2():
#     if request.method == 'POST':
#         codes = request.form.get('code')
#         print(codes)
#         code_auth.append(codes)
#         key = codes
#         remember_device = False
#
#         return key,remember_device
#
#     return render_template("dvufaktorka.html")

users_id = []
audios_dict = {}

from vk_api.audio import VkAudio
@app.route("/login/", methods=["GET", "POST"])
def login():
    message = ''
    bigmass = []
	
    if request.method == 'POST' :
        session['username'] = parseuserid(str(request.form['code']))
        #print(request.form)
        users_id = []

        # username = request.form.get('username')
        # password = request.form.get('password')
        owner_code = str(request.form.get('code'))  # Если None - аудио будут браться из своей музыки
		
        owner = int(parseuserid(owner_code))

        #print(username,password)
    if request.method == 'GET' :
        owner = int(parseuserid(session['username']))
        
    if True:
        try:

            
            #session['username'] = 'starting'
            bigmass.clear()



        except vk_api.AuthError as error_msg:
            print(error_msg)
            return

            #return redirect(url_for('codeinput2'))


        import vk_audio
        

        #users_id.append(one_comm)
        
        vkAuth()
        vk = vk_audio.VkAudio(vk=vk_session)
        
		
        #one_comm = (vk_session.token['user_id'])

        try:
            
            get_dict = audios_dict.get(owner,None)
            if get_dict == None:
			
                
                data = vk.load(owner)  # получаем наши аудио

                #print(data)
                #second_audio = data.Audios                
                index = 1

                for audios in data.Audios:
                    index += 1
                    if len(str(audios['url'])) >= 3  :
                        #print(audios)

                        #print(audios['url'])
                        audios2 = {}
                        audios2['url']=str(audios['url'])
                        audios2['title']=audios['title']
                        audios2['artist']=audios['artist']
                        audios2['length']=getDuration(audios['duration'])
                        
                        
                        bigmass.append(audios2)
                        if index==settings.app_limit+1:
                            break

                #print(bigmass)
                audios_dict[owner] = bigmass
            else:
                bigmass = get_dict

        except:
            pass
            #session.pop('username', None)
            return render_template("login.html")
        one_comm = owner
        two_comm = str(len(bigmass))
        print(owner)
        return render_template("home.html",one_comm=one_comm,two_comm=two_comm,mass=bigmass)

    else:



        print(owner)
        return render_template("home.html",mass=bigmass)

@app.route('/exit/',methods=['GET', 'POST'])
@app.route('/exit',methods=['GET', 'POST'])
def exiting():

    owner = session.pop('username', None)
    audios_dict.pop(owner, None)
    #print(audios_dict[owner])
    

	
    return render_template("login.html")  



if __name__ == '__main__':
    app.run(host=settings.app_host , port = settings.app_port)
