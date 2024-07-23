# coding=utf-8 per definire l'encoding (altrimenti da errore)
#script per fare il parsing dei database di applicazioni non considerate da UFED e aggiungere nuovi elementi al datastore
#importa questo script come decoding scope, ricorda che se vuoi aggiungere degli elementi al data tree d utilizzare il decoding scope (l'applicative scope serve modificare elementi già presenti) 
from physical import * #per utilizzare le API UFED in script esterni (librerie per il decoding scope)
import sys
#import shutil  #per copiare i file usa shutil
import SQLiteParser #libreria per il parsing di database
import datetime #modello per trasformare da timestamp a datetime
from System.Convert import IsDBNull #per controllare se un record di un database è Null
import time
import httplib #libreria per fare le HTTP request


#PENSA SE USARE GLOBAL NEL MAIN INVECE CHE METTERE LE VARIABILI QUI
cellulare=ds.FileSystems[0] #accedi al primo filesystem presente, se l'acquisizione è un cellulare allora è il filesystem del cellulare vale per una full file system
listapp=[] #lista delle applicazioni installate del cellulare


def Check_Installed_App(): #funzione che calcola l'elenco delle applicazioni installate    
    for riga in cellulare['/data/system/packages.list'].Data.read().split('\n'): #leggi i dati in packages.list per riga
        #print(riga) 
        listapp.append(riga.split(' ')[0]) #prendi l'applicazione dalla riga e aggiungila alla lista delle app installate


def Check_Hash(): #funzione che prende l'hash delle applicazioni e lo aggiunge ad un file 
    ##hashlist={} #dizionario che contiene le applicazioni e i loro hash
    gass_db=SQLiteParser.Database.FromNode(cellulare['/data/data/com.google.android.gms/databases/gass.db'])
    
    ##for pacchetto in gass_db['app_info']:
    ##    hashlist[pacchetto['package_name'].Value]=pacchetto['digest_sha256'].Value #riempi il dizionario con chiave nome del pacchetto e valore l'hash (prende sempre il primo elemento del database con quel nome di pacchetto e quindi prende la versione più recente ovvero quella installata sul dispositivo)
    
    #print(hashlist)
    
    hash_app=CarvedString()
    
    hash_app.Deleted=DeletedState.Intact
    hash_app.Source.Value="Hash App"

    hash_app.Value.Value=""
    number_request=0 #numero della richiesta HTTP a Virus Total
    for pacchetto in gass_db['app_info']: 
        hash_app.Value.Value=hash_app.Value.Value+str(pacchetto['package_name'].Value)+': '+str(pacchetto['digest_sha256'].Value) #riempi il CarvedString con il nome dei package e il loro hash
        
        if (number_request<4): #senza l'abbonamento a VirusTotal hai 4 HTTP request con l'API al minuto (teoricamente, in pratica pare che il limite sia 11, ma dopo la 5 da errori meglio non rischiare) 
            reputation=Check_VirusTotal_Reputation(str(pacchetto['digest_sha256'].Value), "0ce5dc209e7723d66c658bcae2da3f77bed7b95ffd56171ffb38cc1e91b97436") #controlla con Virustotal il livello di reputazione dell'app tramite hash, l'api key è pubblica e non è premium
            number_request=number_request+1
            
            hash_app.Value.Value=hash_app.Value.Value+" VirusTotal Reputation Score:  "+reputation+"\n" #Aggiungi il repution score di virustotal dopo l'hash dell'app
        else:
            hash_app.Value.Value=hash_app.Value.Value+"\n" #aggiungi un "\n" per una visualizzazione migliore
    ##for pacchetto in hashlist.keys(): #scorri tutte le chiavi del dizionario
        ##hash_app.Value=hash_app.Value+str(pacchetto)+': '+str(hashlist[pacchetto])+'\n'
        
    ds.Models.Add(hash_app)

def Check_VirusTotal_Reputation(hash, apikey): #funzione che utilizza virustotal tramite api per sapere il livello di reputazione dell'app tramite hash 
    conn = httplib.HTTPSConnection("www.virustotal.com") #fai una richiesta HTTP a VirusTotal
    conn.request("GET", "/api/v3/files/"+hash, headers={ 
        "accept": "application/json",
        "x-apikey": apikey #api key del profilo su virustotal
    })

    response = conn.getresponse()
    if (response.status == 200): #se la richiesta è andata a buon fine
        #print(response.read())  
        #print(response.read().split('"reputation": ')[1].split(',')[0])
        return response.read().split('"reputation": ')[1].split(',')[0]

        


def Paypal_Parsing(): #funzione che fa il parsing dei database di paypal(utile solo il parsing del file last_exit_info)
    WebView_LastExit('/data/data/com.paypal.android.p2pmobile/app_webview/last-exit-info',"Paypal")
    ##last_exit=CarvedString() 
    
    ##last_exit.Deleted=DeletedState.Intact
    ##last_exit.Source.Value="Paypal"
    
    ##ts=cellulare['/data/data/com.paypal.android.p2pmobile/app_webview/last-exit-info'].Data.read().split(',')[1].split(':') #prendi il timestamp contenuto nel file last-exit-info splittando prima per , e poi splittando il secondo elemento per :
    ##last_exit.Value.Value="Ultima uscita dall'applicazione: "+ str(TimeStamp.FromUnixTime(int64_to_unixtimestamp(int(ts[1]))))
    
    ##ds.Models.Add(last_exit)
    
