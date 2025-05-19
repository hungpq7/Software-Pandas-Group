import os
import glob
from datetime import datetime
import pandas as pd
from .data_processing import download_database, read_stock, read_stocks, read_stocks_years

class DataDriver:
    def __init__(self, data_folder):
        """
        Initialize the DataDriver with a data folder path.
        
        Args:
            data_folder (str): Path to the folder containing stock data
        """
        self.data_folder = data_folder
        # Create data folder if it doesn't exist
        os.makedirs(data_folder, exist_ok=True)
        self.metadata = self._scan_metadata()
    
    def _scan_metadata(self):
        """
        Scan the data folder to collect metadata about available stocks and date ranges.
        
        Returns:
            dict: Metadata containing stocks, first day, and last day
        """
        metadata = {
            'stocks': [],
            'first_day': None,
            'last_day': None
        }
        
        try:
            # Get all stock folders
            stock_folders = [d for d in os.listdir(self.data_folder) 
                            if os.path.isdir(os.path.join(self.data_folder, d))]
            
            if not stock_folders:
                return metadata
            
            metadata['stocks'] = stock_folders
            
            # Scan through all data files to find date ranges
            # for stock in stock_folders:
            stock = stock_folders[0] # only check one stock for efficiency
            print("metadata is checking for only one stock: ", stock)
            stock_path = os.path.join(self.data_folder, stock)
            year_folders = [d for d in os.listdir(stock_path) 
                            if os.path.isdir(os.path.join(stock_path, d))]
            
            for year in year_folders:
                year_path = os.path.join(stock_path, year)
                data_files = glob.glob(os.path.join(year_path, '*.csv'))
                
                if not data_files:
                    continue
                    
                # Read the first file to get date range
                df = pd.read_csv(data_files[0], index_col=0)
                dates = pd.to_datetime(df.index)
                
                if metadata['first_day'] is None or dates.min() < metadata['first_day']:
                    metadata['first_day'] = dates.min()
                if metadata['last_day'] is None or dates.max() > metadata['last_day']:
                    metadata['last_day'] = dates.max()
        except Exception as e:
            print(f"Warning: Error scanning metadata: {str(e)}")
            # Return empty metadata if there's an error
            return metadata
        
        return metadata
    
    def get_available_stocks(self):
        """
        Get list of stocks available in the data folder.
        
        Returns:
            list: List of available stock symbols
        """
        
        return self.metadata['stocks']
    
    def get_date_range(self):
        """
        Get the date range of available data.
        
        Returns:
            tuple: (first_day, last_day) as datetime objects
        """
        return self.metadata['first_day'], self.metadata['last_day']
    
    def get_stock_data(self, stock, year=None, download_if_missing=True):
        """
        Get data for a specific stock. If the data is not available locally and 
        download_if_missing is True, it will download the data first.
        
        Args:
            stock (str): Stock symbol
            year (int, optional): Specific year to get data for. If None, gets all available years
            download_if_missing (bool): Whether to download data if not available locally
            
        Returns:
            pd.DataFrame: Stock data
        """
        stock_path = os.path.join(self.data_folder, stock)
        
        # Check if stock data exists locally
        if not os.path.exists(stock_path):
            if download_if_missing:
                # Download data for the current year if no year specified
                if year is None:
                    year = datetime.now().year
                download_database({stock: [stock]}, year, self.data_folder, force_replace=False)
            else:
                raise ValueError(f"Stock {stock} not found in local data folder")
        
        # Read the data
        if year is not None:
            return read_stock(stock, self.data_folder, year)
        else:
            # Get all available years for this stock
            years = [d for d in os.listdir(stock_path) 
                    if os.path.isdir(os.path.join(stock_path, d))]
            return read_stocks_years([stock], self.data_folder, years=[int(y) for y in years])
    
    def get_multiple_stocks_data(self, stocks, year=None, download_if_missing=True):
        """
        Get data for multiple stocks. If any stock's data is not available locally and 
        download_if_missing is True, it will download the data first.
        
        Args:
            stocks (list): List of stock symbols
            year (int, optional): Specific year to get data for. If None, gets all available years
            download_if_missing (bool): Whether to download data if not available locally
            
        Returns:
            pd.DataFrame: Combined stock data
        """
        # Check and download missing stocks if needed
        if download_if_missing:
            missing_stocks = [s for s in stocks if s not in self.metadata['stocks']]
            if missing_stocks:
                if year is None:
                    year = datetime.now().year
                download_database({s: [s] for s in missing_stocks}, year, force_replace=False)
                # Update metadata after downloading
                self.metadata = self._scan_metadata()
        
        # Read the data
        if year is not None:
            return read_stocks(stocks, year, self.data_folder)
        else:
            # Get all available years
            years = range(
                self.metadata['first_day'].year,
                self.metadata['last_day'].year + 1
            )
            return read_stocks_years(stocks, self.data_folder, years=years)
        
    def read_stocks_years(self, stocks, years):
        return read_stocks_years(stocks, self.data_folder, years=years)

    def download_database(self, stocks, year=None, force_replace=False):
        """
        Download data for multiple stocks for a specific year.
        
        Args:
            stocks (list): List of stock symbols to download
            year (int, optional): Year to download data for. If None, uses current year
            force_replace (bool): Whether to replace existing data
        """
        if year is None:
            year = datetime.now().year
            
        # Download data for each stock
        download_database(stocks, year, self.data_folder, force_replace)
        
        # Update metadata after downloading
        self.metadata = self._scan_metadata() 