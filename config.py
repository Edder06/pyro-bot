import os
import json
import time
from pyrogram import Client, filters, types
from pyrogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.handlers import MessageHandler, CallbackQueryHandler

from pyromod import Client

# bot = Client("my_bot")


# ----------CONST--------------------
file_name= "list_hash.json"
telegram_url = "https://t.me/c/"
# ----------CONST--------------------
hand_create = ""
config_informartion = {}
url = {
    "now" : "",
    "before" : "",
}
topic_to_aport = ""
what_method_use = ""
# ---------------------------------------
def isDataOfGroup(cid):
    setVariables(cid)
    if bool(url["now"]) & bool(topic_to_aport):
        return True
    else:
        return False
# ---------------------------------------
def setVariables(id):
    global config_informartion
    
    if os.path.exists(file_name):
        fileExist(id)
    else:
        createVodi(id)

def fileExist(id_group):
# descarga datos si el documento ya existe
    if os.stat(file_name).st_size == 0:
        createVodi(id_group)    
    else:
        downloadNow()
        if not id_group in config_informartion:
            createVodi(id_group)

        updateLocal(id_group)

def downloadNow():#descargo datos para actualizar y revisar
    global config_informartion
    with open(file_name, "r") as file:
        config_informartion = json.load(file)

def updateLocal(id_group):#actualiza valores locales luego de descargarlos
    global url
    global topic_to_aport

    url["now"] = config_informartion[id_group]["url"]
    
    topic_to_aport = config_informartion[id_group]["topic"]

def createVodi(id_group): #creo y subo nueva informacion
    global config_informartion
    with open(file_name, "w") as file:
        config_informartion[id_group] = {}
        config_informartion[id_group]["url"] = ""
        config_informartion[id_group]["topic"] = ""
        json.dump(config_informartion, file)

# ---------------------------------------

# FUNCION QUE CREA BOTONERA DE RESPUESTA SI/NO
def botonera():
    bto_pdf = InlineKeyboardButton("Si",callback_data='si')
    bto_image = InlineKeyboardButton("No",callback_data='no')
    botonera = InlineKeyboardMarkup([[bto_pdf,bto_image]])
    return botonera

