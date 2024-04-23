# coding=utf-8 per definire l'encoding
#Quando importi da script esterni ricorda di utilizzare il decoding scope (l'applicative scope da errori) 
from physical import * #per utilizzare le API UFED in script esterni
import sys
import shutil  #per copiare i file usa shutil
import SQLiteParser #libreria per il parsing di database

#FAI UNA FUNZIONE PER OGNI APPLICAZIONE

def paypal(): #funzione che fa il parsing dei database di paypal
    #TODO
    
def ryanair():
    #TODO
    


def stampa(stringa): #funzione per stampare su un file per il debugging visto che non riesco a fare il print sul trace window di UFED 
    
    with open('C:\\Users\\alessandro.tsulis\\Desktop\\UFED_acquisizione\\stampa.txt','a') as file: #file che contiene le stampe per il debugging visto che non si riesce a stampare sul trace window di UFED, con a si fa l'append invece che w+ prla scrittura, with serve per sostituire il try/except/finnaly per l'error-handling ed è più elegante e non necessita del file.close
        file.write(str(stringa)+"\n") #traformo in stringa perchè passandogli non stringe da errore
        
    #print("This is an error message.", file=sys.stderr) 
    
    '''f=open('C:\\Users\\alessandro.tsulis\\Desktop\\UFED_acquisizione\\stampa.txt','w+') #file di stampa che simula stdout, visto che non riesco a stampare sul trace window di ufed
    f.write(stringa) #trasformo in stringa cellulare che è di tipo FileSystemProxy altrimenti da errore
    #f.write(" altra scritta")
    f.close()'''
    
    
def puliscistampa(): #funzione per rendere vuoto il file di stampa
    with open('C:\\Users\\alessandro.tsulis\\Desktop\\UFED_acquisizione\\stampa.txt','w+') as file: 
        file.write("")
    

def main():
    puliscistampa() #pulisci dalle stampe precedenti il file di stampa
    
    parsing=FileSystem("Parsing")
    
    cellulare=ds.FileSystems[0] #accedi al primo filesystem presente, se l'acquisizione è un cellulare allora è il filesystem del cellulare vale per una full file system
    
    localapp=SQLiteParser.Database.FromNode(cellulare['/data/data/com.android.vending/databases/localappstate.db']) #fai il parsing del database localappstate.db
    
    '''stampa(db)
    stampa(db.DBNode)
    stampa(db.DBWalNode)
    stampa(db.Tables)'''
    
    listapp=[]
    #ins_app=open('C:\\Users\\alessandro.tsulis\\Desktop\\UFED_acquisizione\\app_installate.txt','w+')
    #dis_app=open('C:\\Users\\alessandro.tsulis\\Desktop\\UFED_acquisizione\\app_disintallate.txt','w+')
    with open ('C:\\Users\\alessandro.tsulis\\Desktop\\UFED_acquisizione\\app_installate.txt','w+') as ins_app:
        for riga in cellulare['/data/system/packages.list'].Data.read().split('\n'): #leggi i dati in packages.list per riga
        #stampa(riga) 
            ins_app.write(riga.split(' ')[0]+"\n")
            listapp.append(riga.split(' ')[0]) #prendi l'applicazione dalla riga e aggiungila alla lista
    #ins_app.close()
    
    with open('C:\\Users\\alessandro.tsulis\\Desktop\\UFED_acquisizione\\app_disintallate.txt', 'w+') as dis_app:
        for record in localapp['appstate']: #leggi i record della colonna del database appstate
            #stampa(record)
            #stampa(record['package_name'].Value)
            if record['package_name'].Value not in listapp: #se non è presente nella lista delle app installate
                dis_app.write(str(record['package_name'].Value)+"\n")
                #stampa(record['package_name'].Value)
    #dis_app.close()
    
        
    #CERCA DI CAPIRE COME CREARE DUE FILE CHE CONTENGANO I FILE app_installate e app_disinstallate(DOVRESTI MODIFICARE LA PROPRIETà .DATA DELL'OGGETTO FILE, SOTTO CI SONO DELLE PROVE COMMENTANTE)
    #FORSE UTILE https://docs.python.org/3/library/io.html PER I FILE BINARI
    
    
    '''f= File ("fileprova.txt")

    file=open ('C:\\Users\\alessandro.tsulis\\Desktop\\UFED_acquisizione\\app_installate.txt', "rb")
    
    f.Data= MemoryRange(Chunk(file,0,0))
    #f.Data= MemoryRange(Chunk(Stream(ins_app),0,0))'''
    
    for app in listapp: #puoi anche fare direttamente con if any("paypal" in app for app in listapp)
        if "paypal" in app: #se è presente paypal nelle app installate
            parsing.Children.Add(Directory("paypal")) #aggiungi la cartella paypal al parsing
            parsing.Children.Add(File("prova.txt"))
            paypal()
        
        if "ryanair" in app:
            ryanair()
 
    
       '''if "paypal" in listapp: #se è presente paypal nelle app installate
        parsing.Children.Add(Directory("paypal")) #aggiungi la cartella paypal al parsing
        parsing.Children.Add(File("prova"))'''
    
    
    ds.FileSystems.Add(parsing) #aggiungi il filesystem al datastore
    
    
    
    '''stampa(cellulare['/data/system/packages.list'])
    
    
    stampa(cellulare['/data/system/packages.list'].Data)
    
    stampa(cellulare['/data/system/packages.list'].Data.read())'''
    
    '''stampa("prova")
    stampa(cellulare)'''

   

    '''d= Directory("mydirectory3") #crea il nodo di tipo directory "mydirectory3"
    d.Children.Add(File("fileprova.txt")) #aggiungi alla directory il file fileprova.txt 
    
    cellulare.Children.Add(d) #aggiungi la directory al filesystem''' 
    

    '''fs = FileSystem("mio_filesystem_12") #crea un nuovo nodo filesystem 
    ds.FileSystems.Add (fs) #aggiungi un filestem al DataStore che comprende tutti i dati di un progetto del physical analizer, in una singola linea si fa con ds.FileSystems.Add(FileSystem("filesystem_8"))

    fs.Children.Add(Node("prova",NodeType.File)) #aggiungi un nodo al file system appena creato'''
    
    #print(cellulare, stdout=(open('C:\\Users\\alessandro.tsulis\\Desktop\\UFED_acquisizione\\stampa.txt','w+'))) #non funziona, CI SONO ALCUNI MODI DI FARE LE COSE IN PYTHON CHE IMPORTATI IN UFED NON FUNZIONANO NON SO PERCHè, FORSE PERCHè POTREBBE BASARSI SU IRONPYTHON2.7(CHE IN TEORIA è SOLO LA GUI, MA NON HO ALTRE IPOTESI)
    
    #cellulare.Children.Add(Node("directory2",NodeType.Directory)) #aggiungi una directory al filesystem

    #ds.FileSystems[0].Children.Add(Directory("mydirectory4")) #aggiungi una directory al filesystem senza usare variabili
    
    #f2=File("fileprova.txt") #crea un nodo di tipo File
    
    #ds.FileSystems[0].Children.Add(Node("nuova_directory",NodeType.Directory))

     
'''if __name__ == '__main__': #FACENDO COSì NON VA, CI SONO ALCUNI MODI DI FARE LE COSE IN PYTHON CHE IMPORTATI IN UFED CON SCRIPT ESTERNI NON FUNZIONANO NON SO PERCHè, FORSE PERCHè POTREBBE BASARSI SU IRONPYTHON2.7(CHE IN TEORIA è SOLO LA GUI, MA NON HO ALTRE IPOTESI)
    main()'''
    
main()