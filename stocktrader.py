"""
stocktrader -- A Python module for virtual stock trading
A module that allows the user to load stock data and portflios. Portfolios can
be valuated and transactions can be added. Furthermore, automated trading
strategies can be implemented.

This module was created in Python 3.6.3
"""
class TransactionError(Exception):
    pass

class DateError(Exception):
    pass

stocks = {}
portfolio = {}
transactions = []

def normaliseDate(s):
    """
    This will convert any dates specified in YYYY-MM-DD, YYYY/MM/DD or
    DD.MM.YYYY to YYYY-MM-DD for use in the program. Strings formatted as above
    are hence accepted as inputs and all output will be in the form YYYY-MM-DD.
    A DateError exception IS raised if dates are not in the required format
    """
    if list(s)[4] == "-":
        a = "-"
    elif list(s)[4] == "/":
        a = "/"
    else:
        a = "."
    ymd = s.split(a)
    try:
        if a == ".":
            days = str(int(ymd[0]))
            years = str(int(ymd[2]))
        else:
            days = str(int(ymd[2]))
            years = str(int(ymd[0]))
        months = str(int(ymd[1]))
    except ValueError:
        raise DateError("The date entered is in an invalid format")
    if len(ymd) != 3 or len(days) > 2 or len(months) > 2 or len(years) != 4:
        raise DateError("The date entered is in an invalid format")
    if len(days) == 1:
        days = "0" + days
    if len(months) == 1:
        months = "0" + months
    t = years + "-" + months + "-" + days
    return t

def loadStock(symbol):
    #Got the idea of using enumerate: https://stackoverflow.com/questions/28602689/python-read-file-and-write-lines-according-to-their-index-number
    """
    This function will create a dictionary of date and price information for
    the requested stock and then add this to the stocks dictionary.
    This uses data from stocks in the 'stockdata/' subdirectory.
    A key part is to create lists to set up the dictionary to have a key of
    4 prices for each date element (the normaliseDate function was used).
    """
    fdates = list()
    fprices = list()
    try:
        f = open("stockdata/" + symbol + ".csv", mode="rt", encoding="utf8")
    except FileNotFoundError:
        raise FileNotFoundError("This stock file does not exist hence you can not load stocks of this company")
    try:
        for i, line in enumerate(f):
            if i != 0:
                g = line.split(",")
                fdates.append(normaliseDate(g[0]))
                gp = [float(x) for x in g[1:5] ]
                fprices.append(gp)
        f.close()
    except UnicodeDecodeError:
        raise ValueError("The stock file is not correctly formatted")
    sinfo = dict(zip(fdates, fprices))
    sdict = {symbol: sinfo}
    stocks.update(sdict)

def loadPortfolio(fname="portfolio.csv"):
    """
    This function will open a specified portfolio file from the current
    directory and then modify the portfolio dictionary accordingly.
    The portfolio dictionary should include a date, cash value and stock
    volumes. The required stocks are loaded using loadStock()
    """
    portfolio.clear()
    transactions.clear()
    try:
        f = open(fname, mode="rt", encoding="utf8")
    except Exception:
        raise FileNotFoundError("The requested portfolio file does not exist")
    try:
        for i, line in enumerate(f):
            if i == 0:
                portfolio["date"] = normaliseDate(line)
            elif i == 1:
                portfolio["cash"] = int(line)
            else:
                g = line.split(",")
                portfolio[g[0]] = int(g[1])
                loadStock(g[0])
        f.close()
    except Exception:
        raise ValueError("The portfolio file is not correctly formatted")

