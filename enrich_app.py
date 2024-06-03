# coding=utf-8 per definire l'encoding(altrimenti da errore)
#script per arricchire le applicazioni e gli elementi già presenti del datastore
#ricorda di importare questo script come applicative scope perchè va a modificare gli elementi InstalledApplication già presenti del data tree (pensa anche se ha senso eliminare i parsing impropri, come le posizione di JustEat)
import physical #per utilizzare le API di UFED in script esterni in applicative scope
import PAphysical


def Enrich_App(): #funzione che calcola l'elenco delle applicazioni installate e disinstallate e ne arricchisce le informazoni (cambiala in tipo Enrich_App)
    #DA MODIFICARE UTILIZZANDO I MODELLI INSTALLEDAPPLICATION E AGGIORNANDO QUELLI PRESENTI AGGIIUNGENDO IL FATTO CHE L'APP è CANCELLATA, 
    #L'HASH DELL'APPLICAZIONE, I PERMESSI DELL'APPLICAZIONE E EVENTUALMENTE LA DATA DELL'ULTIMO AGGIORNAMENTO
    #usa ds.Models per accedere ai modelli
    
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
    
    
def main():
    print("******NUOVA ESECUZIONE********")
    
    for i in ds.Models:
        print(i)



main()