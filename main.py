from funzioni import chose_directory,choose_file, get_base_path,load_settings,modify_settings
from classi import GenericFile, check_homogeneity
import traceback
import tomllib
import sys
import os
import questionary
from questionary import Choice

try:
    config_path=os.path.join(get_base_path(),'config.toml') #ricavo il percorso del file config.toml
    with open(config_path, 'rb') as f:
        config = tomllib.load(f)
except FileNotFoundError:
    print('Errore: file config.toml non trovato.')
    sys.exit(1)
except tomllib.TOMLDecodeError as e:
    print(f'Errore: config.toml non è valido: {e}')
    sys.exit(1)
if not os.path.exists(os.path.join(get_base_path(),'preferences.toml')): #se è il primo avvio, crea preferences.toml
    load_settings()
while True: #LOOP CHE FA CONTINUARE IL PROGRAMMAS
    print(f'{'='*100}')
    action_choice=questionary.select('Scegli cosa vuoi fare',
                       choices=[Choice(title='Inizia a Convertire',value=1),Choice(title='Impostazioni',value=2),Choice(title='Esci',value=0)]).ask()
    if action_choice==1:    #gestione selezione files

        files_paths=choose_file()   #permetto di scegliere uno o più file
        if files_paths:    #controllo che non sia vuota la tupla
            if check_homogeneity(files_paths):   #controllo che tutti i file siano relativi alla stessa classe
                try:
                    temp_object=GenericFile.create_from_path(files_paths[0],config=config)  #creo un oggetto temporaneo per poter accedere alle azioni disponibili
                    available_actions=temp_object.get_available_actions()
                    print('\n')
                    choice=questionary.select('Le azioni disponibili per questo file sono:', choices=available_actions).ask()
                    directory_path=''
                    extra_parameters=temp_object.add_extra_parameters(choice=choice,file_list=files_paths)
                    if 'stop' in extra_parameters:
                        if extra_parameters['stop']==True:
                            pass
                    else:
                        if len(files_paths)>1:
                            directory_path=chose_directory()
                            if directory_path=='':
                                print('\n')
                                check=questionary.select('Errore, non hai selezionato la cartella di destinazione',
                                                         choices=[Choice(title='Torna alla home',value=1),Choice(title='Esci',value=0)]).ask()
                                if check==0:
                                    break
                                else:
                                    continue
                        
                        for x in files_paths:
                            chosen_file=GenericFile.create_from_path(x, config=config)
                            chosen_file.choose_action(choice=choice,directory_path=directory_path,extra_parameters=extra_parameters)

                except Exception as e:
                    print(f"ERRORE TECNICO: {e}")
                    traceback.print_exc()  # stampa il traceback completo
                    
                
                print('\n')
                check=questionary.select('Cosa vuoi fare?',
                                                         choices=[Choice(title='Torna alla home',value=1),Choice(title='Esci',value=0)]).ask()
                if check==0:
                    break

            else:
                print('ERRORE')
                print('I formati supportati sono: pdf, jpg, jpeg, png, heic, mov, mp4')
                print('Si ricorda inoltre che in caso di selezione di più file, i file devono essere dello stesso tipo (es: tutte immagini---->quindi jpg jpeg png)')
                print('\n')
                check=questionary.select('Cosa vuoi fare?',
                                        choices=[Choice(title='Torna alla home',value=1),Choice(title='Esci',value=0)]).ask()
                if check==0:
                    break
        else:
            print('ERRORE')
            print('\n')
            check=questionary.select('Cosa vuoi fare?',
                                    choices=[Choice(title='Torna alla home',value=1),Choice(title='Esci',value=0)]).ask()
            if check==0:
                break
    elif action_choice==2:
        possible_actions={
            'Impostazioni file pdf' : 'pdf',
            'Impostazioni immagini' : 'image',
            'Impostazioni file video' : 'video',
            'Impostazioni generali' : 'general',
            'Torna alla home' : ''
        }
        list_of_actions=[]
        for action in possible_actions:
            list_of_actions.append(action)
        available_actions=[]
        for el in list_of_actions:
            available_actions.append(Choice(title=el,value=possible_actions[el]))
        category=questionary.select('Che tipo di impostazione vuoi modificare',choices=available_actions).ask()
        settings=load_settings()
        if category in settings:
            possible_changes=settings[category]
            changes=[]
            for change in possible_changes:
                changes.append(Choice(title=change, value=change))
            changes.append(Choice(title='Torna alla home',value=''))
            print('\n')
            selected_change=questionary.select('Cosa vuoi modificare? ', choices=changes).ask()
        
        if category=='pdf':   #impostazioni pdf

            if selected_change=='pdf_compression_quality': #qui si cambia le impostazioni relative alla compressione dei file pdf
                quality_map={
                        'Qualità alta, compressione bassa' : 1,
                        'Qualità media, compressione media' : 2,
                        'Qualità bassa, compressione bassa' : 3
                }
                available_quality=[]
                for el in quality_map:
                    available_quality.append(Choice(title=el,value=quality_map[el]))
                print('\n')
                quality=questionary.select('Scegli la qualità di compressione',choices=available_quality).ask()
                modify_settings(category=category,selected_change={selected_change : quality})
            else:
                continue
            
        elif category=='image': #impostazioni immagini
            print('NESSUNA IMPOSTAZIONE DISPONIBILE PER LE IMMAGINI')
        
        elif category=='video': #impostazioni video
            if selected_change=='video_compression_quality': #qui si cambia le impostazioni relative alla compressione dei video
                quality_map={
                        'Compressione leggera' : 1,
                        'Compressione media' : 2,
                        'Compressione alta' : 3
                }
                available_quality=[]
                for el in quality_map:
                    available_quality.append(Choice(title=el,value=quality_map[el]))
                print('\n')
                quality=questionary.select('Scegli la qualità di compressione',choices=available_quality).ask()
                modify_settings(category=category,selected_change={selected_change : quality})
            else:
                continue
            
        elif category=='general': #impostazioni generali
            pass
        
        else:   #torna alla home
            continue
    
    else:
        break
    