import os
import traceback
import time
from pyrogram import Client, filters, types, enums
from pyrogram.handlers import MessageHandler

from pyromod import Client

import config


me = os.getenv("ME")
print("mi id :", me,flush=True)
token = os.getenv("SESSION")
# sesion de mi bot
bot = Client("pyro_bot",session_string=token)

config.configurate(bot)

respuestas = {}

preguntas = {
    "autorName" : "Por favor escribe el nombre del autor/diseñador :",
    "hastags" : [f"¿ Usaras <b>Hastags</b> para este aporte ?", "hastagsList"],
    "hastagsList" : "Escribe los hastags que usaras separados por una coma (,)",
    "image" : [f"¿ Tienes una imagen de referencia del modelo ?", "imageDoc"],
    "imageDoc" : ["Por favor enviame la imagen de refencia del modelo.", "verify_img"],
    "document" : ["Ahora porfavor enviame el/los documentos que aportaras.", "verify_doc"],
    "moreDocs" : ["Ok, entonces puedes enviar tu aporte ahora.","verify_doc"],
    "finalice" : "Listo, gracias por tu aporte.",
}
metodo = {
    "autorName" : "ask",
    "hastags" : "send_message",
    "hastagsList" : "ask",
    "image" : "send_message",
    "imageDoc" : "next",
    "document" : "next",
    "moreDocs" : "next",
    "finalice" : "send_message",
}
next_met = {
    "autorName" : "hastags" ,
    "hastagsList" : "image",
    "imageDoc"  : "document",
    "moreDocs" : "finalice",
}
hand = "" # referencia de handler para eliminar despues
listDoc = [] # arreglo donde se guardaran documentos provisionalmente hasta poder procesar, luego se limpia el arreglo
listDoc_to_upload = [] # arreglo donde estaran todos los documentos procesados de un aporte
message_reference = "" # referencia de mensaje para eliminar despues de respuesta
message_reply = "" # referencia de topic o grupo para enviar los mensajes de respuesta
message_chat = "" # referencia de chat donde se hizo el comando
client_reference = "" # referencia del cliente para usar en diferentes funciones
changeNameDoc = "" # referencia para cambiar nombres de documentos aportados
cancel_words = ["cancel", "/cancel", "cancelar", "/cancelar"] # referencias de palabras para cancelar proceso de aporte en partes donde se deba response sino se debe usar el comando /cancel
cancel_commands = ["cancel", "cancelar"] # referencias de comandos para cancelar aporte 

# -------REVISAR----------
#
# -------REVISAR----------

# -------CANCELAR----------
@bot.on_message(filters.command("restart") & filters.user(me))
async def asd(client, m):
    try:
        print("El bot se reiniciara espere...",flush=True)
        # return os.execl(sys.executable, os.path.abspath(__file__), * sys.argv)
        await bot.stop(block=False)
        os._exit(1)
    except Exception as e:
        traceback.print_exc()

@bot.on_message(filters.command("stop") & filters.user(me) & filters.private)
async def asd(client, m):
    try:
        print("El bot se cerrara espere...",flush=True)
        os._exit(3)
    except Exception as e:
        traceback.print_exc()

@bot.on_message(filters.command("id"))
async def asd(client, m):
    try:
        print(m.from_user.id,flush=True)
    except Exception as e:
        traceback.print_exc()

@bot.on_message(filters.command(cancel_commands))
async def asd(client, m):
    try:
        global hand
        chat_id = m.chat.id
        print("se cancelara el aporte", flush=True)
        await bot.delete_messages(chat_id, m.id)
        ne = await bot.get_messages(m.chat.id,m.id-1)
        if ne.reply_markup:
            print("se cancelo mensaje de repuestas para evitar errores", flush=True)
            bot.edit_message_reply_markup(chat_id, ne.id)
        if hand:
            print("se borro handler y se termino proceso de aporte", flush=True)
            await bot.delete_messages(chat_id, message_reference)
            bot.remove_handler(*hand)
            hand = ""
    except Exception as e:
        traceback.print_exc()

# -------CANCELAR----------

# aqui inicia el comando
@bot.on_message(filters.command("aporte"))
async def aportar(client,m):
    try:
        global message_reference
        global message_chat
        global message_reply
        global client_reference

        message_chat = m.chat
        message_reply = m.reply_to_message_id if m.reply_to_message_id else 1

        if not config.isDataOfGroup(str(message_chat.id)[4:]):
            send = "Debes configurar tu lista de hastgas y tu canal de aportes primero, usa el comando /help para mas información."
            res = await bot.send_message(message_chat.id, send, reply_to_message_id=message_reply)
            time.sleep(3)
            await m.delete(), await res.delete()
        else:
            message_reference = m.id
            client_reference = client
            await my_handler()
    except Exception:
        traceback.print_exc()


