# -*- coding: utf-8 -*-

__auth__ = 'Chen Chen'

import sys
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from helper import *


__PATH_FILE = os.path.dirname(__file__)
_ConfigFolder = 'Config'
_ConfigFile = 'config.json'
_InputFolder = 'Input'
_OutputFolder = 'Output'
_FigureFolder = 'Figure'
_Script = os.path.basename(__file__).rstrip('.py')
config = get_config(__PATH_FILE, _ConfigFolder, _ConfigFile)
sns.set(style='darkgrid')


def analyze_fix_er(target):
    file = f'{target}_RLM_std.csv'
    emit_log(config, _Script, f"analyze {file} by fixing er...")

    file_path = os.path.join(__PATH_FILE, _OutputFolder, file)
    df_file = pd.read_csv(file_path, dtype={'session_end': str})
    df_file['session_end'] = pd.to_datetime(df_file['session_end'], format='%Y-%m-%d')
    columns = df_file.columns.tolist()
    columns_pat = [column for column in columns if 'PAT' in column]
    columns_eff = [column for column in columns if 'EFF' in column]
    for er, grouped in df_file.groupby('er'):
        grouped.drop(['er'], axis=1, inplace=True)
        grouped.set_index('session_end', inplace=True)
        grouped_pat = grouped[columns_pat]
        grouped_eff = grouped[columns_eff]
        _, axes = plt.subplots(2, 2, figsize=(16, 16), sharex='col')  # _是创建的figure
        # PAT part
        grouped_pat.plot(ax=axes[0, 0], figsize=(12, 6))
        axes[0][0].set_xlabel('Date')
        axes[0][0].set_ylabel(f'{target}'.capitalize())
        # axes[0][0].set_xticks([])
        grouped_pat_mean = grouped_pat.mean().tolist()
        grouped_pat_err = grouped_pat.std().tolist()
        axes[0][1].bar([column.strip('_PAT') for column in columns_pat], grouped_pat_mean, width=0.5,
                       yerr=grouped_pat_err, label='PAT')
        # 给条形图添加数据标注
        for x, y in enumerate(grouped_pat_mean):
            axes[0][1].text(x, y, f'{round(y, 2)}')
        axes[0][1].legend()
        axes[0][1].set_xlabel('Period')
        axes[0][1].set_ylabel(f'{target} mean'.capitalize())

        # EFF part
        grouped_eff.plot(ax=axes[1, 0], figsize=(12, 6))
        axes[1][0].set_xlabel('Date')
        axes[1][0].set_ylabel(f'{target}'.capitalize())
        grouped_eff_mean = grouped_eff.mean().tolist()
        grouped_eff_err = grouped_eff.std().tolist()
        axes[1][1].bar([column.strip('_EFF') for column in columns_eff], grouped_eff_mean, width=0.5,
                       yerr=grouped_eff_err, label='EFF')
        # 给条形图添加数据标注
        for x, y in enumerate(grouped_eff_mean):
            axes[1][1].text(x, y, f'{round(y, 2)}')
        axes[1][1].legend()
        axes[1][1].set_xlabel('Period')
        axes[1][1].set_ylabel(f'{target} mean'.capitalize())
        _.suptitle(f'{er.upper()}')
        # plt.show()
        plt.savefig(os.path.join(__PATH_FILE, _OutputFolder, f"{file.strip('.csv')}_{er}.png"))
        plt.close()


def analyze_fix_period(target):
    file = f'{target}_RLM_std.csv'
    emit_log(config, _Script, f"analyze {file} by fixing period...")

    file_path = os.path.join(__PATH_FILE, _OutputFolder, file)
    df_file = pd.read_csv(file_path, dtype={'session_end': str})
    df_file['session_end'] = pd.to_datetime(df_file['session_end'], format='%Y-%m-%d')
    columns = df_file.columns.tolist()
    columns_pat = [column for column in columns if 'PAT' in column]
    columns_eff = [column for column in columns if 'EFF' in column]
    for i in range(len(columns_pat)):
        column_pat = columns_pat[i]
        df_pat = df_file[['er', 'session_end', column_pat]]
        df_pivot_pat = pivot(df_pat)
        column_eff = columns_eff[i]
        df_eff = df_file[['er', 'session_end', column_eff]]
        df_pivot_eff = pivot(df_eff)

        _, axes = plt.subplots(2, 2, figsize=(16, 16), sharex='col')  # _是创建的figure
        df_pivot_pat.plot(ax=axes[0, 0], figsize=(12, 6))
        axes[0][0].set_xlabel('Date')
        axes[0][0].set_ylabel(f'{target}'.capitalize())
        # axes[0][0].set_xticks([])
        df_pivot_pat_mean = df_pivot_pat.mean().tolist()
        df_pivot_pat_err = df_pivot_pat.std().tolist()
        axes[0][1].bar(df_pivot_pat.columns, df_pivot_pat_mean, width=0.5,
                       yerr=df_pivot_pat_err, label=column_pat)
        # 给条形图添加数据标注
        for x, y in enumerate(df_pivot_pat_mean):
            axes[0][1].text(x,  y, f'{round(y, 2)}')
        axes[0][1].legend()
        axes[0][1].set_xlabel('Period')
        axes[0][1].set_ylabel(f'{target} mean'.capitalize())

        df_pivot_eff.plot(ax=axes[1, 0], figsize=(12, 6))
        axes[1][0].set_xlabel('Date')
        axes[1][0].set_ylabel(f'{target}'.capitalize())
        # axes[0][0].set_xticks([])
        df_pivot_eff_mean = df_pivot_eff.mean().tolist()
        df_pivot_eff_err = df_pivot_eff.std().tolist()
        axes[1][1].bar(df_pivot_eff.columns, df_pivot_eff_mean, width=0.5, yerr=df_pivot_eff_err, label=column_eff)
        # 给条形图添加数据标注
        for x, y in enumerate(df_pivot_eff_mean):
            axes[1][1].text(x, y, f'{round(y, 2)}')
        axes[1][1].legend()
        axes[1][1].set_xlabel('Period')
        axes[1][1].set_ylabel(f'{target} mean'.capitalize())

        _.suptitle(f"{column_pat.split('_')[-1].upper()}")
        # plt.show()
        plt.savefig(os.path.join(__PATH_FILE, _OutputFolder, f"{file.strip('.csv')}_{column_pat.split('_')[-1]}.png"))
        plt.close()


def pivot(df):
    df_pivot = df.pivot_table(df, index='session_end', columns='er')
    df_pivot.columns = [c[-1] for c in df_pivot.columns]

    return df_pivot


if __name__ == '__main__':
    targets = ['factor_loading', 'tvalue', 'ic']
    for target in targets:
        analyze_fix_er(target)
        analyze_fix_period(target)