def Ryanair_Parsing():
    frlocal_db=SQLiteParser.Database.FromNode(cellulare['/data/data/com.ryanair.cheapflights/databases/fr-local-db'])
    
    for stazione in frlocal_db['recent_stations']:  #Per aggiungere le ricerce effettuate
        ricerca=SearchedItem() #crea il modello elemento cercato
        ricerca.Source.Value="Ryanair"
        ricerca.Deleted=DeletedState.Intact
        ricerca.TimeStamp.Value=TimeStamp.FromUnixTime(int64_to_unixtimestamp(stazione['last_usage'].Value, 'ms')) #assegna i timestamp delle ricerche, il timestamp è in millisecondi
        
        ricerca.Value.Value="From station: "+stazione['origin_station_code'].Value+" to station: "+stazione['station_code'].Value
        #ricerca.Account="prova" #DA CAPIRE SE E COME SI PUò ACCEDERE AD ALCUNI ELEMENTI DEI DATABASE
        #ricerca.Parameters="prova"
        
        ds.Models.Add(ricerca)
   
    
    for profilo in frlocal_db['user_profile']: #per aggiungere account utente ryanair
        account=UserAccount() #crea un modello account
        account.Name.Value=profilo['first_name'].Value+profilo['last_name'].Value #assegna al nome dell'account nome e cognome
        account.Username.Value=profilo['email'].Value
        account.ServiceType.Value= "com.ryanair.cheapflights"
        account.Source.Value="Ryanair"
        #account.Source=profilo['first_name'].Source #EVENTUALMENTE DA CAPIRE MEGLIO COME UTILIZZARE SOURCE PER IMPOSTARE ANCHE SOURCE INFORMATION
        
        
        account.Deleted=DeletedState.Intact #imposta il fatto che l'elemento non è stato cancellato
           
        account.TimeCreated.Value=TimeStamp.FromUnixTime(int64_to_unixtimestamp(profilo['member_since'].Value, 'ms')) #trasfroma da int64 a timestamp unix con il timestamp in millisecondi e poi da unix timestamp a timestamp di UFED e lo assegna alla data di crezione dell'account
        
        if IsDBNull (profilo['phone_number'].Value) == False: #se la colonna del database non è vuota, ANDREBBE FATTO OGNI VOLTA CHE SI GUARDA UNA COLONNA DI UN DATABASE ALTRIMENTI L'ASSEGNAMENTO A NULL DA ERRORE
            cel=PhoneNumber() #crea il modello cellulare
            cel.Value.Value=profilo['phone_number'].Value
            account.Entries.Add(cel) #aggiungi l'entry del numero di cellulare nel profilo
            cel.Deleted=DeletedState.Intact
            cel.Domain.Value=" "
        
        account.Notes.Add("data di nascita: "+str(TimeStamp.FromUnixTime(int64_to_unixtimestamp(profilo['birth_date'].Value, 'ms')))) #aggiungi alle note del profilo la data di nascita
        
        
        ds.Models.Add(account) #aggiungi l'account all'elenco dei modelli account presenti
        

def JustEat_Parsing():
    jelocation_db=SQLiteParser.Database.FromNode(cellulare['/data/data/com.justeat.app.it/databases/je-location-db'])
    
    for indirizzo in jelocation_db['recent_search']: 
        posizione=Location() #potresti anche usare il modelllo SearchedItem ma credo sia meglio Location
        posizione.Deleted=DeletedState.Intact
        posizione.Position.Value=Coordinate(indirizzo['latitude'].Value, indirizzo['longitude'].Value) #aggiungi una coordinata con latitudine e longitude
        posizione.Source.Value='JustEat'
        posizione.TimeStamp.Value=TimeStamp.FromUnixTime(int64_to_unixtimestamp(indirizzo['inserted'].Value, 'ms'))
        
        ind=StreetAddress() #crea un modello StreetAddress per memorizzare tutti i dati sull'indirizzo
        ind.Deleted=DeletedState.Intact
        ind.Street1.Value=indirizzo['street'].Value+" "+indirizzo['street_number'].Value #via e numero civico
        #ind.HouseNumber.Value=int(indirizzo['street_number'].Value)
        ind.City.Value=indirizzo['city'].Value
        ind.PostalCode.Value=indirizzo['postcode'].Value
        
        posizione.Address.Value=ind
        
        ds.Models.Add(posizione)

def GoogleQuickSearchBox_Parsing(): #funzione che fa il parsing di Google Quick Search Box
    WebView_LastExit('/data/data/com.google.android.googlequicksearchbox/app_webview/last-exit-info',"Google Quick Search Box")
     
def Outlook_Parsing():
    WebView_LastExit('/data/data/com.microsoft.office.outlook/app_webview/last-exit-info',"Outlook")
     
def Facebook_Parsing():
    WebView_LastExit('/data/data/com.facebook.katana/app_webview_embedded/last-exit-info',"Facebook") #fai il parsing dell'ultima uscita dalla WebView di Facebook compresa la WebView associata al browser

def Telegram_Parsing():
    WebView_LastExit('/data/data/org.telegram.messenger/app_webview/last-exit-info',"Telegram")
     
