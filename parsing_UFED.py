# coding=utf-8 per definire l'encoding
#Quando importi da script esterni ricorda di utilizzare il decoding scope (l'applicative scope da errori) 
from physical import * #per utilizzare le API UFED in script esterni
import sys
import shutil  #per copiare i file usa shutil
import SQLiteParser #libreria per il parsing di database

#FAI UNA FUNZIONE PER OGNI APPLICAZIONE

def paypal(): #funzione che fa il parsing dei database di paypal
    pass
    #TODO
    
def ryanair():
    pass
    #TODO
    

def main():    
    print("******NUOVA ESECUZIONE********")
    
    parsing=FileSystem("Parsing")
    
    cellulare=ds.FileSystems[0] #accedi al primo filesystem presente, se l'acquisizione è un cellulare allora è il filesystem del cellulare vale per una full file system
    
    localapp=SQLiteParser.Database.FromNode(cellulare['/data/data/com.android.vending/databases/localappstate.db']) #fai il parsing del database localappstate.db
    
    listapp=[]
    ins_app = CarvedString() #crea un modello CarvedString per salvare l'elenco delle applicazioni installate
    dis_app = CarvedString() #crea un modello CarvedString per salvare l'elenco delle applicazioni disinstallate
    
    ins_app.Value.Value="" #assegna il valore della stringa (visualizzato come String in UFED)
    for riga in cellulare['/data/system/packages.list'].Data.read().split('\n'): #leggi i dati in packages.list per riga
        #print(riga) 
        listapp.append(riga.split(' ')[0]) #prendi l'applicazione dalla riga e aggiungila alla lista
        ins_app.Value.Value=ins_app.Value.Value+(riga.split(' ')[0])+"\n" #aggiungi l'applicazione alla lista di quelle installate
        
    ins_app.Source.Value="App installate" #imposta l'attributo source dell'oggetto, pensa se è meglio mettere i database come /data/system/packages.list
    ins_app.Deleted=DeletedState.Intact #imposta il fatto che l'elemento non è stato cancellato
    
    dis_app.Value.Value=""
    for record in localapp['appstate']: #leggi i record della colonna del database appstate
            #print(record)
            #print(record['package_name'].Value)
        if record['package_name'].Value not in listapp: #se non è presente nella lista delle app installate
            #print(record['package_name'].Value)
            dis_app.Value.Value=dis_app.Value.Value+(str(record['package_name'].Value))+"\n" #aggiungi l'applicazione alla lista di quelle disinstallate
            
                
    dis_app.Source.Value="App disinstallate" 
    dis_app.Deleted=DeletedState.Intact
    
    for app in listapp: #puoi anche fare direttamente con if any("paypal" in app for app in listapp)
        if "paypal" in app: #se è presente paypal nelle app installate
            parsing.Children.Add(Directory("paypal")) #aggiungi la cartella paypal al parsing
            parsing.Children.Add(File("prova.txt"))
            paypal()
        
        if "ryanair" in app:
            ryanair()
    
    ds.FileSystems.Add(parsing) #aggiungi il filesystem al datastore
    
    ds.Models.Add(ins_app) #aggiungi il modello al datastore 
    ds.Models.Add(dis_app)
    

    #DA QUI PEZZI DI CODICE CHE POSSONO ESSERE EVENTUALMENTE UTILI(PENSA SE CANCELLARLI)
    
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