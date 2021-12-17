# -*- coding: utf-8 -*-

__auth__ = 'Chen Chen'

import sys
import numpy as np
import pandas as pd
import seaborn as sns
import statsmodels.api as sm
import matplotlib.pyplot as plt
from scipy.stats import spearmanr, ttest_1samp
from helper import *
from factor_processing import gen_factor

__PATH_FILE = os.path.dirname(__file__)
_ConfigFolder = 'Config'
_ConfigFile = 'config.json'
_InputFolder = 'Input'
_OutputFolder = 'Output'
_FigureFolder = 'Figure'
_Script = os.path.basename(__file__).rstrip('.py')
config = get_config(__PATH_FILE, _ConfigFolder, _ConfigFile)
sns.set(style='darkgrid')


def no_zero_factor(df_cross_section, transform=True, z=True, method='std'):
    target_column = df_cross_section.columns.tolist()[-1]
    df_cross_section.dropna(axis=0, inplace=True)
    df_copy = df_cross_section.copy()
    df_copy = df_copy[~df_cross_section[target_column].isin([0])]  # only select non-zero value
    df_factor_transform = gen_factor(df_copy[['symbol', 'session_end'] + [target_column]], transform=transform, z=z,
                                     method=method)

    return df_factor_transform


@func_timer
def modeling(df_exess_return, df_factor, model_type='ols', transform_method='std', save=True):
    columns_factor = df_factor.columns.tolist()
    columns_factor.remove('symbol')
    columns_factor.remove('session_end')
    columns_er = df_exess_return.columns.tolist()
    columns_er = [column for column in columns_er if 'er_' in column]
    emit_log(config, _Script,
             f"{sys._getframe().f_code.co_name}|factor columns: {columns_factor} and "
             f"excess return columns: {columns_er}.")
    results = list()
    indices = list()

    df_columns = ['er', 'session_end']
    df_tvalue = pd.DataFrame(columns=df_columns)
    df_factor_loading = pd.DataFrame(columns=df_columns)
    df_ic = pd.DataFrame(columns=df_columns)
    for column_factor in columns_factor:
        df_tvalue_tmp1 = pd.DataFrame(columns=df_columns)
        df_factor_loading_tmp1 = pd.DataFrame(columns=[column_factor, 'er', 'session_end'])
        df_ic_tmp1 = pd.DataFrame(columns=df_columns)
        for column_er in columns_er:
            sample_count_list = list()
            factor_loading_list = list()
            t_value_list = list()
            ic_list = list()
            dates = list()
            df_tvalue_tmp2 = pd.DataFrame(columns=df_columns)
            df_factor_loading_tmp2 = pd.DataFrame(columns=[column_factor, 'er', 'session_end'])
            df_ic_tmp2 = pd.DataFrame(columns=df_columns)
            for date, df_er_cross_section in df_exess_return.groupby('session_date'):
                # if date > '20190601' or date < '20190303':
                #     continue
                emit_log(config, _Script, '~'*20)
                emit_log(config, _Script, f"start processing {model_type}, {column_factor}, {column_er}, {date}...")
                df_er_cross_section.set_index('symbol', inplace=True)

                df_factor_cross_section = df_factor[df_factor['session_end'] == date][
                    ['symbol', 'session_end'] + [column_factor]]
                if df_factor_cross_section[column_factor].isnull().all():
                    continue
                df_factor_cross_section_transform = no_zero_factor(df_factor_cross_section, method=transform_method)
                df_factor_cross_section_transform.set_index('symbol', inplace=True)
                df_cross_section_transform = df_factor_cross_section_transform.join(df_er_cross_section)
                df_cross_section = df_cross_section_transform[
                    [f'{column_factor}_Trans', column_er, column_er.replace('er', 'total_mv')]]
                df_cross_section = df_cross_section.dropna(axis=0, how='any')

                # column_factor has changes after transform
                column_factor_trans = f'{column_factor}_Trans'
                cross_section_x = df_cross_section[column_factor_trans]
                cross_section_y = df_cross_section[column_er]
                cross_section_w = df_cross_section[column_er.replace('er', 'total_mv')]
                # not_nan = ~np.isnan(cross_section_y) & ~np.isnan(cross_section_x)
                sample_count = len(df_cross_section)
                if sample_count == 0:
                    emit_log(config, _Script, f"0 sample in this cross section...")
                    continue

                sample_count_list.append(sample_count)
                emit_log(config, _Script, f"{sample_count} sample(s) in this cross section...")
                dates.append(date)
                ic_cross_section = spearmanr(cross_section_x, cross_section_y)
                emit_log(config, _Script, f"ic: {ic_cross_section}")
                ic_list.append(ic_cross_section[0])
                result = linear_regression_models(cross_section_x, cross_section_y, cross_section_w, model_type)
                # plot figure of a cross section
                visualize_data(date, df_cross_section, column_factor_trans, column_er, model_type, result.params,
                               rgm=True, save=save)
                factor_loading_list.append(result.params[column_factor_trans])
                t_value_list.append(result.tvalues[column_factor_trans])
                emit_log(config, _Script,
                         f"factor_loading: {result.params[column_factor_trans]}, "
                         f"t_value: {result.tvalues[column_factor_trans]}")
            
            t_value_mean = np.nanmean(t_value_list)
            factor_loading_mean = np.nanmean(factor_loading_list)
            factor_loading_std = np.nanstd(factor_loading_list)
            ic_mean = np.nanmean(ic_list)
            ic_std = np.nanstd(ic_list)
            sample_count_mean = np.nanmean(sample_count_list)
            sample_count_median = np.nanmedian(sample_count_list)

            t_gt2 = np.sum(list(map(lambda x: x >= 2, t_value_list)))/len(t_value_list)
            factor_loading_tvalue = ttest_1samp(factor_loading_list, 0)[0]
            ic_gt002 = np.sum(list(map(lambda x: abs(x) >= 0.02, ic_list)))/len(ic_list)
            ic_tvalue = ttest_1samp(t_value_list, 0)[0]
            data = [t_value_mean, t_gt2, factor_loading_mean, factor_loading_std, factor_loading_tvalue,
                    ic_mean, ic_std, ic_gt002, ic_tvalue, sample_count_mean, sample_count_median]
            results.append(data)
            index = f"{column_er}/{column_factor}"
            indices.append(index)
            emit_log(config, _Script, f"{index}: {data}")

            # ------------------------------- output results -------------------------------
            df_factor_loading_tmp2[column_factor] = factor_loading_list
            df_factor_loading_tmp2.er = column_er
            df_factor_loading_tmp2.session_end = dates

            df_tvalue_tmp2[column_factor] = t_value_list
            df_tvalue_tmp2.er = column_er
            df_tvalue_tmp2.session_end = dates

            df_ic_tmp2[column_factor] = ic_list
            df_ic_tmp2.er = column_er
            df_ic_tmp2.session_end = dates

            df_factor_loading_tmp1 = pd.concat([df_factor_loading_tmp1, df_factor_loading_tmp2])
            df_tvalue_tmp1 = pd.concat([df_tvalue_tmp1, df_tvalue_tmp2])
            df_ic_tmp1 = pd.concat([df_ic_tmp1, df_ic_tmp2])

        df_factor_loading = pd.merge(df_factor_loading, df_factor_loading_tmp1, how='outer', on=['session_end', 'er'])
        df_tvalue = pd.merge(df_tvalue, df_tvalue_tmp1, how='outer', on=['session_end', 'er'])
        df_ic = pd.merge(df_ic, df_ic_tmp1, how='outer', on=['session_end', 'er'])

    df_factor_loading[df_columns + columns_factor].to_csv(
        os.path.join(__PATH_FILE, _OutputFolder, f"factor_loading_{model_type}_{transform_method}.csv"), index=False)
    df_tvalue[df_columns + columns_factor].to_csv(
        os.path.join(__PATH_FILE, _OutputFolder, f"tvalue_{model_type}_{transform_method}.csv"), index=False)
    df_ic[df_columns + columns_factor].to_csv(
        os.path.join(__PATH_FILE, _OutputFolder, f"ic_{model_type}_{transform_method}.csv"), index=False)

    columns = ['t_value_mean', 't_gt2', 'factor_loading_mean', 'factor_loading_std', 'factor_loading_tvalue',
               'ic_mean', 'ic_std', 'ic_gt002', 'ic_tvalue', 'sample_count_mean', 'sample_count_median']
    df_results = pd.DataFrame(results, index=indices, columns=columns)
    df_results.index.name = 'er_over_factor'
    emit_log(config, _Script, f"modeling finished for {model_type}.")

    return df_results