def Gmail_Parsing():
    WebView_LastExit('/data/data/com.google.android.gm/app_webview/last-exit-info',"Gmail")
    
def GooglePlay_Parsing():
    WebView_LastExit('/data/data/com.google.android.gms/app_webview/last-exit-info',"Google Play")

def Eurosport_Parsing():
    WebView_LastExit('/data/data/com.eurosport/app_webview/last-exit-info',"Eurosport")
    
def McDonalds_Parsing():
    WebView_LastExit('/data/data/com.mcdonalds.mobileapp/app_webview/last-exit-info',"McDonald's")
    
def Instagram_Parsing():
    WebView_LastExit('/data/data/com.instagram.android/app_webview/last-exit-info',"Instagram")

def LaGazzettaDelloSport_Parsing():
    WebView_LastExit('/data/data/it.rcs.gazzettaflash/app_webview/last-exit-info',"La Gazzetta dello Sport")

def IntesaSanPaoloMobile_Parsing():
    WebView_LastExit('/data/data/com.latuabancaperandroid/app_webview/last-exit-info',"Intesa San Paolo Mobile")
    
def SamsungApps_Parsing():
    WebView_LastExit('/data/data/com.sec.android.app.samsungapps/app_webview/last-exit-info',"Samsung Apps")

def LegheFC_Parsing():
    WebView_LastExit('/data/data/it.quadronica.leghe/app_webview/last-exit-info',"Leghe FC")
    
def WhatsApp_Parsing():
    WebView_LastExit('/data/data/com.whatsapp/app_webview/last-exit-info',"WhatsApp")
    
def CaptivePortalLogin_Parsing(): #servizio di login per portal captive dove i portal captive è una pagina web che gli utenti devono visualizzare e interagire prima di accedere a una rete pubblica Wi-Fi
    WebView_LastExit('/data/data/com.google.android.captiveportallogin/app_webview/last-exit-info',"Captive Portal Login")

def Trenitalia_Parsing():
    WebView_LastExit('/data/data/com.lynxspa.prontotreno/app_webview/last-exit-info',"Trenitalia")
    
    adobemobile=cellulare['/data/data/com.lynxspa.prontotreno/shared_prefs/AdobeMobile_Lifecycle.xml'].Data.read() #PENSA SE USARE UNA FUNZIONE APPOSITA PER IL PARSING DI TUTTI GLI ADOMOBOBILE COME PER I LAST_EXIT
    
    usoapp=ApplicationUsage() #aggiungi un modello per l'uso di un applicazione
    usoapp.Deleted=DeletedState.Intact
    usoapp.Source.Value='Trenitalia'
    
    usoapp.Name.Value=adobemobile.split('"AppId">')[1].split(' ')[0]
    
    usoapp.LaunchCount.Value=int(adobemobile.split('"Launches" value="')[1].split('"')[0]) #aggiungi il numero di volte in cui l'applicazione è stata lanciata
    
    usoapp.Date.Value= TimeStamp.FromUnixTime(int64_to_unixtimestamp(int(adobemobile.split('"UpgradeDate" value="')[1].split('"')[0]), 's')) #assegna la data di ultimo aggiornamento
    
    usoapp.LastLaunch.Value= TimeStamp.FromUnixTime(int64_to_unixtimestamp(int(adobemobile.split('"LastDateUsed" value="')[1].split('"')[0]), 's')) #aggiungi la data dell'ultimo lancio
    
    ds.Models.Add(usoapp)
    
    
def Unicredit_Parsing():
    WebView_LastExit('/data/data/com.unicredit/app_webview/last-exit-info',"Unicredit")

def ItaloTreno_Parsing():
    WebView_LastExit('/data/data/it.italotreno/app_webview/last-exit-info',"Italo Treno")
    
def SamsungAccount_Parsing():
    WebView_LastExit('/data/data/com.osp.app.signin/app_webview/last-exit-info',"Samsung Account")
    
def GoogleDrive_Parsing():
    WebView_LastExit('/data/data/com.google.android.apps.docs/app_webview/last-exit-info',"Google Drive")
     
def Microsoft365Office_Parsing():
    WebView_LastExit('/data/data/com.microsoft.office.officehubrow/app_webview_com.microsoft.office.officehubrow/last-exit-info',"Microsoft 365(Office)")
    
def Upday_Parsing():
    WebView_LastExit('/data/data/de.axelspringer.yana.zeropage/app_webview/last-exit-info',"Upday")

def Vodafone_Parsing():
    WebView_LastExit('/data/data/it.vodafone.my190/app_webview/last-exit-info',"Vodafone")
    
def ATMMilano_Parsing():
    WebView_LastExit('/data/data/it.atm.appmobile/app_webview/last-exit-info',"ATM Milano Mobile")
    
def Teams_Parsing():
    WebView_LastExit('/data/data/com.microsoft.teams/app_webview/last-exit-info',"Teams")
    
def Youtube_Parsing():
    WebView_LastExit('/data/data/com.google.android.youtube/app_webview/last-exit-info',"Youtube")