def configurate(bot):
    # CONFIGURACION PARA INICIALIZAR TODOS LOS COMANDOS
    @bot.on_message(filters.command("start"))
    async def default_hastags(client, message:Message):
        chat_id = message.chat.id
        str_chat_id = str(chat_id)[4:]

        topic_actual = message.reply_to_message_id if message.reply_to_message_id else 1

        setVariables(str_chat_id)

        res = await bot.send_message(chat_id,"Listo puedes obtener una lista de los comando disponibles aqui /help", reply_to_message_id=topic_actual)
        time.sleep(3)
        await message.delete(), await res.delete()
    # ---------------------------------------

    @bot.on_message(filters.command("getTopic"))
    async def getTopic(client,m):
        chat_id = m.chat.id
        group_chat_str = str(chat_id)[4:]

        topic_actual = m.reply_to_message_id if m.reply_to_message_id else 1
        # --------------
        #actualizar antes de ejecutar
        setVariables(group_chat_str)
        #actualizar antes de ejecutar

        if topic_to_aport:
            hiddden = InlineKeyboardButton("Borrar Mensaje",callback_data="hidden")
            boton = InlineKeyboardMarkup([[hiddden]])
            send = f"Este es tu <a href='{topic_to_aport}'>Canal de aporte</a>"
            res = await bot.send_message(chat_id, send, reply_markup=boton, reply_to_message_id=topic_actual)
            await m.delete()
        else:
            send = f"Te falta asignar tu canal de aportes.\nHaslo con el comando /createTopic"
            res = await bot.send_message(chat_id, send, reply_to_message_id=topic_actual)
            time.sleep(3)
            await bot.delete_messages(chat_id,[m.id,res.id])


    @bot.on_message(filters.command("createTopic"))
    async def createTopicToAport(mes, m):
        chat_id = m.chat.id
        group_chat_str = str(chat_id)[4:]

        global response_to_reply
        global what_method_use
        topic_actual = m.reply_to_message_id if m.reply_to_message_id else 1

        #actualizar antes de ejecutar
        setVariables(group_chat_str)
        #actualizar antes de ejecutar

        if not topic_to_aport:
            # se creara url
            send = f"Encuentra tu canal de aportes y usa el comando /here."
            response_to_reply = await bot.send_message(chat_id, send, reply_to_message_id=topic_actual)

            what_method_use = "createTopic"
            bot.register_next_step_handler(reset_topic,filters.command("here"))
            # Elimina el mensaje de comando que usaste para pasar al siguiente paso
            await m.delete()
        else:
            send = f"Ya tienes un canal de aporte confifgurado <a href='{topic_to_aport}'>Ver Aqui</a>, para este grupo." +  "\n"
            send += f"Si deseas cambairlo, puedes volver a configurarlo con el comando /setTopic"
                
            res = await bot.send_message(chat_id, send, reply_to_message_id=topic_actual)
            time.sleep(3)
            # Elimina el mensaje de comando que usaste para pasar al siguiente paso
            await m.delete(), await res.delete()


    @bot.on_message(filters.command("setTopic"))
    async def setTopicToAport(mes, m):
        chat_id = m.chat.id
        group_chat_str = str(chat_id)[4:]
        
        global response_to_reply
        global what_method_use
        topic_actual = m.reply_to_message_id if m.reply_to_message_id else 1

        #actualizar antes de ejecutar
        setVariables(group_chat_str)
        #actualizar antes de ejecutar

        if topic_to_aport:
            # se creara url
            send = f"Encuentra tu nuevo canal de aportes y usa el comando /here."
            response_to_reply = await bot.send_message(chat_id, send, reply_to_message_id=topic_actual)

            what_method_use = "setTopic"
            bot.register_next_step_handler(reset_topic,filters.command("here"))
            # Elimina el mensaje de comando que usaste para pasar al siguiente paso
            await m.delete()
        else:
            send = f"Aun no has configurado un canal de aporte, puedes hacerlo con el comando /createTopic"

            res = await bot.send_message(chat_id, send, reply_to_message_id=topic_actual)
            time.sleep(3)
            await m.delete(), await res.delete()


    async def reset_topic(client, m):
        chat_id = m.chat.id
        group_chat_str = str(chat_id)[4:]

        global what_method_use
        topic_actual = m.reply_to_message_id if m.reply_to_message_id else 1
        topic_url = telegram_url + group_chat_str + "/" + str(topic_actual)

        with open(file_name, "w+") as file:
            # borrar la url creada
            config_informartion[group_chat_str]["topic"] =  topic_url

            json.dump(config_informartion, file)
        updateLocal(group_chat_str)

        await response_to_reply.delete(), await m.delete()

        mes = "Listo ahora este sera tu canal de aportes."
        if what_method_use == "resetTopic":
            mes = "Listo ahora este es tu nuevo canal de aportes."
        answer = await bot.send_message(m.chat.id, mes, reply_to_message_id=topic_actual)
        time.sleep(5)
        await answer.delete()
        what_method_use = ""

    # ---------------------------------------


    # DEVUELVE EL ENLACE AL MENSAJE CON LA LISTA DE HASHTAGS CONFIGURADA
    @bot.on_message(filters.command("getHash") & filters.group)
    async def obtain_hastags(client, message:Message):
        chat_id = message.chat.id
        id_group_str = str(chat_id)[4:]
        topic_actual = message.reply_to_message_id if message.reply_to_message_id else 1
        # --------------
        #actualizar antes de ejecutar
        setVariables(id_group_str)
        #actualizar antes de ejecutar
        
        if url["now"]:
            hiddden = InlineKeyboardButton("Borrar Mensaje",callback_data="hidden")
            boton = InlineKeyboardMarkup([[hiddden]])
            send = f'Aqui se encuentra tu lista de hashtags. <a href="{url["now"]}">#Hashtags</a>'
            res = await bot.send_message(chat_id, send, reply_markup=boton, reply_to_message_id=topic_actual)
            await message.delete()
        else:#
            send = f"Te falta crear tu lista de hashtags.\nHaslo con el comando /createHash"
            res = await bot.send_message(chat_id, send, reply_to_message_id=topic_actual)
            time.sleep(3)
            await bot.delete_messages(chat_id,[message.id,res.id])
        # --------------

    @bot.on_callback_query(filters.regex("hidden"))
    async def hidden_response(client,call):
        await bot.delete_messages(call.message.chat.id, [call.message.id])

    # CONFIGURACION DE MENSAJE CON HASHTAGS PARA USO DE APORTE
    @bot.on_message(filters.command("createHash") & filters.group)
    async def create_hastags(client, message:Message):
        # comando configurador para pasar el dato 
        # de donde esta la lista de hastags 
        # para poner en la descripcion del aporte formateado
        global response_to_reply
        global what_method_use
        topic_actual = message.reply_to_message_id if message.reply_to_message_id else 1

        chat_id = message.chat.id #id del grupo
        id_group_str = str(chat_id)[4:] #id del grupo string

        #actualizar antes de ejecutar
        setVariables(id_group_str)
        #actualizar antes de ejecutar

        # --------------
        if not url["now"]:
            # se creara url
            send = f"Encuentra y responde al mensaje que contiene tu lista de hastags."
            response_to_reply = await bot.send_message(chat_id, send, reply_to_message_id=topic_actual)

            what_method_use = "createHash"
            bot.register_next_step_handler(old_document_new_information,[filters.reply & filters.text])
            # Elimina el mensaje de comando que usaste para pasar al siguiente paso
            await message.delete()
        else:# ya existe url
            send = f'Ya hay configurada una lista <a href="{url["now"]}">Ver Aqui</a>, para este grupo.' +  "\n"
            send += f"Si no es tu mensaje con tu lista de hashtags, puedes volver a configurarla con el comando /setHash ."
                
            res = await bot.send_message(chat_id, send, reply_to_message_id=topic_actual)
            time.sleep(3)
            # Elimina el mensaje de comando que usaste para pasar al siguiente paso
            await message.delete(), await res.delete()

    # ACTUALIZACION DE MENSAJE CON HASHTAGS PARA USO DE APORTE
    @bot.on_message(filters.command("setHash") & filters.group)
    async def newHash(client,message:Message):
        global response_to_reply
        global what_method_use

        topic_actual = message.reply_to_message_id if message.reply_to_message_id else 1
        
        chat_id = message.chat.id
        id_group_str = str(chat_id)[4:]

        # --------------
        #actualizar antes de ejecutar
        setVariables(id_group_str)
        #actualizar antes de ejecutar

        if url["now"]:
            send =  f"Ahora editaras una lista ya creada, por favor encuentra y responde al mensaje que contiene tu nueva lista de hastags."
            response_to_reply = await bot.send_message(chat_id, send, reply_to_message_id=topic_actual)

            what_method_use = "setHash"
            bot.register_next_step_handler(old_document_reset_information,[filters.reply & filters.text])
            await bot.delete_messages(chat_id, message.id)
            
        else:
            send = f"Aun no has configurado una lista, puedes hacerlo con el comando /createHash ."

            res = await bot.send_message(chat_id, send, reply_to_message_id=topic_actual)
            time.sleep(3)
            await message.delete(), await res.delete()


    async def old_document_new_information(client, message):# Crea informacion de un nuevo hashList en un documento ya creado
        # print("Mensaje: ",message)
        global url
        global config_informartion
        global response_to_reply
        global hand_create
        topic_actual = message.reply_to_message_id if message.reply_to_message_id else 1
        
        chat_id = message.chat.id
        id_group_str = str(chat_id)[4:] #id del grupo
        # -----------------------------------
        if message.reply_to_message:
            url["now"] = telegram_url + id_group_str
            url["now"] += f"/{message.reply_to_top_message_id if message.reply_to_top_message_id else 1 }/{message.reply_to_message_id}"
            # -----------

            with open(file_name, "w+") as file:
                config_informartion[id_group_str]["url"] = url["now"]
                json.dump(config_informartion, file)
            # ----------------------------------
                # -----------
            mes = "Revisa si este enlace te redirige al mensaje correcto"+"\n"
            mes += f'<a href="{url["now"]}">—> Todas las etiquetas</a>'
            await bot.send_message(chat_id, mes, reply_markup=botonera(), reply_to_message_id=topic_actual)
            await bot.delete_messages(chat_id,[response_to_reply.id,message.id])

            response_to_reply = ""
            hand_create = bot.add_handler(CallbackQueryHandler(response_url_create))
        else:
            await no_forward_no_reply(message, "new" )
            
    async def old_document_reset_information(client, message:Message):# Actualiza un documento ya creado con informacion nueva  para un hashList
        # print("Mensaje: ",message)
        global url
        global config_informartion
        global response_to_reply
        global hand_create
        topic_actual = message.reply_to_message_id if message.reply_to_message_id else 1
        
        chat_id = message.chat.id
        id_group_str = str(chat_id)[4:] #id del grupo
        # ----------------
        if message.reply_to_message:
            url["now"] = telegram_url + id_group_str
            url["now"] += f"/{message.reply_to_top_message_id if message.reply_to_top_message_id else 1 }/{message.reply_to_message_id}"
            # -----------

            with open(file_name, "w") as file: #se sobreescrbira la url de este grupo
                url["before"] = config_informartion[id_group_str]["url"]
                config_informartion[id_group_str]["url"] = url["now"]
                json.dump(config_informartion, file)
            # ----------------------------------
                # -----------
            mes = "Revisa si este enlace te redirige al mensaje correcto"+"\n"
            mes += f'O presiona la opcion NO para volver a intentarlo'+"\n"
            mes += f'<a href="{url["now"]}">—> Todas las etiquetas</a>'
            await bot.send_message(chat_id, mes, reply_markup=botonera(), reply_to_message_id=topic_actual)
            await bot.delete_messages(chat_id,[response_to_reply.id,message.id-1,message.id])

            response_to_reply = ""
            hand_create = bot.add_handler(CallbackQueryHandler(response_url_create))
        else:
            await no_forward_no_reply(message, "reset" )
            

    async def no_forward_no_reply(message, call):
        chat_id = message.chat.id
        await bot.delete_messages(chat_id, message.id)
        try:
            send = "Porfavor response a un mensaje antes creado. Para poder crear informacion sobre tu lista"
            if call == "reset":
                send = "Porfavor response a un mensaje antes creado. Para poder actualizar tu lista"
            await response_to_reply.edit(send)
        except:
            print("ya se edito este mensaje")
        
        bot.register_next_step_handler(old_document_reset_information if call == "reset" else old_document_new_information, [filters.reply & filters.text])
        
    # @bot.on_callback_query()
    async def response_url_create(client, call:CallbackQuery):
        global config_informartion
        global url
        global what_method_use
        chat_id = call.message.chat.id
        id_group_str = str(chat_id)[4:]
        try:
            if(call.data == "si"):
                send = "Gracias, se configuro tu mensaje que contiene la lista de hastags, podras acceder a ella desde la descripcion cuando se haga un aporte usando el comando /aporte ."
                await call.message.edit_text(send)

            elif(call.data == "no"):
                send = f"Entiendo, si quieres volver a intentarlo usa /{what_method_use}"
                await call.message.edit_text(send)
                global config_informartion
                with open(file_name, "w+") as file:
                    # borrar la url creada
                    doc = {x:v for x,v in config_informartion[id_group_str].items() if x != "url"}
                    config_informartion[id_group_str] = doc
                    if url["before"]:
                        config_informartion[id_group_str]["url"] = url["before"]
                        url["before"] = ""
                    json.dump(config_informartion, file)
            updateLocal(id_group_str)
            time.sleep(5)
            what_method_use = ""
            await bot.delete_messages(chat_id, call.message.id)
            bot.remove_handler(*hand_create)

        except Exception as e:
            print("Ocurrio algo em respueta", e)
            await bot.delete_messages(chat_id,call.message.id)


# bot.run(print("ya qudo"))
