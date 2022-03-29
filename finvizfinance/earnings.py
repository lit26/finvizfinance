"""
.. module:: earnings
   :synopsis: earnings.

.. moduleauthor:: Tianning Li <ltianningli@gmail.com>
"""
import os
import pandas as pd
from finvizfinance.screener.financial import Financial
from finvizfinance.screener.overview import Overview
from finvizfinance.screener.valuation import Valuation
from finvizfinance.screener.ownership import Ownership
from finvizfinance.screener.performance import Performance
from finvizfinance.screener.technical import Technical


class Earnings:
    """Earnings
    Partition dataframe of ticker information of period of earning dates(This Week,
    Next Week, Previous Week, This Month) into dates

    Args:
        period(str): choose an option of period(This Week, Next Week,
                     Previous Week, This Month).
    """

    def __init__(self, period="This Week"):
        """initiate module"""
        self.earning_days = []
        self.df_days = {}
        self.df = None
        self.period = period
        self._set_period(period)

    def _set_period(self, period):
        """Set the period.

        Args:
            period(str): choose an option of period(This Week, Next Week,
                         Previous Week, This Month).
        """
        check_list = ["This Week", "Next Week", "Previous Week", "This Month"]
        if period not in check_list:
            raise ValueError(
                "Invalid period '{}'. Available period: {}".format(period, check_list)
            )
        self.period = period
        ffinancial = Financial()
        filters_dict = {"Earnings Date": period}
        ffinancial.set_filter(filters_dict=filters_dict)
        self.df = ffinancial.screener_view(order="Earnings Date", verbose=0)
        self.earning_days = list(set(self.df["Earnings"].to_list()))
        self.earning_days.sort()

    def partition_days(self, mode="financial"):
        """Partition dataframe to separate dataframes according to the dates.

        Args:
            mode(str): choose an option of period(financial, overview, valuation, ownership,
                       performance, technical).
        """
        check_list = [
            "financial",
            "overview",
            "valuation",
            "ownership",
            "performance",
            "technical",
        ]
        if mode not in check_list:
            raise ValueError(
                "Invalid mode '{}'. Available mode: {}".format(mode, check_list)
            )

        for earning_day in self.earning_days:
            if mode == "financial":
                self.df_days[earning_day] = self.df[
                    self.df["Earnings"] == earning_day
                ].reset_index(drop=True)
            else:
                self.df_days[earning_day] = self.df[self.df["Earnings"] == earning_day][
                    "Ticker"
                ].to_list()

        fearnings = None
        if mode == "financial":
            return self.df_days
        elif mode == "overview":
            fearnings = Overview()
        elif mode == "valuation":
            fearnings = Valuation()
        elif mode == "ownership":
            fearnings = Ownership()
        elif mode == "performance":
            fearnings = Performance()
        elif mode == "technical":
            fearnings = Technical()

        filters_dict = {"Earnings Date": self.period}
        fearnings.set_filter(filters_dict=filters_dict)
        df2 = fearnings.screener_view(order="Earnings Date", verbose=0)
        df2_days = {}
        for earning_day in self.earning_days:
            tickers = self.df_days[earning_day]
            df2_days[earning_day] = df2[df2["Ticker"].isin(tickers)].reset_index(
                drop=True
            )
        self.df_days = df2_days
        return self.df_days

    def output_excel(self, output_file="earning_days.xlsx"):
        """Output dataframes to single Excel file.

        Args:
            output_file(str): name of the output excel file.
        """
        print("Print to Excel...")
        with pd.ExcelWriter(  # pylint: disable=abstract-class-instantiated
            output_file, datetime_format="YYYY-MM-DD", engine="xlsxwriter"
        ) as writer:
            for name, df in self.df_days.items():
                sheet_name = "_".join(name.split("/"))
                df.to_excel(writer, sheet_name=sheet_name, index=False)

    def output_csv(self, output_dir="earning_days"):
        """Output dataframes to csv files.

        Args:
            output_dir(str): name of the output directory.
        """
        print("Print to CSV...")
        isdir = os.path.isdir(output_dir)
        if not isdir:
            os.mkdir(output_dir)
        for name, df in self.df_days.items():
            file_name = "_".join(name.split("/"))
            df.to_csv(output_dir + "/" + file_name + ".csv", index=False)