def valuatePortfolio(date=None, verbose=False):
    """
    This function will return the sum of the cash and value of all shares
    in the portfolio dictionary at the date specified. The low price of all
    shares on the date is taken. If no date was specified, the portfolio date
    is taken. A selection of verbose=True will print a summary of the portfolio.
    """
    if date == None:
        date = portfolio['date']
    else:
        date = normaliseDate(date)
    ymddate = normaliseDate(date).split("-") #index [0] will be years for each, [1] months, [2] days
    ymdpf = normaliseDate(portfolio['date']).split("-")
    if ( int(ymddate[0]) < int(ymdpf[0]) ) or ( int(ymddate[0]) == int(ymdpf[0]) and int(ymddate[1]) < int(ymdpf[1]) ) or ( int(ymddate[0]) == int(ymdpf[0]) and int(ymddate[1]) == int(ymdpf[1]) and int(ymddate[2]) < int(ymdpf[2]) ):
        raise DateError("The date to valuate your portfolio is before the portfolio was created, which is not possible!")

    value = portfolio['cash']
    for x in portfolio:
        if x not in ['date', 'cash']:
            try:
                value += portfolio[x]*((stocks[x][date])[2])
            except KeyError:
                raise DateError("The date selected to valuate the portfolio is not a trading day")
    if bool(verbose) == True:
        print('Your portfolio on {}:'.format(date))
        print('[* share values based on the lowest price on {}]\n'.format(date))
        print('{:<15} | {:^8} | {:^10} | {:^10}'.format('Capital Type', 'Volume', 'Val/Unit*', 'Value in £*'))
        print('-'*16 + '+' + '-'*10 + '+' + '-'*12 + '+' + '-'*12)
        if portfolio['cash'] != 0:
            print('{:<15} | {:^8} | {:^10.2f} | {:^10.2f}'.format('Cash', '1', portfolio['cash'], portfolio['cash']))
        for x in portfolio:
            if x not in ['date', 'cash']:
                print('{:<15} | {:^8} | {:^10.2f} | {:^10.2f}'.format('Shares of ' + x, portfolio[x], (stocks[x][date])[2], portfolio[x]*((stocks[x][date])[2]) ))
        print('-'*16 + '+' + '-'*10 + '+' + '-'*12 + '+' + '-'*12)
        print('TOTAL VALUE' + ' '*32 + '{:>.2f}\n'.format(value))
    return value

def addTransaction(trans, verbose=False):
    """
    This function will modify the portfolio dict. based on an input, on
    the date given. The cash in the portfolio will be increased/decreased when
    a transaction sells/buys shares, the volume of shares of the corresponding
    symbol will also be modified by the amount given by the 'volume' key.
    If the parameter verbose is set to True, a breakdown is printed. The
    transactions list is appended with the input data.
	A TransactionError Exception is raised if an invalid transaction is given
    """
    ymdtrans = normaliseDate(trans['date']).split("-") #index [0] will be years for each, [1] months, [2] days
    ymdpf = normaliseDate(portfolio['date']).split("-")
    if ( int(ymdtrans[0]) < int(ymdpf[0]) ) or ( int(ymdtrans[0]) == int(ymdpf[0]) and int(ymdtrans[1]) < int(ymdpf[1]) ) or ( int(ymdtrans[0]) == int(ymdpf[0]) and int(ymdtrans[1]) == int(ymdpf[1]) and int(ymdtrans[2]) < int(ymdpf[2]) ):
        raise DateError("The date to add a transaction is before the current portfolio date, which is not possible")
    if trans['symbol'] not in stocks:
        raise ValueError("The stocks you have requested a transaction of do not exist or have not been loaded")
    if trans['symbol'] not in portfolio:
        portfolio.update({trans['symbol']: 0})

    if trans['volume'] <= 0: #will be selling shares
        portfolio['cash'] += abs(trans['volume'])*(stocks[trans['symbol']][normaliseDate(trans['date'])][2])
    else: #will be buying shares
        portfolio['cash'] -= abs(trans['volume'])*(stocks[trans['symbol']][normaliseDate(trans['date'])][1])
        if portfolio['cash'] < 0:
            raise TransactionError("You do not have enough cash to purchase these shares")

    portfolio[trans['symbol']] += trans['volume']
    if portfolio[trans['symbol']] == 0:
        del portfolio[trans['symbol']] #No need to have an entry with 0 shares
    elif portfolio[trans['symbol']] < 0:
        raise TransactionError("You have requested to sell more shares than are in your portfolio")

    portfolio['date'] = normaliseDate(trans['date'])
    transactions.append(trans)
    if bool(verbose) == True:
        if trans['volume'] <= 0:
            print('{}: Sold {} shares of {} for a total of £{:^10.2f}'.format(normaliseDate(trans['date']), abs(trans['volume']), trans['symbol'], abs(trans['volume'])*(stocks[trans['symbol']][normaliseDate(trans['date'])][2]) ))
        else:
            print('{}: Bought {} shares of {} for a total of £{:^10.2f}'.format(normaliseDate(trans['date']), abs(trans['volume']), trans['symbol'], abs(trans['volume'])*(stocks[trans['symbol']][normaliseDate(trans['date'])][1]) ))
        print('Available cash: £{:^6.2f}\n'.format(portfolio['cash']))

