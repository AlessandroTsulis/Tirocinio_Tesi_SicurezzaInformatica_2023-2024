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

#PENSA SE USARE GLOBAL NEL MAIN INVECE CHE METTERE LE VARIABILI QUI
cellulare=ds.FileSystems[0] #accedi al primo filesystem presente, se l'acquisizione è un cellulare allora è il filesystem del cellulare vale per una full file system
listapp=[] #lista delle applicazioni installate del cellulare

def Check_Installed_App(): #funzione che calcola l'elenco delle applicazioni installate    
    localapp_db=SQLiteParser.Database.FromNode(cellulare['/data/data/com.android.vending/databases/localappstate.db']) #fai il parsing del database localappstate.db
    
    for riga in cellulare['/data/system/packages.list'].Data.read().split('\n'): #leggi i dati in packages.list per riga
        #print(riga) 
        listapp.append(riga.split(' ')[0]) #prendi l'applicazione dalla riga e aggiungila alla lista delle app installate

#FAI UNA FUNZIONE PER OGNI APPLICAZIONE (PENSA SE USARE LE CLASSI COME NELL'ESEMPIO FIREFOX_PARSER)


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
        ricerca.TimeStamp.Value=TimeStamp.FromUnixTime(int64_to_unixtimestamp(stazione['last_usage'].Value)) #assegna i timestamp delle ricerche
        
        ricerca.Value.Value="From station: "+stazione['origin_station_code'].Value+" to station: "+stazione['station_code'].Value
        #ricerca.Account="prova" #DA CAPIRE SE E COME SI PUò ACCEDERE AD ALCUNI ELEMENTI DEI DATABASE
        #ricerca.Parameters="prova"
        
        ###ds.Models.Add(ricerca)
   
    
    for profilo in frlocal_db['user_profile']: #per aggiungere account utente ryanair
        account=UserAccount() #crea un modello account
        account.Name.Value=profilo['first_name'].Value+profilo['last_name'].Value #assegna al nome dell'account nome e cognome
        account.Username.Value=profilo['email'].Value
        account.ServiceType.Value= "com.ryanair.cheapflights"
        account.Source.Value="Ryanair"
        #account.Source=profilo['first_name'].Source #EVENTUALMENTE DA CAPIRE MEGLIO COME UTILIZZARE SOURCE PER IMPOSTARE ANCHE SOURCE INFORMATION
        
        
        account.Deleted=DeletedState.Intact #imposta il fatto che l'elemento non è stato cancellato
           
        account.TimeCreated.Value=TimeStamp.FromUnixTime(int64_to_unixtimestamp(profilo['member_since'].Value)) #trasfroma da int64 a timestamp unix e poi da unix timestamp a timestamp di UFED e lo assegna alla data di crezione dell'account
        
        if IsDBNull (profilo['phone_number'].Value) == False: #se la colonna del database non è vuota, ANDREBBE FATTO OGNI VOLTA CHE SI GUARDA UNA COLONNA DI UN DATABASE ALTRIMENTI L'ASSEGNAMENTO A NULL DA ERRORE
            cel=PhoneNumber() #crea il modello cellulare
            cel.Value.Value=profilo['phone_number'].Value
            account.Entries.Add(cel) #aggiungi l'entry del numero di cellulare nel profilo

        
        account.Notes.Add("data di nascita: "+str(TimeStamp.FromUnixTime(int64_to_unixtimestamp(profilo['birth_date'].Value)))) #aggiungi alle note del profilo la data di nascita
        
        
        ###ds.Models.Add(account) #aggiungi l'account all'elenco dei modelli account presenti
        

