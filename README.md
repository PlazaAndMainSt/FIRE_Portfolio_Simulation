# FIRE_Portfolio_Simulation
Investment Portfolio Forecasting

## Intro to the FIRE portfolio modeling tool:
This tool will take your inputs: current portfolio balance, annual contributions, years to forecast out, and your annual expenses when you reach FIRE/retirement. It pulls the historical close prices of the funds in your specified portfolio for the requested time frame. It compiles a list of the 365-day return of that portfolio for every 365-day window in the historical data set. (Example: in a 2 year historical data set, there are 365 1-year windows. Jan 1 2010 - Jan 1 2011, Jan 2 2010 - Jan 2 2011, etc). The model randomly selects returns from that list of historical returns and uses them as your hypothetical returns for each year you are forecasting out. It runs this monte carlo scenario 10,000 times and compiles the results into a histogram to see the distribution.

### Model your personal portfolio based on the actual returns of a provided portfolio
+ Inputs:
    * userid = Your vzid
    * investment_amount = The current value of your investments (retirement & personal)
    * annual_contribution = The total amount you add to your investments each year including:
        * 401k contribution
        * Company 401k match
        * Additional amounts added by your employer
        * Additional amounts you invest each year
    * years_to_model = Number of years from now you are trying to model out
    * annual_expense = The total annual expenses you expect in retirement (or post-FI/RE)
    * time_frame = Number of years of historical data to pull on base portfolio
    * portfolio_dict = dictionary containing the {'TICKER':% of your portfolio}
        * This data is pulled from Yahoo Finance, so the ticker must be available there
        * The default portfolio is:
            * 70% VTSAX: Total US Market Index
            * 15% VGTSX: Total Int'l Market Index
            * 15% VBMFX: Total US Bond Index
        * Supply your own tickers and percents or adjust the percents on the default portfolio as desired
+ Method:
    1. Historical close data is pulled on the tickers in the portfolio provided
    2. 1 year average return rates are calculated for *every* 365-day time period in the data set
    3. The 365-day return rates are compiled in a list of theoretically possible annual returns
    4. A 10,000 cycle monte carlo simulation is run for the supplied years_to_model
        * Each cycle randomly selects years_to_model number of returns from the list generated above
        * These randomly chosen rates are used as the annual returns for your portfolio
        * The portfolio compounds monthly after adding in 1/12th of your annual contribution
        * Portfolio balances are adjusted down for CPI increases (~1.7% annually)
        * The monthly and annual balances are tracked
        * This is repeated 10,000 times to get a very wide range of possible random annual returns
    5. The results of the simulation is displayed in a histogram to illustrate the distribution of your portfolio balance
    6.  Several lines are overlaid for reference:
        * 'Do Nothing' = the total value of your portfolio + contributions
        * 2% Savings = the ending portfolio value if you simply saved the amount in a savings account earning 2% APY
        * Dashed Blue Line = Median value of your portfolio across all simulations
        * 3% FI/RE Amount = The amount you need to be financially independent assuming a 3% safe withdrawal rate and your supplied annual expenses
    7. FI/RE Stats:
        * % of scenarios meeting FIRE Goal = % of the 10,000 simulations that your portfolio balance exceeds the FIRE goal
        * Average Date to Reach FIRE Goal = Average month you meet the FIRE goal, if met
        * FIRE Goals Used: 
            + Main FI --> 25 times your expected annual expenses at retirement (4% safe withdrawal rate)
            + Fat  FI --> 30 times your expected annual expenses at retirement
    

The default portfolio it models off of is based on the three-fund FIRE portfolio recommended by the FIRE community.
VTSAX: Vanguard Total US Market Index Fund
VGTSX: Vanguard Total International Market Index Fund
VBMFX: Vanguard Total US Bond Index Fund
