# coding=utf-8 per definire l'encoding(altrimenti da errore)
#script per arricchire le applicazioni e gli elementi già presenti del datastore
#ricorda di importare questo script come applicative scope perchè va a modificare gli elementi InstalledApplication già presenti del data tree (pensa anche se ha senso eliminare i parsing impropri, come le posizione di JustEat)

import physical #per utilizzare le API di UFED in script esterni in applicative scope
import PAphysical #as PA
import SQLiteParser #libreria per il parsing di database
#from physical import *

cellulare=ds.FileSystems[0] #accedi al primo filesystem presente, se l'acquisizione è un cellulare allora è il filesystem del cellulare vale per una full file system
listapp=[] #lista delle applicazioni installate del cellulare


def Enrich_App(): #funzione che arricchisce le informazioni delle applicazioni evidenziando quali sono state disinstallate, l'hash delle applicazionni e i permessi delle applicazioni

    #localapp_db=SQLiteParser.Database.FromNode(cellulare['/data/data/com.android.vending/databases/localappstate.db']) #fai il parsing del database localappstate.db
    #gass_db=SQLiteParser.Database.FromNode(cellulare['/data/data/com.google.android.gms/databases/gass.db'])
    
    
    
    
    for riga in cellulare['/data/system/packages.list'].Data.read().split('\n'): #leggi i dati in packages.list per riga
        #print(riga) 
        listapp.append(riga.split(' ')[0]) #prendi l'applicazione dalla riga e aggiungila alla lista
    
    for app in list(ds.Models)[0]: #trasforma la collezione di modelli analizzati in lista e accedi alla prima collezione ovvero InstalledApplication 
        print(app)
        if app.Identifier.Value not in listapp: #se l'applicazione non è presenta tra la lista delle app installate
            #print(app)
            app.Description.Value='Applicazione disinstallata'
    
    #LA SOLUZIONE POTREBBE ESSERE DI AGGIUNGERE AL DATATREE UN FILE TXT IN PARSING APP CHE CONTIENE GLI HASH DA GASS.DB IN MODO CHE POI IN ENRICH APP DI PARSARLO IL FILE TXT CHE VIENE AGGIUNTO
    
    #QUA DEVI AGGIUNGERE L'HASH PRENDENDO DA GASS.DB MODIFICANDO IL CAMPO AppGUID DELL'APP
    #gass_db=SQLiteParser.Database.FromNode(cellulare['/data/data/com.google.android.gms/databases/gass.db']) #DA ERRORE PERCHè NON PUOI USARE I PARSER IN APPLICATIVE SCOPE, l'unica idea è importare dei parser come sqlite parser mettendo la cartella in Pylib del physical analizer
    #for pacchetto in gass_db['package_name']:
    #    for hash in gass_db['digest_sha256']:
    #        hashlist[pacchetto.Value]=hash.Value
    
    #print(hashlist)
    
    #for pacchetto in localapp_db['appstate']: #leggi i record della colonna del database localappstate, ovvero i pacchetti installati
            #print(record)
            #print(record['package_name'].Value)
        #if pacchetto['package_name'].Value not in listapp: #se non è presente nella lista delle app installate
            #print(record['package_name'].Value)
            #pass
 
           
                
    
       
    
    
def main():
    print("******NUOVA ESECUZIONE********")
    
    #cerca di accedere a tutte le InstalledApplication per poi modificare le informazioni delle app evidenziando le app disinstallate e aggiungendo l'hash(Gass.db) e i permessi dell'applicazioni(Runtimepermission.xml)
    #e eventualmente il timestamp dell'ultimo aggiornamento(localappstate.db)
 
    
    ###Enrich_App()
    
    
    
    

main()


