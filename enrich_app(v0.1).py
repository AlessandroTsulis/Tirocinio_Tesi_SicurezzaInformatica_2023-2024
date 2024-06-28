# coding=utf-8 per definire l'encoding(altrimenti da errore)
#script per arricchire le applicazioni e gli elementi già presenti del datastore
#ricorda di importare questo script come applicative scope perchè va a modificare gli elementi InstalledApplication già presenti del data tree (pensa anche se ha senso eliminare i parsing impropri, come le posizione di JustEat)

import physical #per utilizzare le API di UFED in script esterni in applicative scope
import PAphysical as PAP
import SQLiteParser #libreria per il parsing di database
#import xml.etree.ElementTree as ET #libreria standard di python per il parsing dei file XML
#import xml.dom.minidom as minidom #eventuale altra libreria per il parsing dei file XML
#from physical import *
#import httplib #libreria per fare le HTTP request

cellulare=ds.FileSystems[0] #accedi al primo filesystem presente, se l'acquisizione è un cellulare allora è il filesystem del cellulare vale per una full file system
listapp=[] #lista delle applicazioni installate del cellulare


def Enrich_App(): #funzione che arricchisce le informazioni delle applicazioni evidenziando quali sono state disinstallate, l'hash delle applicazionni e i permessi delle applicazioni

    #localapp_db=SQLiteParser.Database.FromNode(cellulare['/data/data/com.android.vending/databases/localappstate.db']) #fai il parsing del database localappstate.db
    #gass_db=SQLiteParser.Database.FromNode(cellulare['/data/data/com.google.android.gms/databases/gass.db'])
    
    
    for riga in cellulare['/data/system/packages.list'].Data.read().split('\n'): #leggi i dati in packages.list per riga
        #print(riga) 
        listapp.append(riga.split(' ')[0]) #prendi l'applicazione dalla riga e aggiungila alla lista

        
    hashapp=""
    for modelcollection in list(ds.Models): #scorri tutti i ModelCollection del datastore
        for modello in modelcollection: #scorri tutti i modelli di tutti i ModelCollection
            if (type(modello)== PAP.PA.Data.Models.CarvedString): #se il modello è un CarvedString
    #for stringa in list(ds.Models)[37]: #31: #scorri tutte le CarvedString (la 37esima collezione di modelli è CarvedString se fai carving dopo che hai fatto partire parsing apps altrimenti il numero cambia e senza carving sembra essere 31)
                #if (stringa.Source.Value=="Hash App"): #se il CarvedString è quello degli hash delle app
                if (modello.Source.Value=="Hash App"):
                    hashapp=str(modello.Value.Value)
                
                #print(hashapp) 
                 
                ###stringa.Value.Value=""  #svuota il file Hash App
    
    elencopermessi={}
    runtimepermission=cellulare['data/misc_de/0/apexdata/com.android.permission/runtime-permissions.xml'].Data.read().split('<package name=') #leggi i dti di runtime-permission per pacchetto
    for modelcollection in list(ds.Models): #trasforma la collezione di modelli analizzati in lista e scorri tutti i ModelCollection
    
        for app in modelcollection:
            if (type(app)== PAP.PA.Data.Models.ApplicationModels.InstalledApplication):
                        
            #for app in list(ds.Models)[0]: #trasforma la collezione di modelli analizzati in lista e accedi alla prima collezione ovvero InstalledApplication, guarda se scorrere tutti i modelli e fare con PAP.PA.Data.Models.ApplicationModels.InstalledApplication
                ##print(app)
                if app.Identifier.Value not in listapp: #se l'applicazione non è presenta tra la lista delle app installate
                    #print(app)
                    app.Description.Value='Applicazione disinstallata'
                
                
                ##for riga in range(hashapp.count(':')): #conta il numero di occorrenze di ':' nella stringa (tempo di esecuzione sul ROG circa 2 ore, DA VALUTARE SE MIGLIORABILE METTENDO UN VALORE NON COSì ALTO)
                for riga in range(5): #PER EVITARE CRASH
                    
                    #print(app.Identifier.Value)
                    #print (hashapp.split('\n')[riga].split(': ')[0])
                    apphash=hashapp.split('\n')[riga].split(': ')
                    #print(str(apphash))  
                    if app.Identifier.Value == apphash[0]: #se l'applicazione è presente nel file hash app
                        if 'VirusTotal' in str(apphash): #se nell'hash è anche presente il reputation score di virustotal
                            #print(apphash[2])
                            #print(apphash[3])
                            app.AppGUID.Value= apphash[1]+ apphash[2] #aggiungi all'InstalledApplication il suo hash e il VirusTotal score
                        else:
                            app.AppGUID.Value= apphash[1] #aggiungi all'InstalledApplication il suo hash 
                    
                    #if app.Identifier.Value == hashapp.split('\n')[riga].split(': ')[0]: #se l'applicazione è presente nel file hash app
                        #print("Entrato")
                        #app.AppGUID.Value= hashapp.split('\n')[riga].split(': ')[1] #aggiungi all'InstalledApplication il suo hash 
                
                #elencopermessi={} #SE NON VA LA LISTA DEI PERMESSI PROVA A USARE UN DIZIONARIO
                
                #listapermessi=[]#usa una lista di appoggio per evitare l'errore "collection was modified; enumeration operation may not execute"
                
                for numeropacchetto in range(1,len(runtimepermission)): #scorri tutti i pacchetti
                    #print(str(runtimepermission[numeropacchetto].split('>')[0])) #accedi al nome del pacchetto
                    
                    #print(str(app.Identifier.Value))
                    
                    #listapermessi=[]#usa una lista di appoggio per evitare l'errore "collection was modified; enumeration operation may not execute"
                    
                    if app.Identifier.Value == runtimepermission[numeropacchetto].split('>')[0].replace('"',''): #se l'applicazione è presente in runtime-permission, con .replace rimuove " " nella stringa 
                        #print(len(runtimepermission[numeropacchetto].split("permission name=")))
                        runtimeperm= runtimepermission[numeropacchetto].split('permission name=')
                        
                        listapermessi=[] #usa una lista di appoggio per evitare l'errore "collection was modified; enumeration operation may not execute"
                        for numeropermesso in range(1, len(runtimeperm)): #scorri tutti i permessi del singolo pacchetto 
                            permesso=runtimepermission[numeropacchetto].split('permission name=')[numeropermesso].split('granted=')
                        
                            #print("permesso->"+permesso[0])
                            #print ("granted->"+permesso[1])
                        
                            if 'true' in permesso[1]: #se l'applicazione disponde del permesso
                                
                                
                                
                                if 'GET_ACCOUNTS' in permesso[0] or 'GET_ACCOUNTS_PRIVILEGED' in permesso[0]: #se il permesso corrisponde a determinati valori
                            
                                    #app.Permissions.Add(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Accounts) #aggiungi il permesso Accounts ai permessi dell'applicazione
                                    if not PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Accounts in listapermessi: #se non è gia presente il permesso
                                        listapermessi.append(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Accounts)
                                    
                                    #elencopermessi[app.Identifier.Value]= PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Accounts
                                    
                                elif 'PACKAGE_USAGE_STATS' in permesso[0] or 'READ_PHONE_STATE' in permesso[0]:
                                    
                                    #app.Permissions.Add(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.AppInfo)
                                    
                                    if not PAP.PA.Data.Models.ApplicationModels.PermissionCategory.AppInfo in listapermessi:
                                        listapermessi.append(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.AppInfo)
                                    
                                    
                                elif 'RECORD_AUDIO' in permesso[0] or 'CAPTURE_AUDIO_OUTPUT' in permesso[0] or 'MANAGE_DEVICE_POLICY_AUDIO_OUTPUT' in permesso[0] or 'MODIFY_AUDIO_SETTINGS' in permesso[0] or 'READ_MEDIA_AUDIO' in permesso[0]:
                                    #app.Permissions.Add(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Audio) 
                                    
                                    if not PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Audio in listapermessi:
                                        listapermessi.append(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Audio)
                                    
                                elif 'BLUETOOTH' in permesso[0] or 'BLUETOOTH_ADMIN' in permesso[0] or 'BLUETOOTH_ADVERTISE' in permesso[0] or 'BLUETOOTH_CONNECT' in permesso[0] or 'BLUETOOTH_PRIVILEGED' in permesso[0] or 'BLUETOOTH_SCAN' in permesso[0]:
                                    
                                    #app.Permissions.Add(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Bluetooth)
                                    if not PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Bluetooth in listapermessi:
                                        listapermessi.append(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Bluetooth)
                                    
                                elif 'READ_HISTORY_BOOKMARKS' in permesso[0] or 'WRITE_HISTORY_BOOKMARKS' in permesso[0]:
                                    if not PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Bookmarks in listapermessi:
                                    #app.Permissions.Add(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Bookmarks)
                                        listapermessi.append(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Bookmarks)
                                    
                                elif 'READ_CALENDAR' in permesso[0] or 'WRITE_CALENDAR' in permesso[0]:
                                    #app.Permissions.Add(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Calendars)
                                    if not PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Calendars in listapermessi:
                                        listapermessi.append(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Calendars)
                                    
                                elif 'READ_CONTACTS' in permesso[0] or 'WRITE_CONTACTS' in permesso[0]:
                                    
                                    
                                    #app.Permissions.Add(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Contacts)
                                    if not PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Contacts in listapermessi:
                                        listapermessi.append(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Contacts)
                                    
                                elif 'BILLING' in permesso[0]:
                                 
                                    
                                    #app.Permissions.Add(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.CostMoney)
                                    if not PAP.PA.Data.Models.ApplicationModels.PermissionCategory.CostMoney in listapermessi:
                                        listapermessi.append(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.CostMoney)                        
                                                            
                                elif 'SCHEDULE_EXACT_ALARM' in permesso[0] or 'SET_ALARM' in permesso[0] or 'USE_EXACT_ALARM' in permesso[0]:
                                    
                                    
                                    #app.Permissions.Add(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.DeviceAlarms)
                                    if not PAP.PA.Data.Models.ApplicationModels.PermissionCategory.DeviceAlarms in listapermessi:
                                        listapermessi.append(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.DeviceAlarms)
            
                                elif 'MANAGE_DEVICE_POLICY_DISPLAY' in permesso[0] or 'CHANGE_DISPLAY_COLOR' in permesso[0] or 'CONTROL_DISPLAY_BRIGHTNESS' in permesso[0] or 'CONFIGURE_DISPLAY_BRIGHTNESS' in permesso[0] or 'CONFIGURE_DISPLAY_COLOR_TRANSFORM' in permesso[0]:
                                    
                                    
                                    #app.Permissions.Add(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Display)
                                    if not PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Display in listapermessi:
                                        listapermessi.append(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Display)
                                    
                                    
                                elif 'ACCESS_BACKGROUND_LOCATION' in permesso[0] or 'ACCESS_COARSE_LOCATION' in permesso[0] or 'ACCESS_FINE_LOCATION' in permesso[0] or 'ACCESS_LOCATION_EXTRA_COMMANDS' in permesso[0] or 'ACCESS_MEDIA_LOCATION' in permesso[0] or 'CONTROL_LOCATION_UPDATES' in permesso[0] or 'FOREGROUND_SERVICE_LOCATION' in permesso[0] or 'INSTALL_LOCATION_PROVIDER' in permesso[0] or 'LOCATION_HARDWARE' in permesso[0] or 'MANAGE_DEVICE_POLICY_LOCATION' in permesso[0]:
                             
                                    #app.Permissions.Add(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Locations)
                                    if not PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Locations in listapermessi:
                                        listapermessi.append(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Locations)
                                
                                elif 'DELIVER_COMPANION_MESSAGES' in permesso[0] or 'MANAGE_DEVICE_POLICY_SUPPORT_MESSAGE' in permesso[0] or 'READ_SMS' in permesso[0] or 'RECEIVE_MMS' in permesso[0] or 'RECEIVE_SMS' in permesso[0] or 'SEND_SMS' in permesso[0] or 'DISPATCH_PROVISIONING_MESSAGE' in permesso[0] or 'SEND_RESPOND_VIA_MESSAGE' in permesso[0] or '.C2D_MESSAGE' in permesso[0]:
                             
                                    #app.Permissions.Add(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Messages)
                                    if not PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Messages in listapermessi:
                                        listapermessi.append(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Messages)
                                
                                elif 'FOREGROUND_SERVICE_MICROPHONE' in permesso[0] or 'MANAGE_DEVICE_POLICY_MICROPHONE' in permesso[0] or 'MANAGE_DEVICE_POLICY_MICROPHONE_TOGGLE' in permesso[0]:
                             
                                    #app.Permissions.Add(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Microphone)
                                    if not PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Microphone in listapermessi:
                                        listapermessi.append(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Microphone)
                                    
                                elif 'MANAGE_WIFI_NETWORK_SELECTION' in permesso[0] or 'ACCESS_NETWORK_STATE' in permesso[0] or 'ACCESS_WIFI_STATE' in permesso[0] or 'CHANGE_NETWORK_STATE' in permesso[0] or 'MANAGE_DEVICE_POLICY_MOBILE_NETWORK' in permesso[0] or 'MANAGE_DEVICE_POLICY_NETWORK_LOGGING' in permesso[0] or 'MANAGE_DEVICE_POLICY_PROXY' in permesso[0] or 'MANAGE_WIFI_NETWORK_SELECTION' in permesso[0]:
                             
                                    #app.Permissions.Add(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Network)
                                    if not PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Network in listapermessi:
                                        listapermessi.append(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Network)
                                
                                elif 'GET_ACCOUNTS' in permesso[0] or 'READ_PROFILE' in permesso[0]:
                             
                                    #app.Permissions.Add(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.PersonalInfo)
                                    if not PAP.PA.Data.Models.ApplicationModels.PermissionCategory.PersonalInfo in listapermessi:
                                        listapermessi.append(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.PersonalInfo)
                                    
                                elif 'ANSWER_PHONE_CALLS' in permesso[0] or 'CALL_PHONE' in permesso[0] or 'CALL_PRIVILEGED' in permesso[0] or 'FOREGROUND_SERVICE_PHONE_CALL' in permesso[0] or 'READ_CALL_LOG' in permesso[0] or 'WRITE_CALL_LOG' in permesso[0]:
                                
                                    #app.Permissions.Add(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.PhoneCalls)
                                    if not PAP.PA.Data.Models.ApplicationModels.PermissionCategory.PhoneCalls in listapermessi:
                                        listapermessi.append(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.PhoneCalls)
                                    
                                    
                                elif 'ACCESS_MEDIA_LOCATION' in permesso[0] or 'CAMERA' in permesso[0] or 'READ_MEDIA_IMAGES' in permesso[0] or 'MANAGE_MEDIA' in permesso[0]:
                                
                                    #app.Permissions.Add(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Photos)
                                    if not PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Photos in listapermessi:
                                        listapermessi.append(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Photos)
                                    
                                elif 'reminder.permission.READ' in permesso[0] or 'reminder.permission.WRITE' in permesso[0]:
                                
                                    #app.Permissions.Add(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Reminders)
                                    if not PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Reminders in listapermessi:
                                        listapermessi.append(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Reminders)
                                    
                                elif 'READ_SOCIAL_STREAM' in permesso[0] or 'WRITE_SOCIAL_STREAM' in permesso[0]:
                                    
                                    #app.Permissions.Add(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.SocialInfo)
                                    if not PAP.PA.Data.Models.ApplicationModels.PermissionCategory.SocialInfo in listapermessi:
                                        listapermessi.append(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.SocialInfo)
                                
                                elif 'MANAGE_EXTERNAL_STORAGE' in permesso[0] or 'STORAGE_INTERNAL' in permesso[0] or 'MOUNT_FORMAT_FILESYSTEMS' in permesso[0] or 'MOUNT_UNMOUNT_FILESYSTEMS' in permesso[0] or 'READ_EXTERNAL_STORAGE' in permesso[0] or 'WRITE_EXTERNAL_STORAGE' in permesso[0]:
                                
                                    #app.Permissions.Add(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Storage)
                                    if not PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Storage in listapermessi:
                                        listapermessi.append(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Storage)
                                    
                                elif 'READ_USER_DICTIONARY' in permesso[0] or 'WRITE_USER_DICTIONARY' in permesso[0]:
                                
                                    #app.Permissions.Add(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.UserDictionary)
                                    if not PAP.PA.Data.Models.ApplicationModels.PermissionCategory.UserDictionary in listapermessi:
                                        listapermessi.append(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.UserDictionary)
                                    
                                elif 'ADD_VOICEMAIL' in permesso[0] or 'READ_VOICEMAIL' in permesso[0] or 'WRITE_VOICEMAIL' in permesso[0]:
                                
                                    #app.Permissions.Add(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Voicemail)
                                    if not PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Voicemail in listapermessi:
                                        listapermessi.append(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Voicemail)
                                
                    #print(listapermessi)
                            
                    #for perm in listapermessi:
                        #app.Permissions.Add(perm)
                                
                        #for permesso in listapermessi:
                            #app.Permissions.Add(permesso)
                            
                            
                        elencopermessi[app.Identifier.Value]=listapermessi
                
                ##elencopermessi[app]=listapermessi        
                
                #for perm in elencopermessi[app.Identifier.Value]:   
                    #app.Permissions.Add(perm) #DA SCOMMENTARE SE NON VA LA LISTA
                
            
            #for app, permessi in elencopermessi.items():
                #for perm in permessi:
                    #app.Permissions.Add(perm)
                            
                #for pacchetto,permesso in elencopermessi.items():
                #        if pacchetto==app.Identifier.Value:
                #            for perm in permesso:
                #                app.Permissions.Add(perm)                    
                                
                    #print (runtimepermission[numeropacchetto].split("permission name=")[numeropermesso]) #accedi ad ogni permesso
                    
                    #print (runtimepermission[numeropacchetto].split('permission name=')[numeropermesso].split('granted=')[0]) #accedi al singolo permesso
                    
                    #print(runtimepermission[numeropacchetto].split('permission name=')[numeropermesso].split('granted=')[1]) #accedi al fatto se il permesso è granted oppure no
                    
                    #print(numeropacchetto)
                    #if (numeropacchetto==10): #ANCHE QUESTO VA
                    #    break
                    
                    #if (numeropacchetto==5): #PER EVITARE CRASH
                    #    break
                
            #print(elencopermessi)
   
    for modelcollection in list(ds.Models): #scorri di nuovo le InstalledApplication (per evitare l'errore "Collection was modified; enumeration operation may not execute" se si aggiungevano i permessi durante l'iterazione)    
        for app in modelcollection:
    #for app in list(ds.Models)[0]: 
            if (type(app)== PAP.PA.Data.Models.ApplicationModels.InstalledApplication):
                for pacchetto,permesso in elencopermessi.items():
                    if pacchetto==app.Identifier.Value:
                        for perm in permesso:
                            try:
                                app.Permissions.Add(perm)
                            except Exception:
                                continue #nel caso in cui si solleva un'eccezione passa all'elemento successivo del ciclo
                                
                    #print (packet, permes)
                    
                
                #for app in list(ds.Models)[0]:
            
    
    
    
    
    
    
    
    #albero = ET.fromstring((cellulare['data/misc_de/0/apexdata/com.android.permission/runtime-permissions.xml'].Data.read())) #parsa il file runtime-permission come un albero XML
    #radice = albero.getroot()

    #print(albero.tag)
    
    ##for nodo in albero:
    ##    print(nodo.tag, nodo.attrib)

    #for pacchetto in albero.findall('package'):
        #print(pacchetto.attrib)
        
    #for pacchetto in albero.findall('permission'): #STA ROBA NON VA CHE NON PRENDE I PERMISSION
        #print (pacchetto.attrib)
        #print (pacchetto.find('permission').text)
        #nome = persona.find('nome').text
        
        #print(f"Nome: {nome}, Età: {età}, Città: {città}")
      
    ##hashapp={} #dizionario che contiene i pacchetti e i realtivi hash
    
    ##for stringa in list(ds.Models)[37]: #la 37esima collezione di modelli è CarvedString (pensa se trovi modi più furbi per accedere direttamente ad un singolo modello senza scorrerli tutti, forse con .getbyname)
        ##if (stringa.Source.Value=="Hash App"): #se il CarvedString è quello degli hash delle app
            #print(stringa.Value.Value) #FINO QUI CORRETTO
            
            ##print (range(str(stringa.Value.Value).count('\n')))  #PARTI DA QUI CONTROLLANDO SE IL RANGE è CORRETTO
            
            ##for riga in range(str(stringa.Value.Value).count('\n')): #conta il numero di '\n' ovvero di righe nella stringa
                #valoreriga= str(stringa.Value.Value).split('\n')[riga].split(': ')
                #print(valoreriga) SE USI QUESTO PRINT CRASHA UFED, QUINDI METTICI UN CONTATORE SE LO USI
             
                ####hashapp[str(stringa.Value.Value).split('\n')[riga].split(': ')[0]]= str(stringa.Value.Value).split[riga]('\n').split(': ')[1] #riempi i dizionario con chiave i nomi del pacchetto e valore l'hash del pacchetto
    
    ##print (hashapp)
    
       
    
    
def main():
    print("******NUOVA ESECUZIONE********")
    
    #cerca di accedere a tutte le InstalledApplication per poi modificare le informazioni delle app evidenziando le app disinstallate e aggiungendo l'hash(Gass.db) e i permessi dell'applicazioni(Runtimepermission.xml)
    #e eventualmente il timestamp dell'ultimo aggiornamento(localappstate.db)
 
    
    Enrich_App()
    
    
    
    

main()