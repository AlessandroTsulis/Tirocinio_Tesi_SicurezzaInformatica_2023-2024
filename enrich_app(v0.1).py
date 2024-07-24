# coding=utf-8 per definire l'encoding(altrimenti da errore)
#script per arricchire le applicazioni e gli elementi già presenti del datastore
#ricorda di importare questo script come applicative scope perchè va a modificare gli elementi InstalledApplication già presenti del data tree

import physical #per utilizzare le API di UFED in script esterni in applicative scope
import PAphysical as PAP
import SQLiteParser #libreria per il parsing di database

cellulare=ds.FileSystems[0] #accedi al primo filesystem presente, se l'acquisizione è un cellulare allora è il filesystem del cellulare vale per una full file system
listapp=[] #lista delle applicazioni installate del cellulare


def Enrich_App(): #funzione che arricchisce le informazioni delle applicazioni evidenziando quali sono state disinstallate, l'hash delle applicazionni e i permessi delle applicazioni
    
    for riga in cellulare['/data/system/packages.list'].Data.read().split('\n'): #leggi i dati in packages.list per riga
        listapp.append(riga.split(' ')[0]) #prendi l'applicazione dalla riga e aggiungila alla lista

        
    hashapp=""
    for modelcollection in list(ds.Models): #scorri tutti i ModelCollection del datastore
        for modello in modelcollection: #scorri tutti i modelli di tutti i ModelCollection
            if (type(modello)== PAP.PA.Data.Models.CarvedString): #se il modello è un CarvedString
                if (modello.Source.Value=="Hash App"): #se il CarvedString è quello degli hash delle app
                    hashapp=str(modello.Value.Value)
                
                 
                    ###stringa.Value.Value=""  #svuota il file Hash App
    
    elencopermessi={}
    runtimepermission=cellulare['data/misc_de/0/apexdata/com.android.permission/runtime-permissions.xml'].Data.read().split('<package name=') #leggi i dti di runtime-permission per pacchetto
    for modelcollection in list(ds.Models): #trasforma la collezione di modelli analizzati in lista e scorri tutti i ModelCollection
    
        for app in modelcollection:
            if (type(app)== PAP.PA.Data.Models.ApplicationModels.InstalledApplication):
                     
                if app.Identifier.Value not in listapp: #se l'applicazione non è presenta tra la lista delle app installate
                    
                    app.Description.Value='Applicazione disinstallata'
                
                
                #for riga in range(hashapp.count(':')): #conta il numero di occorrenze di ':' nella stringa (tempo di esecuzione sul ROG circa 2 ore prendendo circa 470 HASH)
                for riga in range(5): #PER EVITARE TEMPI MOLTO LUNGHI
                    apphash=hashapp.split('\n')[riga].split(': ')  
                    if app.Identifier.Value == apphash[0]: #se l'applicazione è presente nel file hash app
                        app.AppGUID.Value= apphash[1] #aggiungi all'InstalledApplication il suo hash 
                    
                
                for numeropacchetto in range(1,len(runtimepermission)): #scorri tutti i pacchetti
                    
                    if app.Identifier.Value == runtimepermission[numeropacchetto].split('>')[0].replace('"',''): #se l'applicazione è presente in runtime-permission, con .replace rimuove " " nella stringa 
                        runtimeperm= runtimepermission[numeropacchetto].split('permission name=')
                        
                        listapermessi=[] #usa una lista di appoggio per evitare l'errore "collection was modified; enumeration operation may not execute"
                        for numeropermesso in range(1, len(runtimeperm)): #scorri tutti i permessi del singolo pacchetto 
                            permesso=runtimepermission[numeropacchetto].split('permission name=')[numeropermesso].split('granted=')
                        
                            if 'true' in permesso[1]: #se l'applicazione disponde del permesso
                                
                                
                                
                                if 'GET_ACCOUNTS' in permesso[0] or 'GET_ACCOUNTS_PRIVILEGED' in permesso[0]: #se il permesso corrisponde a determinati valori
                            
                                    if not PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Accounts in listapermessi: #se non è gia presente il permesso
                                        listapermessi.append(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Accounts) #aggiungi il permesso Accounts ai permessi dell'applicazione
                                    
                                elif 'PACKAGE_USAGE_STATS' in permesso[0] or 'READ_PHONE_STATE' in permesso[0]:
                                  
                                    if not PAP.PA.Data.Models.ApplicationModels.PermissionCategory.AppInfo in listapermessi:
                                        listapermessi.append(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.AppInfo)
                                    
                                    
                                elif 'RECORD_AUDIO' in permesso[0] or 'CAPTURE_AUDIO_OUTPUT' in permesso[0] or 'MANAGE_DEVICE_POLICY_AUDIO_OUTPUT' in permesso[0] or 'MODIFY_AUDIO_SETTINGS' in permesso[0] or 'READ_MEDIA_AUDIO' in permesso[0]: 
                                    
                                    if not PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Audio in listapermessi:
                                        listapermessi.append(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Audio)
                                    
                                elif 'BLUETOOTH' in permesso[0] or 'BLUETOOTH_ADMIN' in permesso[0] or 'BLUETOOTH_ADVERTISE' in permesso[0] or 'BLUETOOTH_CONNECT' in permesso[0] or 'BLUETOOTH_PRIVILEGED' in permesso[0] or 'BLUETOOTH_SCAN' in permesso[0]:
                                    
                                    if not PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Bluetooth in listapermessi:
                                        listapermessi.append(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Bluetooth)
                                    
                                elif 'READ_HISTORY_BOOKMARKS' in permesso[0] or 'WRITE_HISTORY_BOOKMARKS' in permesso[0]:
                                    
                                    if not PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Bookmarks in listapermessi:
                                        listapermessi.append(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Bookmarks)
                                    
                                elif 'READ_CALENDAR' in permesso[0] or 'WRITE_CALENDAR' in permesso[0]:
                                    
                                    if not PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Calendars in listapermessi:
                                        listapermessi.append(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Calendars)
                                    
                                elif 'READ_CONTACTS' in permesso[0] or 'WRITE_CONTACTS' in permesso[0]:
                                    
                                    
                                    if not PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Contacts in listapermessi:
                                        listapermessi.append(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Contacts)
                                    
                                elif 'BILLING' in permesso[0]:
                                 
                                    if not PAP.PA.Data.Models.ApplicationModels.PermissionCategory.CostMoney in listapermessi:
                                        listapermessi.append(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.CostMoney)                        
                                                            
                                elif 'SCHEDULE_EXACT_ALARM' in permesso[0] or 'SET_ALARM' in permesso[0] or 'USE_EXACT_ALARM' in permesso[0]:
                                   
                                    if not PAP.PA.Data.Models.ApplicationModels.PermissionCategory.DeviceAlarms in listapermessi:
                                        listapermessi.append(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.DeviceAlarms)
            
                                elif 'MANAGE_DEVICE_POLICY_DISPLAY' in permesso[0] or 'CHANGE_DISPLAY_COLOR' in permesso[0] or 'CONTROL_DISPLAY_BRIGHTNESS' in permesso[0] or 'CONFIGURE_DISPLAY_BRIGHTNESS' in permesso[0] or 'CONFIGURE_DISPLAY_COLOR_TRANSFORM' in permesso[0]:
                                    
                                    if not PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Display in listapermessi:
                                        listapermessi.append(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Display)
                                    
                                    
                                elif 'ACCESS_BACKGROUND_LOCATION' in permesso[0] or 'ACCESS_COARSE_LOCATION' in permesso[0] or 'ACCESS_FINE_LOCATION' in permesso[0] or 'ACCESS_LOCATION_EXTRA_COMMANDS' in permesso[0] or 'ACCESS_MEDIA_LOCATION' in permesso[0] or 'CONTROL_LOCATION_UPDATES' in permesso[0] or 'FOREGROUND_SERVICE_LOCATION' in permesso[0] or 'INSTALL_LOCATION_PROVIDER' in permesso[0] or 'LOCATION_HARDWARE' in permesso[0] or 'MANAGE_DEVICE_POLICY_LOCATION' in permesso[0]:
                             
                                    if not PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Locations in listapermessi:
                                        listapermessi.append(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Locations)
                                
                                elif 'DELIVER_COMPANION_MESSAGES' in permesso[0] or 'MANAGE_DEVICE_POLICY_SUPPORT_MESSAGE' in permesso[0] or 'READ_SMS' in permesso[0] or 'RECEIVE_MMS' in permesso[0] or 'RECEIVE_SMS' in permesso[0] or 'SEND_SMS' in permesso[0] or 'DISPATCH_PROVISIONING_MESSAGE' in permesso[0] or 'SEND_RESPOND_VIA_MESSAGE' in permesso[0] or '.C2D_MESSAGE' in permesso[0]:
                             
                                    if not PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Messages in listapermessi:
                                        listapermessi.append(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Messages)
                                
                                elif 'FOREGROUND_SERVICE_MICROPHONE' in permesso[0] or 'MANAGE_DEVICE_POLICY_MICROPHONE' in permesso[0] or 'MANAGE_DEVICE_POLICY_MICROPHONE_TOGGLE' in permesso[0]:
                             
                                    if not PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Microphone in listapermessi:
                                        listapermessi.append(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Microphone)
                                    
                                elif 'MANAGE_WIFI_NETWORK_SELECTION' in permesso[0] or 'ACCESS_NETWORK_STATE' in permesso[0] or 'ACCESS_WIFI_STATE' in permesso[0] or 'CHANGE_NETWORK_STATE' in permesso[0] or 'MANAGE_DEVICE_POLICY_MOBILE_NETWORK' in permesso[0] or 'MANAGE_DEVICE_POLICY_NETWORK_LOGGING' in permesso[0] or 'MANAGE_DEVICE_POLICY_PROXY' in permesso[0] or 'MANAGE_WIFI_NETWORK_SELECTION' in permesso[0]:
                             
                                    if not PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Network in listapermessi:
                                        listapermessi.append(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Network)
                                
                                elif 'GET_ACCOUNTS' in permesso[0] or 'READ_PROFILE' in permesso[0]:
                             
                                    if not PAP.PA.Data.Models.ApplicationModels.PermissionCategory.PersonalInfo in listapermessi:
                                        listapermessi.append(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.PersonalInfo)
                                    
                                elif 'ANSWER_PHONE_CALLS' in permesso[0] or 'CALL_PHONE' in permesso[0] or 'CALL_PRIVILEGED' in permesso[0] or 'FOREGROUND_SERVICE_PHONE_CALL' in permesso[0] or 'READ_CALL_LOG' in permesso[0] or 'WRITE_CALL_LOG' in permesso[0]:
                                
                                    if not PAP.PA.Data.Models.ApplicationModels.PermissionCategory.PhoneCalls in listapermessi:
                                        listapermessi.append(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.PhoneCalls)
                                    
                                    
                                elif 'ACCESS_MEDIA_LOCATION' in permesso[0] or 'CAMERA' in permesso[0] or 'READ_MEDIA_IMAGES' in permesso[0] or 'MANAGE_MEDIA' in permesso[0]:
                                
                                    if not PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Photos in listapermessi:
                                        listapermessi.append(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Photos)
                                    
                                elif 'reminder.permission.READ' in permesso[0] or 'reminder.permission.WRITE' in permesso[0]:
                                
                                    if not PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Reminders in listapermessi:
                                        listapermessi.append(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Reminders)
                                    
                                elif 'READ_SOCIAL_STREAM' in permesso[0] or 'WRITE_SOCIAL_STREAM' in permesso[0]:
                                    
                                    if not PAP.PA.Data.Models.ApplicationModels.PermissionCategory.SocialInfo in listapermessi:
                                        listapermessi.append(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.SocialInfo)
                                
                                elif 'MANAGE_EXTERNAL_STORAGE' in permesso[0] or 'STORAGE_INTERNAL' in permesso[0] or 'MOUNT_FORMAT_FILESYSTEMS' in permesso[0] or 'MOUNT_UNMOUNT_FILESYSTEMS' in permesso[0] or 'READ_EXTERNAL_STORAGE' in permesso[0] or 'WRITE_EXTERNAL_STORAGE' in permesso[0]:
                                
                                    if not PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Storage in listapermessi:
                                        listapermessi.append(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Storage)
                                    
                                elif 'READ_USER_DICTIONARY' in permesso[0] or 'WRITE_USER_DICTIONARY' in permesso[0]:
                                
                                    if not PAP.PA.Data.Models.ApplicationModels.PermissionCategory.UserDictionary in listapermessi:
                                        listapermessi.append(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.UserDictionary)
                                    
                                elif 'ADD_VOICEMAIL' in permesso[0] or 'READ_VOICEMAIL' in permesso[0] or 'WRITE_VOICEMAIL' in permesso[0]:
                                
                                    if not PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Voicemail in listapermessi:
                                        listapermessi.append(PAP.PA.Data.Models.ApplicationModels.PermissionCategory.Voicemail)
                            
                        elencopermessi[app.Identifier.Value]=listapermessi
                
                
   
    for modelcollection in list(ds.Models): #scorri di nuovo le InstalledApplication (per evitare l'errore "Collection was modified; enumeration operation may not execute" se si aggiungevano i permessi durante l'iterazione)    
        for app in modelcollection:
            if (type(app)== PAP.PA.Data.Models.ApplicationModels.InstalledApplication):
                for pacchetto,permesso in elencopermessi.items():
                    if pacchetto==app.Identifier.Value:
                        for perm in permesso:
                            try:
                                app.Permissions.Add(perm)
                            except Exception:
                                continue #nel caso in cui si solleva un'eccezione passa all'elemento successivo del ciclo
                                
                    
    
def main():
    print("******NUOVA ESECUZIONE********")
     
    Enrich_App()
    
    
    
main()