"""PERMESSI
Accounts-> android.permission.GET_ACCOUNTS e  android.permission.GET_ACCOUNTS_PRIVILEGED-> 

Appinfo-> DA DEFINIRE

Audio-> CAPTURE_AUDIO_OUTPUT, MANAGE_DEVICE_POLICY_AUDIO_OUTPUT, MODIFY_AUDIO_SETTINGS, READ_MEDIA_AUDIO, RECORD_AUDIO
Bluetooth-> BLUETOOTH, 	BLUETOOTH_ADMIN, BLUETOOTH_ADVERTISE, BLUETOOTH_CONNECT, BLUETOOTH_PRIVILEGED, BLUETOOTH_SCAN

Bookmarks-> DA DEFINIRE

Calendar-> READ_CALENDAR, 	WRITE_CALENDAR
Camera-> CAMERA, FOREGROUND_SERVICE_CAMERA, MANAGE_DEVICE_POLICY_CAMERA, MANAGE_DEVICE_POLICY_CAMERA_TOGGLE
Contacts-> READ_CONTACTS, WRITE_CONTACTS

CostMoney-> DA DEFINIRE

DeviceAlarms->SCHEDULE_EXACT_ALARM, SET_ALARM, USE_EXACT_ALARM
Display-> MANAGE_DEVICE_POLICY_DISPLAY, CONFIGURE_WIFI_DISPLAY(FORSE), CHANGE_DISPLAY_COLOR, CONTROL_DISPLAY_BRIGHTNESS, CONFIGURE_DISPLAY_BRIGHTNESS, CONFIGURE_DISPLAY_COLOR_TRANSFORM,
Locations-> ACCESS_BACKGROUND_LOCATION, ACCESS_COARSE_LOCATION, ACCESS_FINE_LOCATION, ACCESS_LOCATION_EXTRA_COMMANDS, ACCESS_MEDIA_LOCATION, CONTROL_LOCATION_UPDATES, FOREGROUND_SERVICE_LOCATION, INSTALL_LOCATION_PROVIDER, LOCATION_HARDWARE, MANAGE_DEVICE_POLICY_LOCATION
Messages-> DELIVER_COMPANION_MESSAGES, MANAGE_DEVICE_POLICY_SUPPORT_MESSAGE, READ_SMS, RECEIVE_MMS, RECEIVE_SMS, RECEIVE_WAP_PUSH(FORSE), SEND_SMS, DISPATCH_NFC_MESSAGE, DISPATCH_PROVISIONING_MESSAGE, SEND_RESPOND_VIA_MESSAGE, .C2D_MESSAGE
Microphone-> FOREGROUND_SERVICE_MICROPHONE, MANAGE_DEVICE_POLICY_MICROPHONE, MANAGE_DEVICE_POLICY_MICROPHONE_TOGGLE
Network-> MANAGE_WIFI_NETWORK_SELECTION, ACCESS_NETWORK_STATE, 	ACCESS_WIFI_STATE, CHANGE_NETWORK_STATE, MANAGE_DEVICE_POLICY_MOBILE_NETWORK, MANAGE_DEVICE_POLICY_NETWORK_LOGGING, MANAGE_DEVICE_POLICY_PROXY, MANAGE_WIFI_NETWORK_SELECTION, READ_PHONE_STATE(FORSE)

PersonalInfo->DA DEFINIRE

PhoneCalls-> ANSWER_PHONE_CALLS, CALL_PHONE, CALL_PRIVILEGED, FOREGROUND_SERVICE_PHONE_CALL

Photos-> DA DEFINIRE
 
Reminders-> reminder.permission.READ, reminder.permission.WRITE (DA FILE)
SocialInfo-> DA DEFINIRE

Storage-> MANAGE_EXTERNAL_STORAGE, MANAGE_MEDIA(forse photos questa), MOUNT_FORMAT_FILESYSTEMS, MOUNT_UNMOUNT_FILESYSTEMS, READ_EXTERNAL_STORAGE, READ_MEDIA_IMAGES(forse photos), READ_MEDIA_VIDEO, READ_MEDIA_VISUAL_USER_SELECTED(forse photos), WRITE_EXTERNAL_STORAGE
UserDictionary-> READ_USER_DICTIONARY, WRITE_USER_DICTIONARY
Voicemail-> ADD_VOICEMAIL, READ_VOICEMAIL, WRITE_VOICEMAIL

CHATGPT è SCASSATO OGGI, PROVA A CHIEDERE A CHAT APPENA SI RIPIGLIA """