# funcion que crea botones de si y no
def botonera(name, change=""):
    try:
        if not change:
            bto_pdf = types.InlineKeyboardButton("Si",callback_data=f'si_{name}')
            bto_image = types.InlineKeyboardButton("No",callback_data=f'no_{name}')
            botonera = types.InlineKeyboardMarkup([[bto_pdf,bto_image]])
            return botonera
        else:
            bto_pdf = types.InlineKeyboardButton("Si",callback_data=f'{name}Si_{change}')
            bto_image = types.InlineKeyboardButton("No",callback_data=f'{name}No_{change}')
            botonera = types.InlineKeyboardMarkup([[bto_pdf,bto_image]])
            return botonera
    except Exception:
        traceback.print_exc()


# funcion para escuchar respuesta de si y no 
@bot.on_callback_query()
async def checker(client, call):
    try:
        global message_reference
        message_reference = call.message.id
        # print("entre en nuevo bucle")
        if(call.data.startswith("si")):
            await call.message.edit_text(f"{call.message.text} : Si")
            await my_handler(call.data, "si")

        elif(call.data.startswith("no")):
            await call.message.edit_text(f"{call.message.text} : No")
            await my_handler(call.data, "no")
        elif(call.data.startswith("changeNameSi")):
            listDoc.remove(listDoc[0])
            # -----------
            # print("changeName response si")
            await call.message.edit_text(f"{call.message.text} : Si")
            res = call.data.replace("changeNameSi_", "")
            respuestas[f"{res}_response"] = "si"
            send = "Escribe el nuevo nombre para tu archivo:"
            respu =  await bot.ask(message_chat.id, text=send, reply_to_message_id=message_reply)
            if respu.text in cancel_words:
                # return restart()
                print("Se cancelo el aporte")
                return
            nameDoc = respu.text
            respuestas[res] = nameDoc
            await respu.delete(), await respu.sent_message.delete()
            # print("termine si")
            # -----------
            if listDoc:
                await changeName()
            else:
                await moreDocs()

        elif(call.data.startswith("changeNameNo")):
            listDoc.remove(listDoc[0])
            # -----------
            # print("changeName response no")
            await call.message.edit_text(f"{call.message.text} : No")
            res = call.data.replace("changeNameNo_", "")
            respuestas[f"{res}_response"] = "no"
            # print("termine no")
            # -----------
            if listDoc:
                await changeName()
            else:
                await moreDocs()
    except Exception:
        print("on_callback_query Error")
        await bot.delete_messages(call.message.chat.id,call.message.id)
        traceback.print_exc()


# funcion que guarda las respuestas de botones y ejecuta siguiente paso
async def my_handler(dat="",  response=""):
    try:
        global message_reference
        global hand
        if dat:
            # print("my_handler - dat",dat)
            if "_" in dat:
                dato = dat.split("_")[1]
            else:
                dato = dat

            # print("my_handler - respuesta before",respuestas)

            res = preguntas.get(dato)
            met = metodo.get(dato)
            net = next_met.get(dato)
            
            if response:
                respuestas[f"{dato}_response"] = response
                # print("my_handler -respuestas after",respuestas)

            if response == "no":
                await bot.delete_messages(message_chat.id,message_reference)
                await my_handler(net)
            else:
                await actionBot(dato,met,res,net)
            
        # primera interaccion
        else:
            send = f"¿ Sabes cual es el <b>Autor</b> del modelo/plantilla ?"
            res = await bot.send_message(message_chat.id, send,reply_markup=botonera("autorName"), reply_to_message_id=message_reply)
            await bot.delete_messages(message_chat.id,message_reference)
            message_reference = res.id

    except Exception:
        print("handler Error")
        traceback.print_exc()


