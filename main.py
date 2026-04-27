from funzioni import chose_directory,chose_file
from classi import GenericFile, check_homogeneity
import traceback


while True: #LOOP CHE FA CCONTINUARE IL PROGRAMMA
    
    files_paths=chose_file()   #permetto di scegliere uno o più file
    if files_paths:    #controllo che non sia vuota la tupla
        if check_homogeneity(files_paths):   #controllo che tutti i file siano relativi alla stessa classe
            temp_object=GenericFile.create_from_path(files_paths[0])
            temp_object.get_available_actions()
            try:
                choice=int(input())
                directory_path=''
                extra_parameters=temp_object.add_extra_parameters(choice=choice,file_list=files_paths)
                if 'stop' in extra_parameters:
                    if extra_parameters['stop']==True:
                        pass
                else:
                    if len(files_paths)>1:
                        directory_path=chose_directory()
                        if directory_path=='':
                            print('Premere INVIO per una nuova operazione')
                            check=input()
                            if check!='':
                                break
                            else:
                                continue
                    
                    for x in files_paths:
                        chosen_file=GenericFile.create_from_path(x)
                        chosen_file.choose_action(choice=choice,directory_path=directory_path,extra_parameters=extra_parameters)

            except ValueError:
                print('Inserire un numero valido')
            except Exception as e:
                print(f"ERRORE TECNICO: {e}")
                traceback.print_exc()  # stampa il traceback completo
                   
            
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