import pandas as pd
import numpy as np
import yfinance as yf
import keyring
import datetime as dt
from dateutil.relativedelta import relativedelta
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter, StrMethodFormatter
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

pd.options.display.float_format = '{:.2f}'.format

def run_the_portfolio_sim(investment_amount, annual_contribution, annual_expense=0, years_to_model=20, time_frame=8, portfolio_dict={'FSKAX': 0.7,'FSPSX': 0.15,'FXNAX': 0.15}):
    '''
    investment_amount: (int) starting investment balance or amount
    annual_contribution: (int) amount you are contributing annually
    annual_expense: (int) annual expenses needed at FIRE/retirement
    years_to_model: (int) number of years in the market the simulation will run
    time_frame: (int) number of years of historical returns to pull (default=8)
    portfolio_dict: (dict) dictionary with key=stock ticker and value=% of portfolio i.e. {'TICKER': 0.5}
    '''
    welcome_text = '''Running simulation to forecast \na starting portfolio value of {start_amt} \ncontributing {contr} annually for {yr} years'''.format(start_amt='${:,}'.format(investment_amount), contr='${:,}'.format(annual_contribution), yr=str(years_to_model))
    print('\n--------------------------------------')
    print(welcome_text)
    print('\n--------------------------------------')
    
    if sum(portfolio_dict.values()) == 1:
        print('Portfolio allocation = 100%')
    else:
        raise ValueError('Portfolio Allocation does not add up to 100%')

    data = yf.download(tickers=list(portfolio_dict.keys()), period='{x}y'.format(x=time_frame), proxy=web_proxy)
    ticker_close = data['Close'].copy(deep=True)
    #print('\n--------------------------------------')
    #print('Data pulled on your provided portfolio')
    #print(ticker_close.info())
    
    # Re-index the time series data frame since holidays & weekends will be missing
    start_date = dt.datetime.today().date() - relativedelta(years=time_frame)
    end_date = dt.datetime.today().date() - dt.timedelta(1)
    idx = pd.date_range(start_date, end_date)
    ticker_close = ticker_close.reindex(idx, fill_value=np.nan)
    ticker_close.fillna(method='ffill', inplace=True)
    ticker_close.fillna(method='bfill', inplace=True)
    
    ticker_close_whatif = ticker_close.loc[:,].copy(deep=True)

    for k, v in portfolio_dict.items():
        ticker_close_whatif['{ticker}_shares'.format(ticker=k)] = (investment_amount * v) / ticker_close_whatif.iloc[0][k]
        ticker_close_whatif['{ticker}_value'.format(ticker=k)] = ticker_close_whatif['{ticker}_shares'.format(ticker=k)] * ticker_close_whatif[k]

    ticker_close_whatif['Total_value'] = ticker_close_whatif.filter(like='_value').sum(axis=1)
    
    print('\n--------------------------------------')
    print('Generating the historical 365 day actual returns')
    print('*** This can take a short time, please be patient ***')
    ticker_loop_results = {}
    time_frame_days = 365
    for i in range((ticker_close.index[-1] - ticker_close.index[0]).days-time_frame_days):
        ticker_close_loop = ticker_close.iloc[i:i+time_frame_days,].copy(deep=True)

        for k, v in portfolio_dict.items():
            ticker_close_loop['{ticker}_shares'.format(ticker=k)] = (investment_amount * v) / ticker_close_loop.iloc[0][k]
            ticker_close_loop['{ticker}_value'.format(ticker=k)] = ticker_close_loop['{ticker}_shares'.format(ticker=k)] * ticker_close_loop[k]

        ticker_close_loop['Total_value'] = ticker_close_loop.filter(like='_value').sum(axis=1)

        inv_rate_loop = 100 * (ticker_close_loop.filter(like='_value').iloc[-1,:] - ticker_close_loop.filter(like='_value').iloc[0,:])/ticker_close_loop.filter(like='_value').iloc[0,:] / time_frame_days*365
        ticker_loop_results[ticker_close_loop.index[0]] = inv_rate_loop

    ticker_loop_results = pd.DataFrame(ticker_loop_results).T
    print('\n--------------------------------------')
    print('Overall Average Returns for all time periods.')
    print(ticker_loop_results.mean().to_string())
    
    print('\n--------------------------------------')
    print('Running the monte carlo simulation to get distributions of possible results')
    all_one_year_total_returns = np.array(ticker_loop_results['Total_value'])
    all_stats = []
    all_portfolios = []

    num_simulations = 10000
    start_amount = investment_amount
    annual_add_invest = annual_contribution
    for i in range(num_simulations):
        sim_amount, compare_amount, net_rate = start_amount, start_amount, 1
        annual_returns = np.random.choice(all_one_year_total_returns, size=years_to_model)
        portfolio_value = [sim_amount]
        for i in annual_returns:
            for m in range(12):
                net_rate = net_rate * (100+i/12)/100
                sim_amount = sim_amount * (100+i/12)/100 + annual_add_invest/12
                portfolio_value.append(sim_amount)
                compare_amount = compare_amount * (1+0.02/12) + annual_add_invest/12
        all_stats.append([net_rate,sim_amount, compare_amount])
        all_portfolios.append(portfolio_value)
    results_sim_df = pd.DataFrame(all_stats, columns=['Rate', 'Invested', 'Savings_Acct'])
    print('\n--------------------------------------')
    print('Overall Average Results of Simulation')
    print(results_sim_df.mean().to_string())
    
    # Save all monthly results to a data frame
    
    start_date_output = dt.datetime.today().date() + relativedelta(months=1)
    end_date_output = start_date_output + relativedelta(years=years_to_model) + relativedelta(months=1)
    idx_out = pd.date_range(start_date_output, end_date_output, freq='M')
    all_portfolios_trend = pd.DataFrame(all_portfolios)
    all_portfolios_trend = all_portfolios_trend.T
    all_portfolios_trend.set_index(idx_out, inplace=True)
    all_portfolios_trend = all_portfolios_trend.round(0)
    all_portfolios_trend = all_portfolios_trend.sort_values(by=all_portfolios_trend.index[-1], axis=1)
    
    
    # Plot the histogram of results
    sim_data_value = results_sim_df['Invested']
    fig, ax = plt.subplots(figsize=(8,6))
    counts, bins, patches = ax.hist(sim_data_value, facecolor='lightblue', edgecolor='black', bins=15)
    ax.set_xticks(bins)
    ax.xaxis.set_major_formatter(FormatStrFormatter('%0.0f'))
    plt.xticks(rotation=90)
    ax.set_xticklabels(['{:,}'.format(int(x)) for x in ax.get_xticks().tolist()])

    # Change the colors of bars at the edges...
    bottom_pct, top_pct = np.percentile(sim_data_value, [10, 90])
    for patch, rightside, leftside in zip(patches, bins[1:], bins[:-1]):
        if rightside < bottom_pct:
        #if rightside <= 0:
            patch.set_facecolor('red')
        elif leftside > top_pct:
        #elif leftside >= 4.0:
            patch.set_facecolor('green')

    # Label the raw counts and the percentages below the x-axis...
    bin_centers = 0.5 * np.diff(bins) + bins[:-1]
    for count, x in zip(counts, bin_centers):
        # Label the raw counts
        ax.annotate(str(int(count)), xy=(x, 0), xycoords=('data', 'axes fraction'),
            xytext=(0, -18), textcoords='offset points', va='top', ha='center')

        # Label the percentages
        percent = '%0.0f%%' % (100 * float(count) / counts.sum())
        ax.annotate(percent, xy=(x, 0), xycoords=('data', 'axes fraction'),
            xytext=(0, -32), textcoords='offset points', va='top', ha='center')

    min_ylim, max_ylim = plt.ylim()
    plt.axvline(sim_data_value.median(), color='blue', linestyle='dashed', linewidth=1)
    plt.text(sim_data_value.mean()*1.25, max_ylim*0.85, 'Average: ${:,}'.format(int(sim_data_value.mean())))
    plt.text(sim_data_value.mean()*1.25, max_ylim*0.80, 'Median: ${:,}'.format(int(sim_data_value.median())))

    compare_amount = results_sim_df['Savings_Acct'].mean()
    plt.axvline(compare_amount, color='k', linestyle='dashed', linewidth=1)
    plt.text(compare_amount*1.01, max_ylim*0.96, '<- 2% Savings: ${:,}'.format(int(compare_amount)))

    do_nothing_amt = (investment_amount + annual_contribution*years_to_model)
    plt.axvline(do_nothing_amt, color='k', linestyle='dashed', linewidth=1)
    plt.text(do_nothing_amt*1.01, max_ylim*0.75, '<- Do Nothing')
    
    if annual_expense > 0:
        fire_amount_03 = annual_expense/0.03
        plt.axvline(fire_amount_03, color='red', linestyle='dashed', linewidth=1)
        plt.text(fire_amount_03*1.01, max_ylim*0.50, '<- 3% FIRE Amount')
        print('FIRE Goal used: ${:,}'.format(int(fire_amount_03)))
        fire_winners = (results_sim_df['Invested'] >= fire_amount_03).sum() / num_simulations
        months_to_fi = (all_portfolios_trend < fire_amount_03).sum()
        avg_months_to_fi = months_to_fi[months_to_fi != months_to_fi.max()].mean()
        avg_date_of_fi = dt.datetime.today().date() + relativedelta(months=int(avg_months_to_fi))
        print('% of scenarios meeting FIRE Goal: {}%'.format(round(100*fire_winners, 2)))
        print('Average Date to reach FIRE Goal: {dt}'.format(dt=avg_date_of_fi.strftime('%m/%Y')))

    # Give ourselves some more room at the bottom of the plot
    plt.title('Simulated Return Value Probabilities')
    plt.subplots_adjust(bottom=0.2)
    plt.show()
    
    return all_portfolios_trend

current_balance = int(input('Current investment balance: '))
contribution_amt = int(input('Current annual contributions: '))
years_for_model = int(input('How many years out to model: '))
annual_expenses = int(input('Current annual expenses: '))
bond_pct_of_port = int(input('% of the portfolio in bonds: '))/100


if bond_pct_of_port >0.85:
    use_bond_pct = 0.85
else:
    use_bond_pct = bond_pct_of_port
user_portfolio = {'VTSAX': 0.85-use_bond_pct, 'VGTSX': 0.15, 'VBMFX': use_bond_pct}

vanguard_test = run_the_portfolio_sim(investment_amount=current_balance, 
                      annual_contribution=contribution_amt, 
                      years_to_model=years_for_model,
                      annual_expense=annual_expenses,
                      time_frame=18,
                    portfolio_dict={'VTSAX': 0.70, 'VGTSX': 0.15, 'VBMFX': 0.15})



