# -*- coding: utf-8 -*-
from gpLearn.HMM.HMM_function import *

import numpy as np
from matplotlib import cm, pyplot as plt
from get_data.get_stock_hq import stock_price, index_stocks
import seaborn as sns
import pandas as pd
from backtest_func import yearsharpRatio, maxRetrace, annROR
from jqdatasdk import *
from configDB import *
auth(JOINQUANT_USER, JOINQUANT_PW)
import warnings

warnings.filterwarnings("ignore")


if __name__ == '__main__':
    data_path = 'C:/e/data/stock_hq/'
    resualt_path = 'c:/e/hmm/resualt/stockindex/'
    future_period = 1

    max_states = 6
    asset = '600519.XSHG'
    factor_lst = ['alpha000']
    s_data_date = '2010-01-01'
    e_data_date = '2020-12-01'
    all_feature_lst = PowerSetsRecursive(factor_lst)
    all_feature_lst = [i for i in all_feature_lst if len(i) >= 1]
    # all_feature_lst = [['price_deviation']]
    # # 三大股指
    ### 样本外不同滚动窗口回测，参数敏感性测试

    s_date = '2012-01-01'
    train_s_date = '2010-01-01'
    date_lst = [('2012-01-01', '2013-01-01'), ('2013-01-01', '2014-01-01'), ('2014-01-01', '2015-01-01'),
                ('2015-01-01', '2016-01-01'), ('2016-01-01', '2017-01-01'), ('2017-01-01', '2018-01-01'),
                ('2018-01-01', '2019-01-01'), ('2019-01-01', '2020-01-01'), ('2020-01-01', '2021-01-01'), ]

    # all_feature_lst = [['price_deviation']]
    train_days_lst = [i for i in range(480, 30, -40)]
    test_days_lst = [i for i in range(20, 250, 20)]
    period_param_state = []
    asset_lst = ['000300.XSHG', '000016.XSHG', '000905.XSHG', '399006.XSHE']
    for asset in asset_lst:
        data_ori = pd.read_csv(data_path + asset + '_' + 'daily.csv')
        for feature_lst in all_feature_lst:
            for train_days in train_days_lst:
                for test_days in test_days_lst:
                    try:
                        dataFactory = DataFactory(asset, factor_lst, future_period, s_data_date, e_data_date, data_ori)
                        dataset = dataFactory.get_dataset_close()
                        data_set = dataset[dataset.index >= train_s_date]
                        print(asset, '特征因子：', feature_lst, '训练窗口:', train_days, '测试窗口:', test_days)
                        strategy_obj = HmmStrategy(
                            asset=asset, s_date=s_date, max_states=max_states, leverage=1, fee=0.001, data_set=data_set,
                            cols_features=feature_lst, price_name='close', type='future', train_days=train_days,
                            test_days=test_days)
                        annR, sharp, max_retrace, ret_df = strategy_obj.run_outsample()
                        ret_df.to_csv(resualt_path + 'net_param/%s_%s_%s.csv' %(asset, train_days, test_days), encoding='gbk')
                        for (sdate, edate) in date_lst:
                            net = ret_df.loc[sdate:edate, :]
                            if len(net) > 10:
                                net_lst = net['net'].tolist()
                                annR = annROR(net_lst, 1)
                                sharp = yearsharpRatio(net_lst, 1)
                                max_retrace = maxRetrace(net_lst, 1)
                                period_param_state.append(
                                    [asset, sdate, edate, feature_lst, train_days, test_days, annR, sharp, max_retrace])
                    except:
                        continue
    period_param_state_df = pd.DataFrame(
        period_param_state, columns=['instrument', 'sdate', 'edate', '特征因子', '训练窗口', '测试窗口', '年化收益', '夏普比率', '最大回撤'])
    period_param_state_df.to_csv(resualt_path + 'stockindex_sharp_diff_param_close.csv', encoding='gbk')

    # # %%
    #
    # period_param_state_df
    #
    # # %%
    #
    # for feature_lst in all_feature_lst:
    #     for asset in asset_lst:
    #         for (sdate, edate) in date_lst:
    #             group_ = period_param_state_df[
    #                 (period_param_state_df['sdate'] == sdate) & (period_param_state_df['edate'] == edate) & (
    #                         period_param_state_df['instrument'] == asset)]
    #
    #             if len(group_) == 0:
    #                 continue
    #             harvest = []
    #             for train_days in train_days_lst:
    #                 _group = group_[(group_['训练窗口'] == train_days)]
    #                 harvest_row = []
    #                 for test_days in test_days_lst:
    #                     try:
    #                         sharp = _group[(_group['测试窗口'] == test_days)]['夏普比率'].tolist()[0]
    #                     except:
    #                         sharp = -1
    #                     harvest_row.append(sharp)
    #                 harvest.append(harvest_row)
    #             x_label = train_days_lst
    #             y_label = test_days_lst
    #             # print(harvest)
    #             harvest = np.array(harvest)
    #             fig, ax1 = plt.subplots(figsize=(2 * len(y_label), len(y_label)), nrows=1)
    #
    #             vmax = max(max(harvest[i]) for i in range(len(harvest)))
    #             vmin = -vmax
    #             if vmax < 0:
    #                 vmin = min(min(harvest[i]) for i in range(len(harvest)))
    #             h = sns.heatmap(harvest, annot=True, fmt='.2f', ax=ax1, vmax=vmax, vmin=vmin, annot_kws={'size': 20},
    #                             cbar=False)
    #             cb = h.figure.colorbar(h.collections[0])  # 显示colorbar
    #             cb.ax.tick_params(labelsize=28)
    #             ax1.set_title('%s_%s_%s:特征因子%s不同窗口期热力图' % (asset, sdate, edate, feature_lst), fontsize=32)
    #             ax1.set_xticklabels(y_label, fontsize=20)
    #             ax1.set_yticklabels(x_label, fontsize=20)
    #             font = {'family': 'serif',
    #                     'color': 'darkred',
    #                     'weight': 'normal',
    #                     'size': 16,
    #                     }
    #             ax1.set_xlabel('test_days', fontsize=24)
    #             ax1.set_ylabel('train_days', fontsize=24)
    #             fig.tight_layout()
    #
    # # %%
