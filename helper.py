# -*- coding: utf-8 -*-

__auth__ = 'Chen Chen'

import os
import time
import json
import datetime

__PATH_FILE = os.path.dirname(__file__)
_InputFolder = 'Input'
_OutputFolder = 'Output'
_ConfigFolder = 'Config'
_ConfigFile = 'config.json'


def func_timer(func):
    def func_wrapper(*args, **kwargs):
        time_start = time.clock()
        result = func(*args, **kwargs)
        time_end = time.clock()
        time_taken = time_end - time_start
        print(f'{func.__name__} running time: {round(time_taken, 2)} s')
        return result

    return func_wrapper


def get_config(path_file, config_folder, config_file):
    path_config = os.path.join(path_file, config_folder, config_file)
    print('_' * 50)
    print('Read Config File ...')
    with open(path_config) as f:
        config_json = json.loads(f.read())
        for k, v in config_json.items():
            log = f'{k}:{v}'
            print(log)

    return config_json


def create_output_folder(path_file, output_folder, *args):
    path_folder_output = os.path.join(path_file, output_folder, *args)
    if not os.path.exists(path_folder_output):
        print('Output folder is created.')
        os.makedirs(path_folder_output)
    else:
        print('Output folder exists.')


def save_dataframe(df, file_name):
    # create output folder
    create_output_folder(__PATH_FILE, _OutputFolder)
    # save dataframe to target files
    df.to_csv(os.path.join(__PATH_FILE, 'Output', file_name), encoding="utf_8_sig", index=False)


def create_figure_folder(path_file, figure_folder):
    path_folder_figure = os.path.join(path_file, figure_folder)
    if not os.path.exists(path_folder_figure):
        print('Figure folder is created.')
        os.makedirs(path_folder_figure)
    else:
        print('Figure folder exists.')


def gen_timestamp():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def create_log(config, file):
    today = datetime.datetime.today().strftime('%Y%m%d')
    # create log folder
    _PATH_LOG_FOLDER = os.path.join(__PATH_FILE, config['log'])
    if not os.path.exists(_PATH_LOG_FOLDER):
        os.mkdir(_PATH_LOG_FOLDER)
    _PATH_LOG_FILE = os.path.join(_PATH_LOG_FOLDER, f'Log@{file}@{today}.txt')
    if not os.path.exists(_PATH_LOG_FILE):
        with open(_PATH_LOG_FILE, 'w+') as f:
            f.write(f"Log started. @{gen_timestamp()} \n")
    return _PATH_LOG_FILE


def emit_log(config, file, log, path_default=True, print_log=True):
    if path_default:
        _PATH_LOG_FILE = create_log(config, file)
        with open(_PATH_LOG_FILE, 'a+', encoding='utf-8') as f:
            f.write(f"{log} |#{gen_timestamp()}#| \n")
    if print_log:
        print(log)
    # else:
    #     folder, file = os.path.split(path)
    #     if not os.path.exists(folder):
    #         os.makedirs(folder)
    #     if not os.path.exists(path):
    #         with open(path, 'w+') as f:
    #             f.write(f"Log started. @{gen_timestamp()} \n")
    #             f.write(f"{log} @{gen_timestamp()} \n")
    #     else:
    #         with open(path, 'a+') as f:
    #             f.write(f"{log} @{gen_timestamp()} \n")