@func_timer
def linear_regression_models(cross_section_x, cross_section_y, cross_section_w, model_type):
    if model_type.lower() == 'ols':
        result = sm.OLS(cross_section_y, sm.add_constant(cross_section_x)).fit()
        print(result.params)
    elif model_type.lower() == 'wls':
        result = sm.WLS(cross_section_y, sm.add_constant(cross_section_x),
                        weights=cross_section_w).fit()
    elif model_type.lower() == 'rlm':
        result = sm.RLM(cross_section_y, sm.add_constant(cross_section_x), M=sm.robust.norms.HuberT()).fit()
    else:
        emit_log(config, _Script, 'Only support ols, wls, rlm linear models at this moment.')
        raise ValueError('Linear model type error.')

    return result


# TODO this part need to modify, since code structure has changed
def single_cross_section_test(date, df_factor, column_factor, df_er, column_er, model_type, transform_method,
                              save=True):
    df_er_cross_section = df_er[df_er['session_date'] == date]
    df_er_cross_section.set_index('symbol', inplace=True)
    df_factor_cross_section = df_factor[df_factor['session_end'] == date]
    df_factor_cross_section.set_index('symbol', inplace=True)
    df_cross_section = df_factor_cross_section.join(df_er_cross_section)
    df_cross_section = df_cross_section[[column_factor, column_er, column_er.replace('er', 'total_mv')]]
    df_cross_section.dropna(axis=0, how='any', inplace=True)
    cross_section_x = df_cross_section[column_factor]
    cross_section_y = df_cross_section[column_er]
    cross_section_w = df_cross_section[column_er.replace('er', 'total_mv')]
    emit_log(config, _Script, f"length of sample: {len(df_cross_section)}")
    if len(df_cross_section) == 0:
        return
    result = linear_regression_models(cross_section_x, cross_section_y, cross_section_w,
                                      model_type=model_type)
    print(result.params[column_factor])
    print(result.tvalues[column_factor])
    params = result.params

    visualize_data(date, df_cross_section, column_factor, column_er, model_type, params, rgm=True, save=save)
    plt.show()


