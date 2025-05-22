import os
import glob
import time
import shutil
import datetime
import pandas as pd
import vnstock

def _check_existing_data(stock, data_folder, year=None, force_replace=False):
    """
    Check if data exists for a stock and handle force_replace option.
    
    Args:
        stock (str): Stock symbol
        year (int, optional): Specific year to check
        force_replace (bool): If True, remove existing data
    
    Returns:
        tuple: (path, should_proceed)
    """
    if year is not None:
        path = os.path.join(data_folder, stock, str(year))
    else:
        path = os.path.join(data_folder, stock)
        
    if os.path.exists(path):
        if not force_replace:
            print(f"DATA ALREADY EXISTS: {stock}" + (f", {year}" if year else ""))
            return path, False
        if force_replace:
            shutil.rmtree(path)
    
    os.makedirs(path, exist_ok=True)
    return path, True

def _download_from_vnstock(stock, start_date, end_date):
    """
    Download stock data from vnstock API.
    
    Args:
        stock (str): Stock symbol
        start_date (str): Start date in format 'YYYY-MM-DD'
        end_date (str): End date in format 'YYYY-MM-DD'
    
    Returns:
        pd.DataFrame: Downloaded data or None if download failed
    """
    data = vnstock.stock_historical_data(
        symbol=stock,
        start_date=start_date,
        end_date=end_date,
        resolution='1D',
        type='stock',
        beautify=True,
        decor=True,
        source= "DNSE"#"TCBS"
    )
    
    if data is None or data.empty:
        print(f"NO DATA AVAILABLE: {stock}, {start_date} to {end_date}")
        return None
    
    data["logtime"] = datetime.datetime.now().strftime("%Y%m%dT%I:%M%p")
    return data

def _save_data_by_year(data, stock, data_folder,force_replace=False):
    """
    Save data to appropriate year folders.
    
    Args:
        data (pd.DataFrame): Stock data to save
        stock (str): Stock symbol
        force_replace (bool): Whether to replace existing data
    """
    data.index = pd.to_datetime(data.index)
    years = data.index.year.unique()
    
    for year in years:
        year_data = data[data.index.year == year]
        if not year_data.empty:
            path, should_save = _check_existing_data(stock, data_folder, year, force_replace)
            if should_save:
                download_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
                year_data.to_csv(os.path.join(path, f"{download_time}.csv"))
                print(f"{'RENEW' if force_replace else 'NEW'} DATA SAVED TO DATABASE: {stock}, {year}")

def download_stock_data(stock, year, data_folder, path=None, force_replace=False, download_time=None, time_from=None, time_to=None):
    """
    Download historical stock data and save it to the specified path.
    
    Args:
        stock (str): Stock symbol
        year (int): Year to download
        path (str, optional): Path to save data. If None, uses default path
        force_replace (bool): If True, replace existing data
        download_time (str, optional): Timestamp for filename
        time_from (str, optional): Start date in format 'YYYY-MM-DD'
        time_to (str, optional): End date in format 'YYYY-MM-DD'
    """
    if path is None:
        path = os.path.join(data_folder, stock, str(year))
    
    _, should_proceed = _check_existing_data(stock, data_folder, year, force_replace)
    if not should_proceed:
        return
    
    if time_from is None:
        time_from = f"{year}-01-01"
    if time_to is None:
        time_to = f"{year}-12-31"
    if download_time is None:
        download_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    
    data = _download_from_vnstock(stock, time_from, time_to)
    if data is not None:
        data.to_csv(os.path.join(path, f"{download_time}.csv"))
        print(f"{'RENEW' if force_replace else 'NEW'} DATA SAVED TO DATABASE: {stock}")