def savePortfolio(fname="portfolio.csv"):
    """
    This function will save the current portfolio to the current directory.
    This will be in the format; date, cash, shares and corresponding volume
    """
    with open(fname, mode="wt", encoding="utf8") as f:
        f.write(portfolio['date']+"\n")
        f.write(str(portfolio['cash'])+"\n")
        for x in portfolio:
            if x not in ['date', 'cash']:
                f.write(str(x) + "," + str(portfolio[x]) + "\n")

from os import listdir as ld  #this will be used for the 2 functions below AND TRADESTRATEGY2
def sellAll(date=None, verbose=False):
    """
    This function will quickly sell all stocks in the portfolio by performing
    a sell transaction for each stock in the portfolio. This modifies the
    portfolio dictionary
    """
    if date == None:
        date = portfolio['date']
    else:
        date = normaliseDate(date)
    for x in ld("stockdata/"): #as otherwise an error iterating over dictionary
        if x[:-4] in portfolio:
            if bool(verbose) == False:
                addTransaction({'date':date, 'symbol':x[:-4], 'volume':portfolio[x[:-4]]*(-1)})
            else:
                addTransaction({'date':date, 'symbol':x[:-4], 'volume':portfolio[x[:-4]]*(-1)}, True)

def loadAllStocks():
    """
    This function applies loadStock() to all files in the "stockdata/"
    subdirectory, hence loads all possible stocks to the dictionary
    """
    for i in ld("stockdata/"):
        try:
            loadStock(i[:-4]) #removes ".csv", which is added again by loadStock()
        except Exception:
            pass

def tradeStrategy1(verbose=False):
    """
    This function implements a trading strategy where the stock with the highest
    price growth over 10 days is bought and then sold when its price has
    sufficiently increased/decreased. The functions which determine this are
    detailed. This process is then repeated throughout the time period.
    Only 1 stock is traded at one time. Data from the stock dictionary is used,
    hence required stocks must be loaded. The portfolio dictionary is modified
    using addTransaction()
    """
    lstdates = list()
    for i in stocks:
        for j in stocks[i]:
            lstdates.append(normaliseDate(j))
        break #A way of only using one stock for dates
    lstdates.sort()
    def H(s,j):
        #The high price of stock s on trading day number j
        return stocks[s][lstdates[j]][1] #this could return the 0th entry
    def L(s,k):
        #The low price of stock s on trading day number k
        return stocks[s][lstdates[k]][2]
    def Q_buy(s,j):
        #A measure of how much a stock price has risen over 10 trading days
        return 10*H(s,j) / (H(s,j) + H(s,j-1) + H(s,j-2) + H(s,j-3) + H(s,j-4) + H(s,j-5) + H(s,j-6) + H(s,j-7) + H(s,j-8) + H(s,j-9)) #try and condense this
    def Q_sell(s,j,k):
        #A measure of how much value the stock has added/removed to portfolio
        return L(s,k) / H(s,j)
    try:
        j = lstdates.index(normaliseDate(portfolio['date']))
    except ValueError: #if portfolio is not trading day, just choose day 10
        j = 9
    if j < 9:
        j = 9
    while j < len(lstdates):
        qbuys = list()
        for s in stocks:
            qbuys.append(Q_buy(s,j))
            if Q_buy(s,j) == max(qbuys):
                t = s #t will be the optimal stock
        v = 0
        while (stocks[t][lstdates[j]][1])*v <= portfolio['cash']:
            v +=1
        else:
            v -= 1 #so the volume is the maximum whilst still having cash
        addTransaction({'date':lstdates[j], 'symbol':t, 'volume':v}, verbose)
        k = j+1
        while Q_sell(t,j,k) > 0.7 and Q_sell(t,j,k) < 1.3 and k < len(lstdates)-1:
            k += 1
        if k < len(lstdates)-1: #else we have reached the final trading day
            addTransaction({'date':lstdates[k], 'symbol':t, 'volume':-v}, verbose)
        j = k+1

