# coding=utf-8 per definire l'encoding(altrimenti da errore)
#script per arricchire le applicazioni e gli elementi già presenti del datastore
#ricorda di importare questo script come applicative scope perchè va a modificare gli elementi InstalledApplication già presenti del data tree (pensa anche se ha senso eliminare i parsing impropri, come le posizione di JustEat)

import physical #per utilizzare le API di UFED in script esterni in applicative scope
import PAphysical as PAP
import SQLiteParser #libreria per il parsing di database
#import xml.etree.ElementTree as ET #libreria standard di python per il parsing dei file XML
#import xml.dom.minidom as minidom #eventuale altra libreria per il parsing dei file XML
#from physical import *

cellulare=ds.FileSystems[0] #accedi al primo filesystem presente, se l'acquisizione è un cellulare allora è il filesystem del cellulare vale per una full file system
listapp=[] #lista delle applicazioni installate del cellulare


def Enrich_App(): #funzione che arricchisce le informazioni delle applicazioni evidenziando quali sono state disinstallate, l'hash delle applicazionni e i permessi delle applicazioni

    #localapp_db=SQLiteParser.Database.FromNode(cellulare['/data/data/com.android.vending/databases/localappstate.db']) #fai il parsing del database localappstate.db
    #gass_db=SQLiteParser.Database.FromNode(cellulare['/data/data/com.google.android.gms/databases/gass.db'])
    
    
    for riga in cellulare['/data/system/packages.list'].Data.read().split('\n'): #leggi i dati in packages.list per riga
        #print(riga) 
        listapp.append(riga.split(' ')[0]) #prendi l'applicazione dalla riga e aggiungila alla lista

        
    hashapp="" #SAREBBE MEGLIO SCORRERE TUTTI I MODELLI E QUANDO INCONTRI LA COLLEZIONE CARVED STRING FAI TUTTO IL RESTO, VISTO CHE SEMBRA CAMBI IL NUMERO DELLA COLLEZZIONE NEL MODELLO(USA PA. e tutto il resto per arrivare ad installedapplication, dovrebbe essere PAP.PA.Data.Models.ApplicationModels.InstalledApplication e PAP.PA.Data.Models.CarvedString)
    for stringa in list(ds.Models)[37]: #31: #scorri tutte le CarvedString (la 37esima collezione di modelli è CarvedString se fai carving dopo che hai fatto partire parsing apps altrimenti il numero cambia e senza carving sembra essere 31)
        if (stringa.Source.Value=="Hash App"): #se il CarvedString è quello degli hash delle app
            hashapp=str(stringa.Value.Value)
            
            #print(hashapp) 
             
            ###stringa.Value.Value=""  #svuota il file Hash App
    
    #COSE DA CONTROLLARE SONO:
    #-COME RISOLVERE L'ERRORE "Collection was modified; enumeration operation may not execute" CHE TI SI PRESENTA A VOLTE QUANDO METTI I PERMESSI NELLE APPLICAZIONI (probabilmente ti devi appogiare ad una lista o a un dizionario di liste), ALLA PIù BRUTTA USA TRY EXCEPT QUANDO FAI I .ADD PER CATTURARE L'ERRORE E SCRIVERE ALMENO UN CERTO NUMERO DI PERMESSI
    
    elencopermessi={}
    runtimepermission=cellulare['data/misc_de/0/apexdata/com.android.permission/runtime-permissions.xml'].Data.read().split('<package name=') #leggi i dti di runtime-permission per pacchetto
    for app in list(ds.Models)[0]: #trasforma la collezione di modelli analizzati in lista e accedi alla prima collezione ovvero InstalledApplication 
        ##print(app)
        if app.Identifier.Value not in listapp: #se l'applicazione non è presenta tra la lista delle app installate
            #print(app)
            app.Description.Value='Applicazione disinstallata'
        
        
        ##for riga in range(hashapp.count(':')): #conta il numero di occorrenze di ':' nella stringa (tempo di esecuzione sul ROG circa 2 ore, DA VALUTARE SE MIGLIORABILE METTENDO UN VALORE NON COSì ALTO)
        ##for riga in range(5): #PER EVITARE CRASH
            
            #print(app.Identifier.Value)
            #print (hashapp.split('\n')[riga].split(': ')[0])
            
            ##apphash=hashapp.split('\n')[riga].split(': ')
            ##if app.Identifier.Value == apphash[0]: #se l'applicazione è presente nel file hash app
            ##    app.AppGUID.Value= apphash[1] #aggiungi all'InstalledApplication il suo hash 
            
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
                            
                            listapermessi.append(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Accounts)
                            
                            #elencopermessi[app.Identifier.Value]= PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Accounts
                            
                        if 'PACKAGE_USAGE_STATS' in permesso[0] or 'READ_PHONE_STATE' in permesso[0]:
                            
                            #app.Permissions.Add(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.AppInfo)
                            
                            listapermessi.append(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.AppInfo)
                            
                            
                        if 'RECORD_AUDIO' in permesso[0] or 'CAPTURE_AUDIO_OUTPUT' in permesso[0] or 'MANAGE_DEVICE_POLICY_AUDIO_OUTPUT' in permesso[0] or 'MODIFY_AUDIO_SETTINGS' in permesso[0] or 'READ_MEDIA_AUDIO' in permesso[0]:
                            #app.Permissions.Add(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Audio) 
                            
                            listapermessi.append(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Audio)
                            
                        if 'BLUETOOTH' in permesso[0] or 'BLUETOOTH_ADMIN' in permesso[0] or 'BLUETOOTH_ADVERTISE' in permesso[0] or 'BLUETOOTH_CONNECT' in permesso[0] or 'BLUETOOTH_PRIVILEGED' in permesso[0] or 'BLUETOOTH_SCAN' in permesso[0]:
                            
                            #app.Permissions.Add(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Bluetooth)
                            listapermessi.append(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Bluetooth)
                            
                        if 'READ_HISTORY_BOOKMARKS' in permesso[0] or 'WRITE_HISTORY_BOOKMARKS' in permesso[0]:
                            
                            #app.Permissions.Add(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Bookmarks)
                            listapermessi.append(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Bookmarks)
                            
                        if 'READ_CALENDAR' in permesso[0] or 'WRITE_CALENDAR' in permesso[0]:
                            #app.Permissions.Add(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Calendars)
                            listapermessi.append(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Calendars)
                            
                        if 'READ_CONTACTS' in permesso[0] or 'WRITE_CONTACTS' in permesso[0]:
                            
                            #app.Permissions.Add(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Contacts)
                            listapermessi.append(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Contacts)
                            
                        if 'BILLING' in permesso[0]:
                         
                            
                            #app.Permissions.Add(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.CostMoney)
                            listapermessi.append(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.CostMoney)                        
                                                    
                        if 'SCHEDULE_EXACT_ALARM' in permesso[0] or 'SET_ALARM' in permesso[0] or 'USE_EXACT_ALARM' in permesso[0]:
                            
                            
                            #app.Permissions.Add(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.DeviceAlarms)
                            listapermessi.append(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.DeviceAlarms)
    
                        if 'MANAGE_DEVICE_POLICY_DISPLAY' in permesso[0] or 'CHANGE_DISPLAY_COLOR' in permesso[0] or 'CONTROL_DISPLAY_BRIGHTNESS' in permesso[0] or 'CONFIGURE_DISPLAY_BRIGHTNESS' in permesso[0] or 'CONFIGURE_DISPLAY_COLOR_TRANSFORM' in permesso[0]:
                            
                            
                            #app.Permissions.Add(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Display)
                            listapermessi.append(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Display)
                            
                            
                        if 'ACCESS_BACKGROUND_LOCATION' in permesso[0] or 'ACCESS_COARSE_LOCATION' in permesso[0] or 'ACCESS_FINE_LOCATION' in permesso[0] or 'ACCESS_LOCATION_EXTRA_COMMANDS' in permesso[0] or 'ACCESS_MEDIA_LOCATION' in permesso[0] or 'CONTROL_LOCATION_UPDATES' in permesso[0] or 'FOREGROUND_SERVICE_LOCATION' in permesso[0] or 'INSTALL_LOCATION_PROVIDER' in permesso[0] or 'LOCATION_HARDWARE' in permesso[0] or 'MANAGE_DEVICE_POLICY_LOCATION' in permesso[0]:
                     
                            #app.Permissions.Add(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Locations)
                            listapermessi.append(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Locations)
                        
                        if 'DELIVER_COMPANION_MESSAGES' in permesso[0] or 'MANAGE_DEVICE_POLICY_SUPPORT_MESSAGE' in permesso[0] or 'READ_SMS' in permesso[0] or 'RECEIVE_MMS' in permesso[0] or 'RECEIVE_SMS' in permesso[0] or 'SEND_SMS' in permesso[0] or 'DISPATCH_PROVISIONING_MESSAGE' in permesso[0] or 'SEND_RESPOND_VIA_MESSAGE' in permesso[0] or '.C2D_MESSAGE' in permesso[0]:
                     
                            #app.Permissions.Add(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Messages)
                            listapermessi.append(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Messages)
                        
                        if 'FOREGROUND_SERVICE_MICROPHONE' in permesso[0] or 'MANAGE_DEVICE_POLICY_MICROPHONE' in permesso[0] or 'MANAGE_DEVICE_POLICY_MICROPHONE_TOGGLE' in permesso[0]:
                     
                            #app.Permissions.Add(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Microphone)
                            listapermessi.append(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Microphone)
                            
                        if 'MANAGE_WIFI_NETWORK_SELECTION' in permesso[0] or 'ACCESS_NETWORK_STATE' in permesso[0] or 'ACCESS_WIFI_STATE' in permesso[0] or 'CHANGE_NETWORK_STATE' in permesso[0] or 'MANAGE_DEVICE_POLICY_MOBILE_NETWORK' in permesso[0] or 'MANAGE_DEVICE_POLICY_NETWORK_LOGGING' in permesso[0] or 'MANAGE_DEVICE_POLICY_PROXY' in permesso[0] or 'MANAGE_WIFI_NETWORK_SELECTION' in permesso[0]:
                     
                            #app.Permissions.Add(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Network)
                            listapermessi.append(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Network)
                        
                        if 'GET_ACCOUNTS' in permesso[0] or 'READ_PROFILE' in permesso[0]:
                     
                            #app.Permissions.Add(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.PersonalInfo)
                            listapermessi.append(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.PersonalInfo)
                            
                        if 'ANSWER_PHONE_CALLS' in permesso[0] or 'CALL_PHONE' in permesso[0] or 'CALL_PRIVILEGED' in permesso[0] or 'FOREGROUND_SERVICE_PHONE_CALL' in permesso[0] or 'READ_CALL_LOG' in permesso[0] or 'WRITE_CALL_LOG' in permesso[0]:
                        
                            #app.Permissions.Add(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.PhoneCalls)
                            listapermessi.append(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.PhoneCalls)
                            
                            
                        if 'ACCESS_MEDIA_LOCATION' in permesso[0] or 'CAMERA' in permesso[0] or 'READ_MEDIA_IMAGES' in permesso[0] or 'MANAGE_MEDIA' in permesso[0]:
                        
                            #app.Permissions.Add(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Photos)
                            listapermessi.append(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Photos)
                            
                        if 'reminder.permission.READ' in permesso[0] or 'reminder.permission.WRITE' in permesso[0]:
                        
                            #app.Permissions.Add(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Reminders)
                            listapermessi.append(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Reminders)
                            
                        if 'READ_SOCIAL_STREAM' in permesso[0] or 'WRITE_SOCIAL_STREAM' in permesso[0]:
                        
                            #app.Permissions.Add(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.SocialInfo)
                            listapermessi.append(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.SocialInfo)
                        
                        if 'MANAGE_EXTERNAL_STORAGE' in permesso[0] or 'STORAGE_INTERNAL' in permesso[0] or 'MOUNT_FORMAT_FILESYSTEMS' in permesso[0] or 'MOUNT_UNMOUNT_FILESYSTEMS' in permesso[0] or 'READ_EXTERNAL_STORAGE' in permesso[0] or 'WRITE_EXTERNAL_STORAGE' in permesso[0]:
                        
                            #app.Permissions.Add(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Storage)
                            listapermessi.append(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Storage)
                            
                        if 'READ_USER_DICTIONARY' in permesso[0] or 'WRITE_USER_DICTIONARY' in permesso[0]:
                        
                            #app.Permissions.Add(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.UserDictionary)
                            listapermessi.append(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.UserDictionary)
                            
                        if 'ADD_VOICEMAIL' in permesso[0] or 'READ_VOICEMAIL' in permesso[0] or 'WRITE_VOICEMAIL' in permesso[0]:
                        
                            #app.Permissions.Add(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Voicemail)
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
    #PROVA EVENTUALMENTE AD ESEGUIRLO DA 0 UNA PRIMA VOLTA, MAGARI FUNZIONA
    for app in list(ds.Models)[0]: #scorri di nuovo le InstalledApplication (per evitare l'errore "Collection was modified; enumeration operation may not execute" se si aggiungevano i permessi durante l'iterazione)
        for pacchetto,permesso in elencopermessi.items():
            if pacchetto==app.Identifier.Value:
                for perm in permesso:
                    app.Permissions.Add(perm)
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