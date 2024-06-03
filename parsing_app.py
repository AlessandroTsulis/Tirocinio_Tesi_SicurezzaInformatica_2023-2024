# coding=utf-8 per definire l'encoding
#script per fare il parsing dei database di applicazioni non considerate da UFED e aggiungere nuovi elementi al datastore
#importa questo script come decoding scope, ricorda che se vuoi aggiungere degli elementi al data tree d utilizzare il decoding scope (l'applicative scope serve modificare elementi già presenti) 
from physical import * #per utilizzare le API UFED in script esterni (librerie per il decoding scope)
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

def Check_Installed_App(): #funzione che calcola l'elenco delle applicazioni installate    
    localapp_db=SQLiteParser.Database.FromNode(cellulare['/data/data/com.android.vending/databases/localappstate.db']) #fai il parsing del database localappstate.db
    
    for riga in cellulare['/data/system/packages.list'].Data.read().split('\n'): #leggi i dati in packages.list per riga
        #print(riga) 
        listapp.append(riga.split(' ')[0]) #prendi l'applicazione dalla riga e aggiungila alla lista delle app installate

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
        
        ds.Models.Add(posizione)

def int64_to_unixtimestamp(tp):  #funzione che trasforma da int64 a unixtimestamp     
    dt=datetime.datetime.fromtimestamp(tp/1000) #trasforma da timestamp a datetime, il timestamp è in millisecondi quindi si divide per 1000, se fosse in microsecondi dividi per 1000000, in nanosecondi dividi per 1000000000
    
    unixtp=time.mktime(dt.timetuple()) #trasforma il datetime in timestamp unix con mktime, con .timetuple trasforma il datetame in una tupla di tipo time
    #print(TimeStamp.FromUnixTime(time.mktime(dt.timetuple())))
    
    ##dt=dt-datetime.datetime(1601,1,1) #calcola la differenza tra la data specificata e l'epoca FILETIME che è l'1-01-1601
    ##filetime= dt.days * 86400 * 10**7 + (dt.seconds-3600) * 10**7 + dt.microseconds * 10 #converti in intervalli da 100 nanosecondi, si ha 1 giorno=86400 secondi e 1 secondo= 10^7  100 nanosecondi, -3600 secondi perchè tolgo 1 ora al timestamp per l'UTC
    
    return unixtp


def main():    
    print("******NUOVA ESECUZIONE********")
    
    Check_Installed_App()
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

     
"""if __name__ == '__main__': #FACENDO COSì NON VA, CI SONO ALCUNI MODI DI FARE LE COSE IN PYTHON CHE IMPORTATI IN UFED CON SCRIPT ESTERNI NON FUNZIONANO NON SO PERCHè, FORSE PERCHè POTREBBE BASARSI SU IRONPYTHON2.7(CHE IN TEORIA è SOLO LA GUI, MA NON HO ALTRE IPOTESI)
    main()"""

main()