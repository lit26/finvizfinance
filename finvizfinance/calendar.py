from finvizfinance.util import webScrap
import pandas as pd

"""
.. module:: Calendar
   :synopsis: Calendar table.

.. moduleauthor:: Andres Gonzalez <atowersc@gmail.com> 
In inspiration with Tianning Li <ltianningli@gmail.com> 
"""

CALENDAR_URL = 'https://finviz.com/calendar.ashx'

class Calendar:
    """Calendar
    Getting information from the complete week Calendar page.
    """
    
    def __init__(self):
        """initiate module

        """
        self.soup = webScrap(CALENDAR_URL)
        self.calendar = {}

    def getCalendar(self):
        """Get calendar information table.

        Retrieves table information from finviz finance calendar.

        Returns:
            calendar(dict): calendar table

        """
        tables = self.soup.findAll('table')
        calendar = tables[3]
        calendar_df = self._getNewsHelper(calendar)


        self.calendar = calendar_df
        return self.calendar

    def _getNewsHelper(self, tables):
        """Get insider information table helper function.

        Returns:
            df(pandas.DataFrame): calendar information table

        """

        df = pd.DataFrame([], columns=['Date', 'Next', 'Release', 'Impact', 'For', 'Val', 'Actual', 'Expected', 'Prior'])
        tables = tables.findAll('tr')[3:]

        for row in tables:
            cols = row.find_all('td')
            date = cols[0].text
            
            attr = row.get("class")
            if str(attr) == "['calendar-now']":
                nexxt = ">>>>"
            else:
                nexxt = "    "

            if cols[2].text == "Release":
                release = "----------"
            else:
                release = cols[2].text
            imp = row.findAll('img')[1].get("src")
            if imp.endswith('_1.gif'):
                impact = "x"
            else:
                if imp.endswith('_2.gif'):
                    impact = "xx"
                else:
                    if imp.endswith('_3.gif'):
                        impact = "xxx"
                    else:
                        impact = "----------"
            if cols[4].text == "For":
                forr = "----------"
            else:
                forr = cols[4].text
            try:
                if cols[5].find("span").get("style") == "color:#008800;":
                    val = " > "
                else:
                    val = " < "
            except:
                val = "---"
            if cols[5].text == "Actual":
                actual = "----------"
            else:
                actual = cols[5].text
            if cols[6].text == "Expected":
                expected = "----------"
            else:
                expected = cols[6].text
            if cols[7].text == "Prior":
                prior = "----------"
            else:
                prior = cols[7].text
            df = df.append({
            'Date':date,
            'Next':nexxt,
            'Release':release,
            'Impact':impact,
            'For':forr,
            'Val':val,
            'Actual':actual,
            'Expected':expected,
            'Prior':prior},
            ignore_index=True)
        return df