def visualize_data(date, df_cross_section, column_factor, column_er, model_type, params, rgm=True, save=True):
    ax = sns.scatterplot(x=column_factor, y=column_er, size=column_er.replace('er', 'total_mv'), data=df_cross_section)
    fig = ax.get_figure()
    plt.xlim([-1, 3])
    # fig = sns.relplot(x=column_factor, y=column_er, data=df_cross_section, kind='scatter')
    if rgm and len(params) > 1:
        visualize_rgm(df_cross_section, column_factor, params)
    if save:
        create_figure_folder(__PATH_FILE, _FigureFolder)
        fig.savefig(
            os.path.join(__PATH_FILE, _FigureFolder, f"{model_type}@{column_er}^{column_factor}@{date}@{_Script}.png"))
        plt.close()


def visualize_rgm(df_cross_section, column_factor, params):
    x = np.linspace(df_cross_section[column_factor].min(), df_cross_section[column_factor].max(), 50)
    y = params[0] + x*params[1]
    plt.plot(x, y, c='r')


def main():
    emit_log(config, _Script, f"Program starts...")
    # read factor data
    df_factor = pd.read_csv(os.path.join(__PATH_FILE, _OutputFolder, 'factor.csv'),
                            dtype={'symbol': str, 'session_end': str})
    # read excess return
    df_er = pd.read_csv(os.path.join(__PATH_FILE, _OutputFolder, 'excess_return.csv'),
                        dtype={'symbol': str, 'session_date': str})
    # start modeling
    # model_type_list = ['OLS', 'WLS', 'RLM']
    model_type_list = ['RLM']
    transform_method = 'std'
    for model_type in model_type_list:
        df = modeling(df_er, df_factor, model_type=model_type, transform_method=transform_method, save=True)
        df.to_csv(os.path.join(__PATH_FILE, _OutputFolder, f"model_results_{model_type}_{transform_method}.csv"))

    # single_cross_section_test('20200529', df_factor, 'PAT_M', df_er, 'er_1m', model_type='OLS', transform_method='std',
    #                           save=False)

    emit_log(config, _Script, f"All finished")


if __name__ == '__main__':
    main()

