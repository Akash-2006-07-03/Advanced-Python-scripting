import os
import shutil
import json
import sys
from subprocess import PIPE, run

GAME_DIR = "game"
GAME_CODE_EXTENSION = ".go"
GAME_COMPILE_COMMAND = ["go", "build"]

def get_all_gamesdir(source_path):
    game_path = []
    for root, dirs, files in os.walk(source_path):
        for directory in dirs:
            if GAME_DIR in directory.lower():
                path = os.path.join(source_path,directory)
                game_path.append(path)
        break

    return game_path

def get_new_dir_names(game_paths,to_strip):
    new_game_path = []
    for path in game_paths:
        _, dir_name = os.path.split(path)
        new_path = dir_name.replace(to_strip,"")
        new_game_path.append(new_path)
    
    return new_game_path

def create_target_dir(target):
    if not os.path.exists(target):
        os.mkdir(target)

def copy_and_overwrite(source,dest):
    if os.path.exists(dest):
        shutil.rmtree(dest)
    shutil.copytree(source,dest)

def make_json_metadata_file(path,game_dirs):
    data = {
        "gamenames" : game_dirs,
        "no_of_games" : len(game_dirs)
    }

    with open(path, 'w') as f:
        json.dump(data,f)

def compile_game_code(path):
    code_file_name = None
    for root,dirs,files in os.walk(path):
        for file in files:
            if file.endswith(GAME_CODE_EXTENSION):
                code_file_name = file
            
            break
        break

    if code_file_name is None:
        return
    
    command = GAME_COMPILE_COMMAND + [code_file_name]
    run_code(command, path)

def run_code(command, path):
    cwd = os.getcwd()
    os.chdir(path)

    result = run(command, stdout=PIPE, stdin=PIPE, universal_newlines=True)
    print("complete result",result)

    os.chdir(cwd)

def main(source,target):
    cwd = os.getcwd()
    source_path = os.path.join(cwd,source)
    target_path = os.path.join(cwd,target)

    game_paths = get_all_gamesdir(source_path)
    new_game_paths = get_new_dir_names(game_paths,"_game")
    
    create_target_dir(target_path)

    for scr, dest in zip(game_paths,new_game_paths):
        dest_path = os.path.join(target_path,dest)
        copy_and_overwrite(scr,dest_path)
        compile_game_code(dest_path)

    json_path = os.path.join(target_path,'metadata.json')
    make_json_metadata_file(json_path,new_game_paths)
    




if __name__ == "__main__":
    args = sys.argv
    if len(args) != 3:
        raise Exception("Args must contain source and target only!")
    source, target = args[1:]
    
    main(source,target)