def JustEat_Parsing():
    jelocation_db=SQLiteParser.Database.FromNode(cellulare['/data/data/com.justeat.app.it/databases/je-location-db'])
    
    for indirizzo in jelocation_db['recent_search']: 
        posizione=Location() #potresti anche usare il modelllo SearchedItem ma credo sia meglio Location
        posizione.Deleted=DeletedState.Intact
        posizione.Position.Value=Coordinate(indirizzo['latitude'].Value, indirizzo['longitude'].Value) #aggiungi una coordinata con latitudine e longitude
        posizione.Source.Value='JustEat'
        posizione.TimeStamp.Value=TimeStamp.FromUnixTime(int64_to_unixtimestamp(indirizzo['inserted'].Value))
        
        ind=StreetAddress() #crea un modello StreetAddress per memorizzare tutti i dati sull'indirizzo
        ind.Deleted=DeletedState.Intact
        ind.Street1.Value=indirizzo['street'].Value+" "+indirizzo['street_number'].Value #via e numero civico
        #ind.HouseNumber.Value=int(indirizzo['street_number'].Value)
        ind.City.Value=indirizzo['city'].Value
        ind.PostalCode.Value=indirizzo['postcode'].Value
        
        posizione.Address.Value=ind
        
        ###ds.Models.Add(posizione)

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

def int64_to_unixtimestamp(tp):  #funzione che trasforma da int64 a unixtimestamp     
    dt=datetime.datetime.fromtimestamp(tp/1000) #trasforma da timestamp a datetime, il timestamp è in millisecondi quindi si divide per 1000, se fosse in microsecondi dividi per 1000000, in nanosecondi dividi per 1000000000
    
    unixtp=time.mktime(dt.timetuple()) #trasforma il datetime in timestamp unix con mktime, con .timetuple trasforma il datetame in una tupla di tipo time
    #print(TimeStamp.FromUnixTime(time.mktime(dt.timetuple())))
    
    ##dt=dt-datetime.datetime(1601,1,1) #calcola la differenza tra la data specificata e l'epoca FILETIME che è l'1-01-1601
    ##filetime= dt.days * 86400 * 10**7 + (dt.seconds-3600) * 10**7 + dt.microseconds * 10 #converti in intervalli da 100 nanosecondi, si ha 1 giorno=86400 secondi e 1 secondo= 10^7  100 nanosecondi, -3600 secondi perchè tolgo 1 ora al timestamp per l'UTC
    
    return unixtp

def WebView_LastExit(path, name): #funzione che fa il parsing del file last-exit-info della WebView di android frequente in molte app prendendo come parametri il percorso del file e il nome dell'app
    last_exit=CarvedString() 
    
    last_exit.Deleted=DeletedState.Intact
    last_exit.Source.Value=name
        
    ts=cellulare[path].Data.read().split(',')[1].split(':') #prendi il timestamp contenuto nel file last-exit-info splittando prima per , e poi splittando il secondo elemento per :
    
    if(name=="Facebook"): #facebook ha il last-exit-info sia della WebView e sia della WebView associata ad un browser
        ts_browser=cellulare['/data/data/com.facebook.katana/app_browser_proc_webview/last-exit-info'].Data.read().split(',')[1].split(':') #prendi il timestamp di last-exit-info che si riferisce al webview del browser
        last_exit.Value.Value="Ultima uscita dalla WebView: "+ str(TimeStamp.FromUnixTime(int64_to_unixtimestamp(int(ts[1]))))+"\nUltima uscita dalla WebView del browser: "+str(TimeStamp.FromUnixTime(int64_to_unixtimestamp(int(ts_browser[1]))))  
        #ds.Models.Add(last_exit)
        
    elif(name=="Google Play"): #Google Play ha il last-exit info sia della WebView e sia della WebView associata a AdMob
        ts_admob=cellulare['/data/data/com.google.android.gms/app_webview_admob-service/last-exit-info'].Data.read().split(',')[1].split(':')
        last_exit.Value.Value="Ultima uscita dalla WebView: "+ str(TimeStamp.FromUnixTime(int64_to_unixtimestamp(int(ts[1]))))+"\nUltima uscita dalla WebView di AdMob: "+str(TimeStamp.FromUnixTime(int64_to_unixtimestamp(int(ts_admob[1]))))  
        #ds.Models.Add(last_exit)
        
    elif(name=="Microsoft 365(Office)"): #Microsoft 365 ha il last-exit info sia della WebView riferita all'applicazione generale e sia della WebView associata specifichitamente ad Excel
        ts_excel=cellulare['/data/data/com.microsoft.office.officehubrow/app_webview_com.microsoft.office.officemobile.excel/last-exit-info'].Data.read().split(',')[1].split(':')
        last_exit.Value.Value="Ultima uscita dalla WebView: "+ str(TimeStamp.FromUnixTime(int64_to_unixtimestamp(int(ts[1]))))+"\nUltima uscita dalla WebView di Excel: "+str(TimeStamp.FromUnixTime(int64_to_unixtimestamp(int(ts_excel[1]))))  
        #ds.Models.Add(last_exit)
    else:
        last_exit.Value.Value="Ultima uscita dalla WebView: "+ str(TimeStamp.FromUnixTime(int64_to_unixtimestamp(int(ts[1])))) #prendi il timestamp contenuto nel file last-exit-info splittando prima per , e poi splittando il secondo elemento per :
        #ds.Models.Add(last_exit)
    
    ds.Models.Add(last_exit)