def ProtonVPN_Parsing():
    db=SQLiteParser.Database.FromNode(cellulare['/data/data/ch.protonvpn.android/databases/db'])
    
    for profilo in db['UserEntity']:
        account=UserAccount()
        
        if IsDBNull (profilo['name'].Value) == False: #se la colonna del database non è vuota
            account.Name.Value=profilo['name'].Value
        
        account.Username.Value=profilo['email'].Value
        account.ServiceType.Value= "ch.protonvpn.android"
        account.Source.Value="ProtonVPN"
        
        account.Deleted=DeletedState.Intact #imposta il fatto che l'elemento non è stato cancellato
           
        account.TimeCreated.Value=TimeStamp.FromUnixTime(int64_to_unixtimestamp(profilo['createdAtUtc'].Value, 'ms'))
        
        account.Notes.Add("Moneta: "+profilo['currency'].Value+" credito account: "+str(profilo['credit'].Value)) #aggiungi alle note del profilo la moneta utilizzata e il credito sul profilo
        
        
        ds.Models.Add(account) #aggiungi l'account all'elenco dei modelli account presenti

def Aptoide_Parsing():  
    #da aggiungere un elenco delle notifiche e un CarvedString che contiene l'elenco delle applicazioni installat e e gli che store che aptoide utilizza
    aptoide_db= SQLiteParser.Database.FromNode(cellulare['/data/data/cm.aptoide.pt/databases/aptoide.db'])
    
    
    for notification in aptoide_db['notification']:
        notifica=Notification() 
        
        if IsDBNull(notification['body'].Value) == False:
            #print(notification['body'].Value)
            notifica.Body.Value=notification['body'].Value #aggiungi il body della notifica
            
        if notification['timeStamp'].Value> 0:
            notifica.TimeStamp.Value=TimeStamp.FromUnixTime(int64_to_unixtimestamp(notification['timeStamp'].Value, 'ms'))
        
        url=WebAddress() #crea un modello WebAddress
        
        url.Deleted=DeletedState.Intact
        
        url.Value.Value=notification['url'].Value
        
        notifica.Urls.Add(url) #aggiungi l'URL a cui si riferisce la notizia
        
        notifica.Source.Value="Aptoide"
        
        
        notifica.Deleted=DeletedState.Intact
        
       
        ds.Models.Add(notifica)
    
    
    stringa=CarvedString()
    
    stringa.Deleted=DeletedState.Intact
    
    stringa.Source.Value="Aptoide"
    
    stringa.Value.Value="Applicazioni installate da aptoide: "+"\n"
    for pacchetto in aptoide_db['aptoideinstallapp']: #scorri tutte le app installate con aptoide
        stringa.Value.Value=stringa.Value.Value+pacchetto['packageName'].Value+"\n"
    
    stringa.Value.Value=stringa.Value.Value+"\n"+"Store utilizzati: "+"\n"
    for store in aptoide_db['store']: #scorri tutte gli store che sono utilizzati da aptoide
        stringa.Value.Value=stringa.Value.Value+store['storeName'].Value+"\n"
    
    ds.Models.Add(stringa)
    
    
    
def Teamviewer_Parsing():
    connessioni=cellulare['/data/data/com.teamviewer.teamviewer.market.mobile/files/connection.txt'].Data.read().split('\n')
    
    stringa=CarvedString()
    
    stringa.Deleted=DeletedState.Intact
    
    stringa.Source.Value="Teamviewer"
    
    stringa.Value.Value="ELENCO CONNESSIONI\n"
    
    for numeroriga in range(len(connessioni)-1): #scorri tutto il file per riga (-1 perchè il file termina con una riga vuota)
        riga=connessioni[numeroriga].split(' ')
        
        stringa.Value.Value=stringa.Value.Value+"ID Teamviewer: "+riga[0]+"   Connessione da: "+riga[23]+" "+riga[24]+" a: "+riga[33]+" "+riga[34]+"   Account: "+riga[43]+" "+riga[44]+"   Tipologia: "+riga[59]+"\n\n" 
 
 
    ds.Models.Add(stringa)
    
def AndroidAuto_Parsing():
    #da fare eventualmente il parsing del file primes.xml
    pass

#def Zoom_Parsing():
    #trovato nulla
#    pass
    
