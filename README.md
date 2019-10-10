# FIRE_Portfolio_Simulation
Investment Portfolio Forecasting

Intro to the FIRE portfolio modeling tool:
This tool will take your inputs: current portfolio balance, annual contributions, years to forecast out, and your annual expenses when you reach FIRE/retirement. It pulls the historical close prices of the funds in your specified portfolio for the requested time frame. It compiles a list of the 365-day return of that portfolio for every 365-day window in the historical data set. (Example: in a 2 year historical data set, there are 365 1-year windows. Jan 1 2010 - Jan 1 2011, Jan 2 2010 - Jan 2 2011, etc). The model randomly selects returns from that list of historical returns and uses them as your hypothetical returns for each year you are forecasting out. It runs this monte carlo scenario 10,000 times and compiles the results into a histogram to see the distribution.

The default portfolio it models off of is based on the three-fund FIRE portfolio recommended by the FIRE community.
VTSAX: Vanguard Total US Market Index Fund
VGTSX: Vanguard Total International Market Index Fund
VBMFX: Vanguard Total US Bond Index Fund