# funcion que ejecuta el siguiente paso luego de respuesta de boton
async def actionBot(dato, metodo, action,  next=""):
    try:
        global message_reference
        global hand
        if metodo == "send_message":
            if type(action) == list: # mensajes de preguntas normales
                mes = await bot.send_message(message_chat.id, action[0],reply_markup=botonera(action[1]), reply_to_message_id=message_reply)
                message_reference = mes.id
            else: # mensaje final,aqui se inicia la funcion para enviar el aporte al canal ya establecido anteriormente.
                mes = await bot.send_message(message_chat.id, action, reply_to_message_id=message_reply)
                message_reference = mes.id
                time.sleep(2)
                await bot.delete_messages(message_chat.id, message_reference)
                esperando = await bot.send_message(message_chat.id,f"Ahora enviare tu aporte, espera un momento...", reply_to_message_id=message_reply)
                await isConfig(str(message_chat.id)[4:])
                await bot.delete_messages(message_chat.id,esperando.id)

        if metodo == "ask":
            # res = await bot.send_message(message_chat.id, action, reply_to_message_id=message_reply)
            # has = await res.chat.listen()
            # --------------
            res = await bot.ask(message_chat.id, action, reply_to_message_id=message_reply)
            print(res.text)
            if res.text in cancel_words:
                # return restart()
                print("se cancelo el aporte en ask")
                return
            has = res
            await bot.delete_messages(message_chat.id,message_reference)
            respuestas[dato] = has.text

            await bot.delete_messages(message_chat.id,[res.id,has.id])
            if next:
                await my_handler(next)

        if metodo == "next":
            await bot.delete_messages(message_chat.id,message_reference)
            res = await bot.send_message(message_chat.id, action[0], reply_to_message_id=message_reply)
            message_reference = res.id
            be = bot.add_handler(MessageHandler(func[action[1]][0], func[action[1]][1]))
            hand = be
    except Exception:
        traceback.print_exc()


# verificador de documentos 
async def verify_doc(client,message):
    try:
        global listDoc
        mes_id = message.id
        # if message.document:# aqui se guardara el documento para enviarse al final de flujo
        listDoc.append(message)
        if message_reference:
            await bot.delete_messages(message_chat.id, message_reference)
        ne = await bot.get_messages(message_chat.id,mes_id+1)
        if ne.empty:
            global hand
            bot.remove_handler(*hand)
            hand = ""
            await edit_docs()
    except Exception:
        print("verify_doc Error")
        traceback.print_exc()


# añadiendo handler para esperar la imagen de referencia.
async def verify_img(client,message):
    try:
        global hand
        # print("verify_img message.id: ",message.id)
        if message.photo: # guarda imagen de referencia para enviar despues
            photoId = message.photo.file_id
            # aqui guardamos la imagen
            neo = await bot.download_media(photoId, in_memory=True)
            respuestas["imageDoc"] = neo
            # eliminaresmos la el mensaje con la foto y el mensaje anterior para que este mas limpio
            await bot.delete_messages(message_chat.id, [message_reference, message.id] )
            # se debe remover el escuchador de imagenes
            bot.remove_handler(*hand)
            hand = ""
            # despues de esto seguira el flujo de documento
            await my_handler("document")
    except Exception:
        print("verify_img Error")
        traceback.print_exc()


func = {
    "verify_doc" : [verify_doc, filters.document],
    "verify_img" : [verify_img, filters.photo]
}


# revisara si hay mas mensajes que se enviaron
async def revisar(mes):
    try:
        ne = await bot.get_messages(message_chat.id,mes+1)
        if ne.empty:
            global hand
            bot.remove_handler(*hand)
            # print(f"revisar - Tienes {len(listDoc)} archivos enviados")
            # print(f"revisar - Se iniciara el editor de archivos")
            await bot.delete_messages(message_chat.id, [mes] )
            await edit_docs()
    except Exception:
        print("Revisar Error")
        traceback.print_exc()
        send = "Ocurrio un error por favor informa al equipo o intentalo más tarde."
        res = await bot.send_message(message_chat.id, send, reply_to_message_id=message_reply)
        time.sleep(5)
        await res.delete()


async def edit_docs():
    # print("edit docs init")
    try:
        global listDoc
        for iterDoc in listDoc:

            ext = iterDoc.document.file_name.split(".")[-1]
            photoId = iterDoc.document.file_id
            # -------------------------------------
            # aqui guardaremos los nuevos mensajes descargados
            nameDoc = "".join(iterDoc.document.file_name.split(".")[0:-1])
            # print("edit docs - Name",nameDoc)
            # -------------------------------------
            upload = await bot.send_message(message_chat.id, "Espera mientras descargo tu aporte...")
            neo = await bot.download_media(photoId)

            await upload.delete()
            
            listDoc_to_upload.append([neo, nameDoc, ext, iterDoc.document.file_unique_id])
            await bot.delete_messages(message_chat.id, iterDoc.id)
        # print(f"edit docs - Se recibieron todos los archivos ({len(listDoc)}) aportados")

        await changeName()

        # listDoc = []
    except Exception:
        print("edit docs Error")
        traceback.print_exc()