def Booking_Parsing():
    notifications_db= SQLiteParser.Database.FromNode(cellulare['/data/data/com.booking/databases/notifications.db'])
    
    
    for notification in notifications_db['notification']:
        notifica=Notification() 
        
        if IsDBNull(notification['body'].Value) == False:
            
            notifica.Body.Value=notification['title'].Value+"\n"+notification['body'].Value #aggiungi il body della notifica e il suo titolo
            
        if notification['time_epoch'].Value> 0:
            notifica.TimeStamp.Value=TimeStamp.FromUnixTime(int64_to_unixtimestamp(notification['time_epoch'].Value,'s')) 
        
        notifica.Source.Value="Booking"
        
        
        notifica.Deleted=DeletedState.Intact
        
        
        ds.Models.Add(notifica)
        
    
    mybooking=cellulare['/data/data/com.booking/shared_prefs/mybooking.xml'].Data.read()
    #print (mybooking)
    
    
    account=UserAccount()
    account.Source.Value="Booking"
    account.Deleted=DeletedState.Intact
    
    account.ServiceType.Value="com.booking"
    
    account.Name.Value=mybooking.split('"pref3firstname">')[1].split('<')[0]+" "+mybooking.split('"pref3lastname">')[1].split('<')[0]
    account.Username.Value=mybooking.split('"pref3email">')[1].split('<')[0]
    
    cel=PhoneNumber()
    cel.Domain.Value=" "
    cel.Deleted=DeletedState.Intact
    
    cel.Value.Value=mybooking.split('"pref3phone">')[1].split('<')[0]
    account.Entries.Add(cel)
    
    ind=StreetAddress() #crea un modello StreetAddress
    ind.Deleted=DeletedState.Intact
    ind.Street1.Value=mybooking.split('"pref3address">')[1].split('<')[0]
    ind.City.Value=mybooking.split('"pref3city">')[1].split('<')[0]
    ind.State.Value=mybooking.split('"pref3country">')[1].split('<')[0]
    
    account.Addresses.Add(ind) #aggiungi l'indirizzo all'account
    
    exps3_db=SQLiteParser.Database.FromNode(cellulare['/data/data/com.booking/databases/exps3.db'])
    
    for record in exps3_db['uvis']:
        if record['type'].Value=="email_address": #se il record del database è una email
                
                email=record['uvi'].Value
                if(str(email)!=' ' and email!=account.Username.Value):#se la mail non è vuota e non corrisponde a quella di mybooking.xml 
                    
                    account2=UserAccount() #crea un altro account utente
                    account2.Source.Value="Booking"
                    account2.Deleted=DeletedState.Intact
                    account2.ServiceType.Value="com.booking"
                    
                    account2.Username.Value=email
                    
                    ds.Models.Add(account2)
    
    ds.Models.Add(account)
    
    postbooking_db=SQLiteParser.Database.FromNode(cellulare['/data/data/com.booking/databases/post_booking_reservation_cache'])
    
    stringa=CarvedString()
    stringa.Source.Value="Booking"
    stringa.Deleted=DeletedState.Intact
    
    stringa.Value.Value="PRENOTAZIONI"+'\n'
    
    #pin=0
    for prenotazione in postbooking_db['records']: #scorri tutti i record del database postbooking (SEMBRA CHE QUESTO DATABASE VENGA SCORSO DAL BASSO VERSO L'ALTO, CONTROLLA)
        if str(prenotazione['key'].Value).endswith('.reservation.property'): #se la stringa termina con .reservation.property 
            stringa.Value.Value=stringa.Value.Value+"Luogo: "+str(prenotazione['record'].Value).split(':"')[1].split('"')[0]+"   "
            
            #print(str(prenotazione['record'].Value).split(':"')[1].split('"')[0].split('T'))
        
        elif str(prenotazione['key'].Value).endswith('.reservation'): #se la stringa termina esattamente con .reservation
            starttime= str(prenotazione['record'].Value).split('startDateTime":"')[1].split('"')[0].split('T')[0]+" "+str(prenotazione['record'].Value).split('startDateTime":"')[1].split('"')[0].split('T')[1]
            endtime= str(prenotazione['record'].Value).split('endDateTime":"')[1].split('"')[0].split('T')[0]+" "+str(prenotazione['record'].Value).split('endDateTime":"')[1].split('"')[0].split('T')[1]
            
            stringa.Value.Value=stringa.Value.Value+"Inizio: "+starttime+" Fine: "+endtime+"\n"
    
        
    ds.Models.Add(stringa)

    
def Deliveroo_Parsing():
    roorder=cellulare['/data/data/com.deliveroo.orderapp/shared_prefs/RooOrderApp.txt.xml'].Data.read()
    
    posizione=Location()
    posizione.Deleted=DeletedState.Intact
    posizione.Source.Value='Deliveroo'
    
    posizione.Position.Value=Coordinate(float(roorder.split('location_lat">')[1].split('<')[0]), float(roorder.split('location_lng">')[1].split('<')[0])) #aggiungi una coordinata con latitudine e longitude
    
    posizione.TimeStamp.Value=TimeStamp.FromUnixTime(int64_to_unixtimestamp(int(roorder.split('timestamp" value="')[1].split('"')[0]), 'ms'))
    
    posizione.Description.Value="Ultimo metodo di pagamento: "+roorder.split('method_type">')[1].split('<')[0]
    
    ds.Models.Add(posizione)
    
