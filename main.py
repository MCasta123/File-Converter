from funzioni import choose_directory,choose_file, get_base_path,load_settings,modify_settings, create_menu, use_settings, to_do_after_conversion, write_cancellation_log,load_cancellation_log
from classi import GenericFile, check_homogeneity
import traceback
import tomllib
import sys
import os


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
if not os.path.exists(os.path.join(get_base_path(),'cancellation_log.json')): #se non esiste cancellation_log.json lo creo
    write_cancellation_log()
while True: #LOOP CHE FA CONTINUARE IL PROGRAMMAS
    print(f'{'='*100}')
    initial_actions={
        'Inizia a convertire' : 1,
        'Impostazioni' : 2,
        'Accedi alle conversioni sospese' : 3,
        'Esci' : 0
    }
    action_choice=create_menu(message='Scegli cosa vuoi fare', dictio=initial_actions)
    if action_choice==1:    #gestione selezione files

        files_paths=choose_file()   #permetto di scegliere uno o più file
        if files_paths:    #controllo che non sia vuota la tupla
            if check_homogeneity(files_paths):   #controllo che tutti i file siano relativi alla stessa classe
                try:
                    temp_object=GenericFile.create_from_path(files_paths[0],config=config)  #creo un oggetto temporaneo per poter accedere alle azioni disponibili
                    available_actions=temp_object.get_available_actions()
                    print('\n')
                    choice=create_menu(message='Le azioni disponibili per questo file sono: ', dictio=available_actions)
                    directory_path=''
                    extra_parameters=temp_object.add_extra_parameters(choice=choice,file_list=files_paths)
                    if 'stop' in extra_parameters:
                        if extra_parameters['stop']==True:
                            pass
                    else:
                        if len(files_paths)>1:
                            directory_path=choose_directory()
                            if directory_path=='':
                                print('\n')
                                message='Errore, non hai selezionato la cartella di destinazione'
                                check=create_menu(message=message,dictio={'Torna alla home' : 1, 'Esci' : 0})
                                if check==0:
                                    break
                                else:
                                    continue
                        converted_files=list(files_paths)
                        for x in files_paths:
                            chosen_file=GenericFile.create_from_path(x, config=config)
                            returned_path=chosen_file.choose_action(choice=choice,directory_path=directory_path,extra_parameters=extra_parameters)
                            if returned_path: #se entro nell' if vuol dire che choose_action ha restituito un path da rimouivere dalla lista dei file convertiti
                                if returned_path in converted_files:
                                    converted_files.remove(returned_path)
                    
                    behaviour_after_conversion=use_settings(category='general',option='after_conversion')
                    if not behaviour_after_conversion:
                        action_to_do_after_conversion={
                            'Converti ed elimina tutti i files precedenti' : 1,
                            'Converti e mantieni tutti i files' : 2,        #default
                            'Converti e salva i files precedenti per cancellari in seguito dopo averli controllati con un unico click' : 3
                        }
                        behaviour_after_conversion=create_menu(dictio=action_to_do_after_conversion,message='Seleziona cosa vuoi fare con i file originari dopo che sono stati convertiti')
                        print('Fatto')
                    to_do_after_conversion(behaviour=behaviour_after_conversion,files_paths=converted_files)
                except Exception as e:
                    print(f"ERRORE TECNICO: {e}")
                    traceback.print_exc()  # stampa il traceback completo
                  

                print('\n')
                message='Cosa vuoi fare?'
                if behaviour_after_conversion==3: #se l'utente ha scelto di controllare i file nuovi per poi eliminare i vecchi stampa questo menu
                    check=create_menu(message=message,dictio={'Ho controllato i files nuovi. Cancella i vecchi': 2,'Non memorizzarli, questi files sono sicuro di tenerli' : 3 ,'Torna alla home' : 1, 'Esci' : 0})
                else:   #altrimenti stampa questo
                    check=create_menu(message=message,dictio={'Torna alla home' : 1, 'Esci' : 0})
                if check==0:    #termina programma
                    break
                elif check==2:  #chiama funzione che cancella i files che avevamo memorizzato
                    load_cancellation_log()
                elif check==3: #se l'utente è sicuro di tenere quei file posso non salvarli
                    load_cancellation_log(delete_last_element=True)   #chiamo funzione con il parametro false in modo che semplicemente leva dal file json questa conversione

            else:
                print('ERRORE')
                print('I formati supportati sono: pdf, jpg, jpeg, png, heic, mov, mp4')
                print('Si ricorda inoltre che in caso di selezione di più file, i file devono essere dello stesso tipo (es: tutte immagini---->quindi jpg jpeg png)')
                print('\n')
                message='Cosa vuoi fare?'
                check=create_menu(message=message,dictio={'Torna alla home' : 1, 'Esci' : 0})
                if check==0:
                    break
        else:
            print('ERRORE')
            print('\n')
            message='Cosa vuoi fare?'
            check=create_menu(message=message,dictio={'Torna alla home' : 1, 'Esci' : 0})
            if check==0:
                break
    elif action_choice==2:
        
        possible_actions={
            'Impostazioni file pdf' : 'pdf',
            'Impostazioni immagini' : 'image',
            'Impostazioni file video' : 'video',
            'Impostazioni generali' : 'general',
            'Reset impostazioni' : 'reset',
            'Torna alla home' : ''
        }
        category=create_menu(dictio=possible_actions, message='Che tipo di impostazioni vuoi modificare')
        settings=load_settings()
        if category in settings:
            
            possible_changes=settings[category]

            possible_changes_alias={
                'pdf_compression_quality' : 'Scegli la qualità di compressione dei files pdf',
                'video_compression_quality' : 'Scegli la qualità di compressione dei video',
                'after_conversion' : 'Scegli cosa fa il convertitore dopo aver convertito i files'
            }
            selected_change=create_menu(dictio=possible_changes, message='Cosa vuoi modificare? ',return_the_keys=True, dictionary_of_alias=possible_changes_alias)
        if category=='pdf':   #impostazioni pdf

            if selected_change=='pdf_compression_quality': #qui si cambia le impostazioni relative alla compressione dei file pdf
                pdf_quality_map={
                        'Qualità alta, compressione bassa' : 1,
                        'Qualità media, compressione media' : 2,
                        'Qualità bassa, compressione bassa' : 3
                }
                quality=create_menu(dictio=pdf_quality_map,message='Scegli la qualità di compressione')
                modify_settings(category=category,selected_change={selected_change : quality})
            else:
                continue
            
        elif category=='image': #impostazioni immagini
            print('NESSUNA IMPOSTAZIONE DISPONIBILE PER LE IMMAGINI')
        
        elif category=='video': #impostazioni video
            if selected_change=='video_compression_quality': #qui si cambia le impostazioni relative alla compressione dei video
                video_quality_map={
                        'Compressione leggera' : 1,
                        'Compressione media' : 2,
                        'Compressione alta' : 3
                }
                quality=create_menu(dictio=video_quality_map, message='Scegli la qualità di compressione')
                modify_settings(category=category,selected_change={selected_change : quality})
            else:
                continue
            
        elif category=='general': #impostazioni generali
            if selected_change=='after_conversion':
                action_to_do_after_conversion={
                    'Converti ed elimina tutti i files precedenti' : 1,
                    'Converti e mantieni tutti i files' : 2,        #default
                    'Converti e salva i files precedenti per cancellari in seguito dopo averli controllati' : 3
                }
                after_conversion=create_menu(dictio=action_to_do_after_conversion,message='Seleziona cosa vuoi fare con i file originari dopo che sono stati convertiti')
                modify_settings(category=category,selected_change={selected_change : after_conversion})
            else:
                continue
        elif category=='reset': #reset impostazioni
            preference_file_path=os.path.join(get_base_path(),'preferences.toml')
            if os.path.exists(preference_file_path):
                os.remove(preference_file_path)
            load_settings()
        else:   #torna alla home
            continue
    elif action_choice==3:
        settings=load_settings()
        if settings['general']['after_conversion']!=3:
            print('Questa sezione è disponibile solo se si abilita l\'impostazione di tenere in memoria i files dopo la conversione per cancellarli in seguito')
            print('Per farlo:')
            print('Torna alla home -> Impostazioni -> generali -> Scegli cosa fa il convertitore dopo aver convertito i files -> Converti e salva i files precedenti per cancellari in seguito dopo averli controllati')
        else:
            load_cancellation_log()
    else:
        break
    