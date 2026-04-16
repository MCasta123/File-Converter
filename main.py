from funzioni import *
from classi import *


while True: #LOOP CHE FA CCONTINUARE IL PROGRAMMA
    
    percorsiFile=scegliFile()   #permetto di scegliere uno o più file
    if percorsiFile:    #controllo che non sia vuota la tupla
        if controlloOmegeneitaFile(percorsiFile):   #controllo che tutti i file siano relativi alla stessa classe
            oggettoProva=fileGenerico.creaDaPercorso(percorsiFile[0])
            oggettoProva.getAzioniDisponibili()
            try:
                scelta=int(input())
                percorsoCartella=''
                parametriExtra=oggettoProva.aggiungiParametriExtra(scelta=scelta,listaFile=percorsiFile)
                if 'stop' in parametriExtra:
                    if parametriExtra['stop']==True:
                        pass
                else:
                    if len(percorsiFile)>1:
                        percorsoCartella=scegliCartella()
                        if percorsoCartella=='':
                            print('Premere INVIO per una nuova operazione')
                            check=input()
                            if check!='':
                                break
                            else:
                                continue
                    
                    for x in percorsiFile:
                        fileScelto=fileGenerico.creaDaPercorso(x)
                        fileScelto.scegliAzione(scelta=scelta,percorsoCartella=percorsoCartella,extraParam=parametriExtra)

            except ValueError:
                print('Inserire un numero valido')
            except Exception as e:
                print(f"ERRORE TECNICO: {e}")
                   
            
            print('Premere INVIO per una nuova operazione')
            check=input()
            if check!='':
                break

        else:
            print('ERRORE')
            print('I formati supportati sono: pdf, jpg, jpeg, png, mov, mp4')
            print('Si ricorda inoltre che in caso di selezione di più file, i file devono essere dello stesso tipo (es: tutte immagini---->quindi jpg jpeg png)')
            print('Premere INVIO per riprovare')
            check=input()
            if check!='':
                break
    else:
        print('ERRORE')
        print('Per riprovare premere INVIO')
        retry=input()
        if retry!='':
            break
    #############################################################