def Glovo_Parsing():
    glovo_db=SQLiteParser.Database.FromNode(cellulare['/data/data/com.glovo/databases/glovo.db'])
    
    for ubicazione in glovo_db['hyperlocal_locations']: 
        posizione=Location()
        posizione.Deleted=DeletedState.Intact
        posizione.Source.Value='Glovo'
        
        if (ubicazione['hyperlocal_last_used'].Value >0): #se il timestamp non è zero
            posizione.TimeStamp.Value=TimeStamp.FromUnixTime(int64_to_unixtimestamp(ubicazione['hyperlocal_last_used'].Value, 'ms'))
        
        posizione.Position.Value=Coordinate(ubicazione['hyperlocal_latitude'].Value, ubicazione['hyperlocal_longitude'].Value) #aggiungi una coordinata con latitudine e longitude
        
        
        
        ind=StreetAddress() #crea un modello StreetAddress per memorizzare tutti i dati sull'ubicazione
        ind.Deleted=DeletedState.Intact
        
        ind.City.Value= ubicazione['hyperlocal_city_code'].Value
        if IsDBNull (ubicazione['hyperlocal_title'].Value) == False: #se il record del database relativo all'indirizzo non è vuoto
            ind.Street1.Value=ubicazione['hyperlocal_title'].Value
        
        if IsDBNull (ubicazione['hyperlocal_description'].Value) == False: #se il record relativo ad informazioni extra non è vuoto
            posizione.Description.Value=ubicazione['hyperlocal_description'].Value
        
        posizione.Address.Value=ind
        
        ds.Models.Add(posizione)
        
        
    glovogeoadd_db=SQLiteParser.Database.FromNode(cellulare['/data/data/com.glovo/databases/glovoapp_geo_address_history.db'])
    
    for indirizzo in glovogeoadd_db['address_search_history']:
        ricerca=SearchedItem()
        ricerca.Source.Value="Glovo"
        ricerca.Deleted=DeletedState.Intact
        
        ricerca.TimeStamp.Value=TimeStamp.FromUnixTime(int64_to_unixtimestamp(indirizzo['last_used_timestamp'].Value, 'ms')) #assegna i timestamp delle ricerche, il timestamp è in millisecondi
        
        ricerca.Value.Value=indirizzo['full_address'].Value
        
        ricerca.Position.Value=Coordinate(indirizzo['latitude'].Value, indirizzo['longitude'].Value) 
        
        ds.Models.Add(ricerca)

def Netflix_Parsing():
    apphistory=SQLiteParser.Database.FromNode(cellulare['/data/data/com.netflix.mediaclient/databases/appHistory'])
    
    
    utilizzoapp=CarvedString() 
    
    utilizzoapp.Deleted=DeletedState.Intact
    utilizzoapp.Source.Value="Netflix"
    
    utilizzoapp.Value.Value="ELENCO CONTENUTI VISIONATI\n"
    for evento in apphistory['playEvent']:
        utilizzoapp.Value.Value=utilizzoapp.Value.Value+"Contenuto guardato il: "+ str(TimeStamp.FromUnixTime(int64_to_unixtimestamp(evento['eventTime'].Value, 'ms')))+" durata contenuto: "+str(evento['duration'].Value/60000)+" minuti" #divido per 6000 perchè trasformo da millisecondi a minuti
        
        for network in apphistory['sessionNetworkStatistics']:
            if int(evento['playableId'].Value)==int(network['streamId'].Value): #se il contenuto è lo stesso in entrambe le tabelles
                utilizzoapp.Value.Value=utilizzoapp.Value.Value+" IP: "+network['ip'].Value+" tipologia connessione: "+network['networkType'].Value+"\n" #aggiungi le informazioni relative alle connessioni utilizzate per il contenuto
        
    
    
    ds.Models.Add(utilizzoapp)
    
    

def Italo_Parsing():
    adobemobile=cellulare['/data/data/it.italotreno/shared_prefs/AdobeMobile_Lifecycle.xml'].Data.read()
    
    usoapp=ApplicationUsage() #aggiungi un modello per l'uso di un applicazione
    usoapp.Deleted=DeletedState.Intact
    usoapp.Source.Value='Italo'
    
    usoapp.Name.Value=adobemobile.split('"AppId">')[1].split(' ')[0]
    
    usoapp.LaunchCount.Value=int(adobemobile.split('"Launches" value="')[1].split('"')[0]) #aggiungi il numero di volte in cui l'applicazione è stata lanciata
    
    usoapp.Date.Value= TimeStamp.FromUnixTime(int64_to_unixtimestamp(int(adobemobile.split('"UpgradeDate" value="')[1].split('"')[0]), 's')) #assegna la data di ultimo aggiornamento
    
    usoapp.LastLaunch.Value= TimeStamp.FromUnixTime(int64_to_unixtimestamp(int(adobemobile.split('"LastDateUsed" value="')[1].split('"')[0]), 's')) #aggiungi la data dell'ultimo lancio
    
    ds.Models.Add(usoapp)

#def FlixBus_Parsing(): #TODO
#    pass
    
#def Chess_Parsing(): #TODO
#    pass



def int64_to_unixtimestamp(tp, type):  #funzione che trasforma da int64 a unixtimestamp     
    if (type=='ms'): # se il timestamp è in millisecondi
    
        dt=datetime.datetime.fromtimestamp(tp/1000) #trasforma da timestamp a datetime, il timestamp è in millisecondi quindi si divide per 1000, se fosse in microsecondi dividi per 1000000, in nanosecondi dividi per 1000000000
    
    if (type=='s'): # se il timestamp è in secondi
        
        dt=datetime.datetime.fromtimestamp(tp)
        
    
    unixtp=time.mktime(dt.timetuple()) #trasforma il datetime in timestamp unix con mktime, con .timetuple trasforma il datetame in una tupla di tipo time
    
    
        
    
    #print(TimeStamp.FromUnixTime(time.mktime(dt.timetuple())))
    
    ##dt=dt-datetime.datetime(1601,1,1) #calcola la differenza tra la data specificata e l'epoca FILETIME che è l'1-01-1601
    ##filetime= dt.days * 86400 * 10**7 + (dt.seconds-3600) * 10**7 + dt.microseconds * 10 #converti in intervalli da 100 nanosecondi, si ha 1 giorno=86400 secondi e 1 secondo= 10^7  100 nanosecondi, -3600 secondi perchè tolgo 1 ora al timestamp per l'UTC
    
    return unixtp

