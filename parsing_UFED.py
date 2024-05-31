# coding=utf-8 per definire l'encoding
#Quando importi da script esterni ricorda di utilizzare il decoding scope (l'applicative scope da errori) 
from physical import * #per utilizzare le API UFED in script esterni
import sys
#import shutil  #per copiare i file usa shutil
import SQLiteParser #libreria per il parsing di database
import datetime #modello per trasformare da timestamp a datetime
from System.Convert import IsDBNull #per controllare se un record di un database è Null
#import numpy as np
import time

#PENSA SE USARE GLOBAL NEL MAIN INVECE CHE METTERE LE VARIABILI QUI
cellulare=ds.FileSystems[0] #accedi al primo filesystem presente, se l'acquisizione è un cellulare allora è il filesystem del cellulare vale per una full file system
listapp=[] #lista delle applicazioni installate del cellulare

def Installed_Uninstalled_App(): #funzione che calcola l'elenco delle applicazioni installate e disinstallate e le aggiunge al datastore (cambiala in tipo Enrich_App)
    #DA MODIFICARE UTILIZZANDO I MODELLI INSTALLEDAPPLICATION E AGGIORNANDO QUELLI PRESENTI AGGIIUNGENDO IL FATTO CHE L'APP è CANCELLATA, 
    #L'HASH DELL'APPLICAZIONE, I PERMESSI DELL'APPLICAZIONE E EVENTUALMENTE LA DATA DELL'ULTIMO AGGIORNAMENTO
    #usa ds.Models per accedere ai modelli con .GetByName
    
    localapp_db=SQLiteParser.Database.FromNode(cellulare['/data/data/com.android.vending/databases/localappstate.db']) #fai il parsing del database localappstate.db
    
    ##ins_app = CarvedString() #crea un modello CarvedString per salvare l'elenco delle applicazioni installate
    ##dis_app = CarvedString() #crea un modello CarvedString per salvare l'elenco delle applicazioni disinstallate
    
    ##ins_app.Value.Value="" #assegna il valore della stringa (visualizzato come String in UFED)
    for riga in cellulare['/data/system/packages.list'].Data.read().split('\n'): #leggi i dati in packages.list per riga
        #print(riga) 
        listapp.append(riga.split(' ')[0]) #prendi l'applicazione dalla riga e aggiungila alla lista
        ##ins_app.Value.Value=ins_app.Value.Value+(riga.split(' ')[0])+"\n" #aggiungi l'applicazione alla lista di quelle installate
        
    ##ins_app.Source.Value="App installate" #imposta l'attributo source dell'oggetto, pensa se è meglio mettere i database come /data/system/packages.list
    ##ins_app.Deleted=DeletedState.Intact #imposta il fatto che l'elemento non è stato cancellato
    
    ##dis_app.Value.Value=""
    for pacchetto in localapp_db['appstate']: #leggi i record della colonna del database localappstate, ovvero i pacchetti installati
            #print(record)
            #print(record['package_name'].Value)
        if pacchetto['package_name'].Value not in listapp: #se non è presente nella lista delle app installate
            #print(record['package_name'].Value)
            ##dis_app.Value.Value=dis_app.Value.Value+(str(record['package_name'].Value))+"\n" #aggiungi l'applicazione alla lista di quelle disinstallate
            pass 
            #QUI MODIFICA (CON DELETESTATE O SCRIVENDOLO IN ALTRO MODO) CHE LE APPLICAZIONI SONO STATE DISINSTALLATE
                
    ##dis_app.Source.Value="App disinstallate" 
    ##dis_app.Deleted=DeletedState.Intact
    
        
    ##ds.Models.Add(ins_app) #aggiungi il modello al datastore 
    ##ds.Models.Add(dis_app)

#FAI UNA FUNZIONE PER OGNI APPLICAZIONE (PENSA SE USARE LE CLASSI COME NELL'ESEMPIO FIREFOX_PARSER)


def Paypal_Parsing(): #funzione che fa il parsing dei database di paypal
    pass
    #TODO
    