async def moreDocs():
    try:
        global respuestas
        message = "¿ Quieres enviar mas documentos ?"
        await bot.send_message(message_chat.id, message, reply_markup=botonera("moreDocs"), reply_to_message_id=message_reply)
        await bot.delete_messages(message_chat.id, message_reference)
    except Exception:
        print("moreDocs Error")
        traceback.print_exc()


async def changeName():
    try:
        await bot.delete_messages(message_chat.id, message_reference)
        send = f"¿ Quieres ponerle un nuevo nombre al archivo <b>{listDoc[0].document.file_name}</b> ?"
        await bot.send_message(message_chat.id, send, reply_markup=botonera("changeName",listDoc[0].document.file_unique_id), reply_to_message_id=message_reply)
    except Exception:
        print("changeName Error")
        traceback.print_exc()


# comando para enviar el aporte formateado.
async def isConfig(chat_id):
    try:
        global hand
        if config.isDataOfGroup(chat_id):
            # pasa hcaer la funcion de aporte
            await send_aport()
        else:
            send = "Necesitas configurar tu lista de hastags y tu canal de aportes para poder mandar tu aporte, usa los comandos /start /createHash /setTopic" + "\n"
            send += "Luego usa el comando /send para enviar el aporte que acabas de hacer"
            await bot.send_message(message_chat.id, send)
            hand = bot.add_handler(MessageHandler(send_aport(message_chat.id),filters.command("send")))
            # manda mensaje de que necesitas configurar tu lista de hastags y tu canal de aportes
    except Exception:
        print("isConfig Error")
        traceback.print_exc()


# funcion que envia el aporte formateado
async def send_aport():
    try:
        hastags = [] 
        text_hastags = ""
        mss = ""
        global listDoc_to_upload
        global respuestas

        topic = int(config.topic_to_aport.split("/")[-1])
        # print("sand - topic:",topic)
        etiquetas = config.url["now"]
        await bot.send_chat_action(message_chat.id, enums.ChatAction.TYPING)

        # primero verificaremos si hay un autor
        if respuestas["autorName_response"] == "si":
            hastags.append(respuestas["autorName"].lower().replace(" ", "_"))
            mss  += f'🔸 Autor plantilla: <b>{(respuestas["autorName"]).title()}</b>' + '\n'
        
        
        mss  += '🔸 Formato de plantilla: <b>PDF</b>' + '\n'
        # mss += '🔸 Instrucciones: sí'+ '\n'
        # mss += '✅ Descargar plantilla'+ '\n'

        # verificaremos si hay un hastags por usar
        if respuestas["hastagsList_response"] == "si":
            for has in respuestas["hastagsList"].split(","):
                has = has.lower().strip().replace(" ", "_")
                hastags.append(has)
            # transformamos la lista en una lista de hastags
        for item in hastags:
            text_hastags += f"#{item} "
        mss += '<b>🏷 Etiquetas:</b>'+ '\n'
        mss += text_hastags+ '\n'

        mss += f'<a href="{etiquetas}">—> Todas las etiquetas</a>'+ '\n'

        if respuestas["imageDoc_response"] == "si":
            await bot.send_photo(message_chat.id, respuestas["imageDoc"], caption=mss, reply_to_message_id=topic)
        else:
            await bot.send_message(message_chat.id, text=mss, reply_to_message_id=topic)

        for item in listDoc_to_upload:
            await bot.send_chat_action(message_chat.id, enums.ChatAction.UPLOAD_DOCUMENT)
            if respuestas[f"{item[3]}_response"] == "si":
                item[1] = respuestas[f"{item[3]}"]
            # PREGUNTA PARA CAMBIAR NOMBRE EN OTRO FLUJO---------------
            await bot.send_document(message_chat.id, document=item[0], file_name=f"{item[1]}.{item[2]}", reply_to_message_id=topic)
            os.remove(item[0])

        # luego de mandar los aportes limpiamos la memoria para no reenviar en el siguiente aporte
        # shutil.rmtree(f"./pyrogram/downloads", ignore_errors=True)
        listDoc_to_upload = []
        respuestas = {}
        # print("sand -Termine aporte")
# ------------------------------------
    except Exception:
        print("isConfig send_aport")
        traceback.print_exc()


bot.run(print("me", "ya esya"))