def WebView_LastExit(path, name): #funzione che fa il parsing del file last-exit-info della WebView di android frequente in molte app prendendo come parametri il percorso del file e il nome dell'app
    last_exit=CarvedString() 
    
    last_exit.Deleted=DeletedState.Intact
    last_exit.Source.Value=name+"(WebView)"
        
    ts=cellulare[path].Data.read().split(',')[1].split(':') #prendi il timestamp contenuto nel file last-exit-info splittando prima per , e poi splittando il secondo elemento per :
    
    if(name=="Facebook"): #facebook ha il last-exit-info sia della WebView e sia della WebView associata ad un browser
        ts_browser=cellulare['/data/data/com.facebook.katana/app_browser_proc_webview/last-exit-info'].Data.read().split(',')[1].split(':') #prendi il timestamp di last-exit-info che si riferisce al webview del browser
        last_exit.Value.Value="Ultima uscita dalla WebView: "+ str(TimeStamp.FromUnixTime(int64_to_unixtimestamp(int(ts[1]), 'ms')))+"\nUltima uscita dalla WebView del browser: "+str(TimeStamp.FromUnixTime(int64_to_unixtimestamp(int(ts_browser[1]),'ms')))  
        #ds.Models.Add(last_exit)
        
    elif(name=="Google Play"): #Google Play ha il last-exit info sia della WebView e sia della WebView associata a AdMob
        ts_admob=cellulare['/data/data/com.google.android.gms/app_webview_admob-service/last-exit-info'].Data.read().split(',')[1].split(':')
        last_exit.Value.Value="Ultima uscita dalla WebView: "+ str(TimeStamp.FromUnixTime(int64_to_unixtimestamp(int(ts[1]),'ms')))+"\nUltima uscita dalla WebView di AdMob: "+str(TimeStamp.FromUnixTime(int64_to_unixtimestamp(int(ts_admob[1]), 'ms')))  
        #ds.Models.Add(last_exit)
        
    elif(name=="Microsoft 365(Office)"): #Microsoft 365 ha il last-exit info sia della WebView riferita all'applicazione generale e sia della WebView associata specifichitamente ad Excel
        ts_excel=cellulare['/data/data/com.microsoft.office.officehubrow/app_webview_com.microsoft.office.officemobile.excel/last-exit-info'].Data.read().split(',')[1].split(':')
        last_exit.Value.Value="Ultima uscita dalla WebView: "+ str(TimeStamp.FromUnixTime(int64_to_unixtimestamp(int(ts[1]), 'ms')))+"\nUltima uscita dalla WebView di Excel: "+str(TimeStamp.FromUnixTime(int64_to_unixtimestamp(int(ts_excel[1]),'ms')))  
        #ds.Models.Add(last_exit)
    else:
        last_exit.Value.Value="Ultima uscita dalla WebView: "+ str(TimeStamp.FromUnixTime(int64_to_unixtimestamp(int(ts[1]),'ms'))) #prendi il timestamp contenuto nel file last-exit-info splittando prima per , e poi splittando il secondo elemento per :
        #ds.Models.Add(last_exit)
    
    ds.Models.Add(last_exit)