def Ryanair_Parsing():
    frlocal_db=SQLiteParser.Database.FromNode(cellulare['/data/data/com.ryanair.cheapflights/databases/fr-local-db'])
    
    for stazione in frlocal_db['recent_stations']:  #Per aggiungere le ricerce effettuate
        ricerca=SearchedItem() #crea il modello elemento cercato
        ricerca.Source.Value="Ryanair"
        ricerca.Deleted=DeletedState.Intact
        ricerca.TimeStamp.Value=TimeStamp.FromUnixTime(int64_to_unixtimestamp(stazione['last_usage'].Value)) #assegna i timestamp delle ricerche
        
        ricerca.Value.Value="From station: "+stazione['origin_station_code'].Value+" to station: "+stazione['station_code'].Value
        #ricerca.Account="prova" #DA CAPIRE SE E COME SI PUò ACCEDERE AD ALCUNI ELEMENTI DEI DATABAS
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
           
        account.TimeCreated.Value=TimeStamp.FromUnixTime(int64_to_unixtimestamp(profilo['member_since'].Value)) #trasfroma da int64 a timestamp unix e poi da unix timestamp a timestamp di UFED e lo assegna alla data di crezione dell'account
        
        if IsDBNull (profilo['phone_number'].Value) == False: #se la colonna del database non è vuota, ANDREBBE FATTO OGNI VOLTA CHE SI GUARDA UNA COLONNA DI UN DATABASE ALTRIMENTI L'ASSEGNAMENTO A NULL DA ERRORE
            cel=PhoneNumber() #crea il modello cellulare
            cel.Value.Value=profilo['phone_number'].Value
            account.Entries.Add(cel) #aggiungi l'entry del numero di cellulare nel profilo

        
        account.Notes.Add("data di nascita: "+str(TimeStamp.FromUnixTime(int64_to_unixtimestamp(profilo['birth_date'].Value)))) #aggiungi alle note del profilo la data di nascita
        
        
        ds.Models.Add(account) #aggiungi l'account all'elenco dei modelli account presenti
        

def int64_to_unixtimestamp(tp):  #funzione che trasforma da int64 a unixtimestamp     
    dt=datetime.datetime.fromtimestamp(tp/1000) #trasforma da timestamp a datetime, il timestamp è in millisecondi quindi si divide per 1000, se fosse in microsecondi dividi per 1000000, in nanosecondi dividi per 1000000000
    
    unixtp=time.mktime(dt.timetuple()) #trasforma il datetime in timestamp unix con mktime, con .timetuple trasforma il datetame in una tupla di tipo time
    #print(TimeStamp.FromUnixTime(time.mktime(dt.timetuple())))
    
    ##dt=dt-datetime.datetime(1601,1,1) #calcola la differenza tra la data specificata e l'epoca FILETIME che è l'1-01-1601
    ##filetime= dt.days * 86400 * 10**7 + (dt.seconds-3600) * 10**7 + dt.microseconds * 10 #converti in intervalli da 100 nanosecondi, si ha 1 giorno=86400 secondi e 1 secondo= 10^7  100 nanosecondi, -3600 secondi perchè tolgo 1 ora al timestamp per l'UTC
    
    return unixtp

        
        
        
    
def JustEat_Parsing():
    pass
    #TODO

def main():    
    print("******NUOVA ESECUZIONE********")
    
    Installed_Uninstalled_App()
    ###parsing=FileSystem("Parsing")
    
    for app in listapp: #puoi anche fare direttamente con if any("paypal" in app for app in listapp)
        if "paypal" in app: #se è presente paypal nelle app installate
            ##parsing.Children.Add(Directory("paypal")) #aggiungi la cartella paypal al parsing
            ##parsing.Children.Add(File("prova.txt"))
            Paypal_Parsing()
        
        if "ryanair" in app:
            Ryanair_Parsing()
            
        if "justeat" in app:
            JustEat_Parsing()
            
    
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

     
'''if __name__ == '__main__': #FACENDO COSì NON VA, CI SONO ALCUNI MODI DI FARE LE COSE IN PYTHON CHE IMPORTATI IN UFED CON SCRIPT ESTERNI NON FUNZIONANO NON SO PERCHè, FORSE PERCHè POTREBBE BASARSI SU IRONPYTHON2.7(CHE IN TEORIA è SOLO LA GUI, MA NON HO ALTRE IPOTESI)
    main()'''
    
main()