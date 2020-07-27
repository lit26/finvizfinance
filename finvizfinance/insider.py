from finvizfinance.util import webScrap
import pandas as pd

INSIDER_URL = 'https://finviz.com/insidertrading.ashx'

class Insider:
    def __init__(self, option='latest'):
        if option == 'latest':
            self.soup = webScrap(INSIDER_URL)
        elif option == 'top week':
            self.soup = webScrap(INSIDER_URL+'?or=-10&tv=100000&tc=7&o=-transactionValue')
        elif option == 'top owner trade':
            self.soup = webScrap(INSIDER_URL+'?or=10&tv=1000000&tc=7&o=-transactionValue')
        self.df = None

    def getInsider(self):
        insider_trader = self.soup.findAll('table')[5]
        rows = insider_trader.findAll('tr')
        table_header = [i.text.strip() for i in rows[0].findAll('td')]
        df = pd.DataFrame([], columns=table_header)
        rows = rows[1:]
        for row in rows:
            cols = row.findAll('td')
            ticker = cols[0].text
            owner = cols[1].text
            relationship = cols[2].text
            date = cols[3].text
            transaction = cols[4].text
            cost = cols[5].text
            cost = float(cost)
            n_shares = cols[6].text
            n_shares = float(''.join(n_shares.split(',')))
            value = cols[7].text
            value = float(''.join(value.split(',')))
            n_shares_total = cols[8].text
            n_shares_total = float(''.join(n_shares_total.split(',')))
            sec_form = cols[9].text
            df = df.append({'Ticker': ticker,
                            'Owner': owner,
                            'Relationship': relationship,
                            'Date': date,
                            'Transaction': transaction,
                            'Cost': cost,
                            '#Shares': n_shares,
                            'Value ($)': value,
                            '#Shares Total': n_shares_total,
                            'SEC Form 4': sec_form}, ignore_index=True)
        self.df = df
        return df