def main():    
    print("******NUOVA ESECUZIONE********")
    
    Check_Installed_App()
    
    Check_Hash()
    
    f_gmail=False #flag per controllare più occorrenze di gmail
    f_grdive=False #flag per controllare più occorrenze googledrive
    
    for app in listapp: #puoi anche fare direttamente con if any("paypal" in app for app in listapp)
        if "paypal" in app: #se è presente paypal nelle app installate
            ##parsing.Children.Add(Directory("paypal")) #aggiungi la cartella paypal al parsing
            ##parsing.Children.Add(File("prova.txt"))
            Paypal_Parsing()
            
        elif "ryanair" in app:
            Ryanair_Parsing()
            
        elif "justeat" in app:
            JustEat_Parsing()
        
        elif "googlequicksearchbox" in app:
            GoogleQuickSearchBox_Parsing()
            
        elif "outlook" in app:
            Outlook_Parsing()
        
        elif "facebook.katana" in app:
            Facebook_Parsing()
        
        elif "telegram" in app:
            Telegram_Parsing()
            
        elif "com.google.android.gm" in app:
            if (f_gmail==False): #se non è stato ancora trovata una corrispondenza tra la lista di app
                Gmail_Parsing()
                f_gmail=True #la corrispondeza è già stata trovata quindi metti a True il flag in modo da evitare di aggiungere più volte la stessa cosa essendo che gmail ha più rispondenti
            
            
        elif "play.games" in app:
            GooglePlay_Parsing()
        
        elif "eurosport" in app:
            Eurosport_Parsing()
        
        elif "mcdonalds" in app:
            McDonalds_Parsing()
            
        elif "instagram" in app: 
            Instagram_Parsing()
            
        elif "gazzetta" in app:
            LaGazzettaDelloSport_Parsing()
            
        elif "latuabancaperandroid" in app:
            IntesaSanPaoloMobile_Parsing()
            
        elif "samsungapps" in app:
            SamsungApps_Parsing()
            
        elif "quadronica.leghe" in app:
            LegheFC_Parsing()
        
        elif "whatsapp" in app:
            WhatsApp_Parsing()
        
        elif "google.android.captiveportallogin" in app:
            CaptivePortalLogin_Parsing()
        
        elif "prontotreno" in app:
            Trenitalia_Parsing()
        
        elif "unicredit" in app:
            Unicredit_Parsing()
            
        elif "italotreno" in app:
            ItaloTreno_Parsing()
            
        elif "osp.app" in app:
            SamsungAccount_Parsing()
            
        elif "com.google.android.apps.docs" in app:
            if (f_grdive==False):
                GoogleDrive_Parsing()
                f_grdive=True
         
        elif "officehubrow" in app:
            Microsoft365Office_Parsing()
        
        elif "yana.zeropage" in app:  
            Upday_Parsing()
            
        elif "atm.appmobile" in app:
            ATMMilano_Parsing()
            
        elif "teams" in app:
            Teams_Parsing()
        
        elif "youtube" in app:
            Youtube_Parsing()
          
        elif "vodafone" in app:
            Vodafone_Parsing()
        
        elif "protonvpn" in app:
            ProtonVPN_Parsing()
        
        elif "aptoide" in app:
            Aptoide_Parsing()
            
        elif "teamviewer" in app:
            Teamviewer_Parsing()
            
        #elif "projection.gearhead" in app:
        #    AndroidAuto_Parsing()
        
        #elif "zoom" in app:
        #    Zoom_Parsing()
       
        elif "booking" in app:
            Booking_Parsing()
       
        elif "glovo" in app:
            Glovo_Parsing()
            
        elif "deliveroo" in app:
            Deliveroo_Parsing()
            
        elif "netflix.mediaclient" in app:
            Netflix_Parsing()
        
        if "italotreno" in app: #con elif non funziona e viene ignorata la condizione
            Italo_Parsing()
        
        #elif "flixbus" in app:
        #    FlixBus_Parsing()
        
        #elif "chess" in app: 
        #    Chess_Parsing()
            
    
    ###ds.FileSystems.Add(parsing) #aggiungi il filesystem al datastore
    
    

    #DA QUI PEZZI DI CODICE CHE POSSONO ESSERE EVENTUALMENTE UTILI(PENSA SE CANCELLARLI)



#def datetime_to_int32(dt):  #funzione che trasforma da datetime a int32 (SI HA COME ANNO LIMITE IL 2048 ESSENDO UN INT32, QUINDI QUANDO PUOI USA GLI ALTIRI)
     # Epoch Unix
#    epoch = datetime.datetime(1970, 1, 1)
    
    # Calcola il timestamp Unix in secondi
#    timestamp = int((dt - epoch).total_seconds()-3600) #sottrai 3600 perchè togli 1 ora al timestamp per l'UTC
    
#    print(timestamp)
#    return timestamp


#print(type(profilo['birth_date'].Value))
#print(TimeStamp.FromFileTime(profilo['birth_date'].Value))


    
    '''print(db)
    print(db.DBNode)
    print(db.DBWalNode)
    print(db.Tables)'''

    '''d= Directory("mydirectory3") #crea il nodo di tipo directory "mydirectory3"
    d.Children.Add(File("fileprova.txt")) #aggiungi alla directory il file fileprova.txt 
    
    cellulare.Children.Add(d) #aggiungi la directory al filesystem''' 
    

    '''fs = FileSystem("mio_filesystem_12") #crea un nuovo nodo filesystem 
    ds.FileSystems.Add (fs) #aggiungi un filestem al DataStore che comprende tutti i dati di un progetto del physical analizer, in una singola linea si fa con ds.FileSystems.Add(FileSystem("filesystem_8"))

    fs.Children.Add(Node("prova",NodeType.File)) #aggiungi un nodo al file system appena creato'''
    
    #cellulare.Children.Add(Node("directory2",NodeType.Directory)) #aggiungi una directory al filesystem

    #ds.FileSystems[0].Children.Add(Directory("mydirectory4")) #aggiungi una directory al filesystem senza usare variabili
    
    #f2=File("fileprova.txt") #crea un nodo di tipo File
    
    #ds.FileSystems[0].Children.Add(Node("nuova_directory",NodeType.Directory))


    #ins_app=open('C:\\Users\\alessandro.tsulis\\Desktop\\UFED_acquisizione\\app_installate.txt','w+')
    #dis_app=open('C:\\Users\\alessandro.tsulis\\Desktop\\UFED_acquisizione\\app_disintallate.txt','w+')
    #with open ('C:\\Users\\alessandro.tsulis\\Desktop\\UFED_acquisizione\\app_installate.txt','w+') as ins_app:
    #with open ('C:\\Users\\alessandro.tsulis\\Desktop\\ROBA_TESI\\app_installate.txt','w+') as ins_app:

     
"""if __name__ == '__main__': #FACENDO COSì NON VA, CI SONO ALCUNI MODI DI FARE LE COSE IN PYTHON CHE IMPORTATI IN UFED CON SCRIPT ESTERNI NON FUNZIONANO NON SO PERCHè, FORSE PERCHè POTREBBE BASARSI SU IRONPYTHON2.7(CHE IN TEORIA è SOLO LA GUI, MA NON HO ALTRE IPOTESI)
    main()"""

main()