from os import listdir
def tradeStrategy2(verbose=False):
    """
    This strategy works using 2 principles;
    1) Shares with a relatively constant share price, which are not prone to
    sudden price changes, seem to be a safer investment
    2) If a share price has gained massively, then it is prone to a later lapse
    in price. Hence it is a good time to sell after a big price hike

    The 5 least volatile stocks are bought on the 225th trading day, or the date
    of the portfolio. These stocks are only sold if there is a significant
    increase in their price (x1.7). The aim is to only buy less risky stocks
    and keep transactions to a minimum to avoid losses.

    Data from the stocks dictionary is used hence stocks must be loaded, and
    the portfolio dictionary is modified accordingly.

    This is a conservative strategy compared to tradeStrategy1, hopefully
    fitted for investors who aim to guarantee a small profit but not aim big
    """
    m=225 #the number of trading days to consider stock data
    n=5 #the number of stocks to buy
    r=1.7 #the price gain ratio at which to sell any stocks
    lstdates = list()
    for i in stocks:
        for j in stocks[i]:
            lstdates.append(normaliseDate(j))
        break
    lstdates.sort()
    def H(s,j):
        return stocks[s][lstdates[j]][1]
    def L(s,k):
        return stocks[s][lstdates[k]][2]
    def MaxH(s,j): #the max high price of stock s over 200 days previously from day j
        highs = list()
        for i in range(m):
            highs.append(stocks[s][lstdates[j-i]][1])
        return max(highs)
    def MinL(s,j): #the min low price of a stock s over 200 days previously from day j
        lows = list()
        for i in range(m):
            lows.append(stocks[s][lstdates[j-i]][2])
        return min(lows)
    def Q_buy2(s,j): #a measure of how much a stock has varied in price in the 200 days prior to i
        return MaxH(s,j) / MinL(s,j)
    def Q_sell(s,j,k): #a measure of how much value the stock has added/removed to portfolio
        return L(s,k) / H(s,j)
    try:
        k = lstdates.index(normaliseDate(portfolio['date'])) #the numbered day to work from
    except ValueError: #if portfolio is not trading day, just choose day m-1
        k = m-1
    if k < m-1:
        k = m-1
    qbuys = list()
    for s in stocks:
        qbuys.append(abs(Q_buy2(s,k) -1))
    qbuys.sort()
    topn = qbuys[:n] #So we aim to buy the top n stocks
    msps = (portfolio['cash'])/n #maximum spend per stock
    for s in stocks:
        if abs(Q_buy2(s,k) -1) in topn:
            v = 0
            while (stocks[s][lstdates[k]][1])*v <= msps:
                v +=1
            else:
                v -= 1 #so the volume is the maximum whilst still having cash
            addTransaction({'date':lstdates[k], 'symbol':s, 'volume':v}, verbose)
    #so we have now bought the n least volatile stocks. Next we sell stocks if they make a big price gain
    for x in ld("stockdata/"):
        if x[:-4] in portfolio:
            l = k
            while Q_sell(x[:-4],k,l) < r and l < len(lstdates)-1:
                l +=1
            if l < len(lstdates)-1:
                try:
                    addTransaction({'date':lstdates[l], 'symbol':x[:-4], 'volume':-1*portfolio[x[:-4]]}, verbose)
                except DateError: #if attempt to perform transaction before portfolio date, unavoidable as stocks looked at 1 by 1
                    pass #simply do not carry out transaction

def main():
    loadPortfolio('portfolio0.csv')
    loadAllStocks()
    valuatePortfolio(verbose=True)
    tradeStrategy1(verbose=True)
    valuatePortfolio('2018-03-13', verbose=True)
    print(stocks)

main()

if __name__ == '__main__' or __name__ == 'builtins':
    main()