def download_stock_data_by_date_range(stock, from_date, to_date, data_folder, force_replace=False):
    """
    Download historical stock data for a specific date range and save it to the appropriate year folders.
    
    Args:
        stock (str): Stock symbol
        from_date (str): Start date in format 'YYYY-MM-DD'
        to_date (str): End date in format 'YYYY-MM-DD'
        force_replace (bool): If True, replace existing data
    """
    from_date_dt = pd.to_datetime(from_date)
    to_date_dt = pd.to_datetime(to_date)
    years = range(from_date_dt.year, to_date_dt.year + 1)
    
    # Check if we should proceed with download
    should_proceed = False
    for year in years:
        _, proceed = _check_existing_data(stock, year, force_replace)
        if proceed:
            should_proceed = True
            break
    
    if not should_proceed:
        return
    
    data = _download_from_vnstock(stock, from_date, to_date)
    if data is not None:
        _save_data_by_year(data, stock, data_folder, force_replace)

def download_database(stock_list, year, data_folder, force_replace=False):
    """
    Download and update stock data into the database.
    
    Args:
        stock_list (dict): Dictionary of stock groups and their respective stock symbols
        year (int): Year for which data is to be downloaded
        force_replace (bool): If True, replace existing data
    """
    year = str(year)
    time_from, time_to = f"{year}-01-01", f"{year}-12-31"
    download_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    
    for stock in stock_list:
        download_stock_data(stock, year, data_folder,force_replace=force_replace, 
                          download_time=download_time, time_from=time_from, time_to=time_to)
        time.sleep(0.1)  # Prevent API rate limit issues

def download_database_by_date_range(stock_list, from_date, to_date, force_replace=False):
    """
    Download and update stock data into the database for a specific date range.
    
    Args:
        stock_list (dict): Dictionary of stock groups and their respective stock symbols
        from_date (str): Start date in format 'YYYY-MM-DD'
        to_date (str): End date in format 'YYYY-MM-DD'
        force_replace (bool): If True, replace existing data
    """
    for stock in stock_list:
        download_stock_data_by_date_range(stock, from_date, to_date, force_replace)
        time.sleep(0.1)  # Prevent API rate limit issues

def read_stock(stock, data_folder, year=None):
    """
    Read data of a specific stock.

    Args:
        stock (str): Stock symbol
        year (int): Year of the data to read

    Returns:
        pd.DataFrame: Stock data
    """
    path = os.path.join(data_folder, stock, str(year))
    file_path = glob.glob(os.path.join(path, '*'))[0]
    data = pd.read_csv(file_path, header=[0], index_col=0)
    return data

def read_stocks(stocks, year, data_folder):
    """
    Read data of multiple stocks.

    Args:
        stocks (list): List of stock symbols
        year (int): Year of the data to read

    Returns:
        pd.DataFrame: Combined stock data
    """
    # data = [read_stock(stock, data_folder, year) for stock in stocks]
    # return pd.concat(data, axis=1)
    
    data = []
    for stock in stocks:
        data_i = read_stock(stock, data_folder, year)
        data_i.columns = pd.MultiIndex.from_tuples( [(i, stock) for i in data_i.columns] )
        data.append( data_i )
    # TODO: sửa lại thêm 2 line: stock_id và tên value vì luồng format mới không có tên stock trong raw data
    return pd.concat(data, axis=1)

def read_stocks_years(stocks, data_folder, years=None, year_from=None, year_to=None):
    """
    Read data of multiple stocks across multiple years.

    Args:
        stocks (list): List of stock symbols
        years (list, optional): Specific years to read data for
        year_from (int, optional): Start year (inclusive) if `years` is not provided
        year_to (int, optional): End year (inclusive) if `years` is not provided

    Returns:
        pd.DataFrame: Combined stock data across the specified years
    """
    if years is None:
        if year_from is None or year_to is None:
            raise ValueError("Either 'years' or both 'year_from' and 'year_to' must be provided.")
        years = range(year_from, year_to + 1)
    
    data_frames = [read_stocks(stocks, year, data_folder) for year in years]
    return pd.concat(data_frames, axis=0, ignore_index=True)