def main():    
    print("******NUOVA ESECUZIONE********")
    
    Check_Installed_App()
    ###parsing=FileSystem("Parsing")
    f_gmail=False #flag per controllare più occorrenze di gmail
    f_grdive=False #flag per controllare più occorrenze googledrive
    
    for app in listapp: #puoi anche fare direttamente con if any("paypal" in app for app in listapp)
        if "paypal" in app: #se è presente paypal nelle app installate
            ##parsing.Children.Add(Directory("paypal")) #aggiungi la cartella paypal al parsing
            ##parsing.Children.Add(File("prova.txt"))
            Paypal_Parsing()
        
        if "ryanair" in app:
            Ryanair_Parsing()
            
        if "justeat" in app:
            JustEat_Parsing()
        
        if "googlequicksearchbox" in app:
            GoogleQuickSearchBox_Parsing()
            
        if "outlook" in app:
            Outlook_Parsing()
        
        if "facebook.katana" in app:
            Facebook_Parsing()
        
        if "telegram" in app:
            Telegram_Parsing()
            
        if "com.google.android.gm" in app:
            if (f_gmail==False): #se non è stato ancora trovata una corrispondenza tra la lista di app
                Gmail_Parsing()
                f_gmail=True #la corrispondeza è già stata trovata quindi metti a True il flag in modo da evitare di aggiungere più volte la stessa cosa essendo che gmail ha più rispondenti
            
            
        if "play.games" in app:
            GooglePlay_Parsing()
        
        if "eurosport" in app:
            Eurosport_Parsing()
        
        if "mcdonalds" in app:
            McDonalds_Parsing()
            
        if "instagram" in app: 
            Instagram_Parsing()
            
        if "gazzetta" in app:
            LaGazzettaDelloSport_Parsing()
            
        if "latuabancaperandroid" in app:
            IntesaSanPaoloMobile_Parsing()
            
        if "samsungapps" in app:
            SamsungApps_Parsing()
            
        if "quadronica.leghe" in app:
            LegheFC_Parsing()
        
        if "whatsapp" in app:
            WhatsApp_Parsing()
        
        if "google.android.captiveportallogin" in app:
            CaptivePortalLogin_Parsing()
        
        if "prontotreno" in app:
            Trenitalia_Parsing()
        
        if "unicredit" in app:
            Unicredit_Parsing()
            
        if "italotreno" in app:
            ItaloTreno_Parsing()
            
        if "osp.app" in app:
            SamsungAccount_Parsing()
            
        if "com.google.android.apps.docs" in app:
            if (f_grdive==False):
                GoogleDrive_Parsing()
                f_grdive=True
         
        if "officehubrow" in app:
            Microsoft365Office_Parsing()
        
        if "yana.zeropage" in app:  
            Upday_Parsing()
            
        if "atm.appmobile" in app:
            ATMMilano_Parsing()
            
        if "teams" in app:
            Teams_Parsing()
        
        if "youtube" in app:
            Youtube_Parsing()
          
        if "vodafone" in app:
            Vodafone_Parsing()
            
    
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