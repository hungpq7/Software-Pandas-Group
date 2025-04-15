from flask import Flask, render_template, request, redirect, url_for
from smartinvest import DataDriver
from smartinvest.interactor.stock_qa import StockQASystem
import os
from datetime import datetime, timedelta

app = Flask(__name__)

# Initialize DataDriver
project_root = os.path.dirname(os.path.abspath(__file__))
data_folder = os.path.join(project_root, 'data')
data_driver = DataDriver(data_folder=data_folder)

# Initialize QA System
qa_system = None

def initialize_qa_system():
    """
    Initialize the QA system with the data driver.
    This function ensures the QA system is initialized only once.
    """
    global qa_system
    if qa_system is None:
        try:
            qa_system = StockQASystem(data_driver)
            print("QA System initialized successfully")
        except Exception as e:
            print(f"Error initializing QA system: {str(e)}")
            qa_system = None

# Initialize QA system when the app starts
initialize_qa_system()

def should_refresh_data():
    """
    Check if data should be refreshed based on the last available date.
    Returns True if current date is more than 2 days ahead of the last date in database.
    """
    try:
        first_day, last_day = data_driver.get_date_range()
        if last_day is None:
            return True
        
        current_date = datetime.now().date()
        last_date = last_day.date()
        days_diff = (current_date - last_date).days
        
        return days_diff > 2
    except Exception as e:
        print(f"Error checking refresh condition: {str(e)}")
        return False

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    result_type = None
    download_message = None
    refresh_message = None
    current_year = datetime.now().year
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'check_stocks':
            stocks = data_driver.get_available_stocks()
            result = '\n'.join(stocks)
            result_type = 'stocks'
            
        elif action == 'check_dates':
            first_day, last_day = data_driver.get_date_range()
            result = f"From: {first_day}\nTo: {last_day}"
            result_type = 'dates'
            
        elif action == 'download_stock':
            stock_id = request.form.get('stock_id', '').strip().upper()
            year = request.form.get('year', '')
            
            if not stock_id:
                download_message = "Please enter a stock ID"
            elif not year:
                download_message = "Please enter a year"
            else:
                try:
                    year = int(year)
                    if year < 2000 or year > 2100:
                        download_message = "Year must be between 2000 and 2100"
                    else:
                        # Check if stock exists
                        available_stocks = data_driver.get_available_stocks()
                        if stock_id in available_stocks:
                            download_message = f"Stock {stock_id} is already available in the database."
                        else:
                            # Download data for specified year
                            data_driver.download_database([stock_id], year, force_replace=False)
                            download_message = f"Successfully downloaded data for {stock_id} for year {year}"
                            
                            # Update QA system with new data
                            if qa_system:
                                try:
                                    qa_system.update_data()
                                    print(f"QA system updated with new stock {stock_id}")
                                except Exception as e:
                                    print(f"Error updating QA system: {str(e)}")
                except ValueError:
                    download_message = "Please enter a valid year"
                except Exception as e:
                    download_message = f"Error downloading {stock_id}: {str(e)}"
                
        elif action == 'refresh_data':
            if should_refresh_data():
                # Show refreshing message and redirect to refresh route
                return render_template('index.html',
                                    result=result,
                                    result_type=result_type,
                                    download_message=download_message,
                                    refresh_message="Refreshing data...",
                                    is_refreshing=True,
                                    current_year=current_year)
            else:
                refresh_message = "Data is up to date (less than 2 days old)"
    else:
        # Only show refresh message on GET request if it's from the refresh route
        refresh_message = request.args.get('refresh_message')
    
    return render_template('index.html', 
                         result=result, 
                         result_type=result_type,
                         download_message=download_message,
                         refresh_message=refresh_message,
                         current_year=current_year)

@app.route('/refresh', methods=['GET'])
def refresh():
    try:
        # Get all available stocks
        stocks = data_driver.get_available_stocks()
        if stocks:
            # Download data for current year
            current_year = datetime.now().year
            data_driver.download_database(stocks, current_year, force_replace=True)
            refresh_message = "Data refreshed successfully"
            
            # Update QA system with refreshed data
            if qa_system:
                try:
                    qa_system.update_data()
                    print("QA system updated with refreshed data")
                except Exception as e:
                    print(f"Error updating QA system: {str(e)}")
        else:
            refresh_message = "No stocks available to refresh"
    except Exception as e:
        refresh_message = f"Error refreshing data: {str(e)}"
    
    return redirect(url_for('index', refresh_message=refresh_message))

@app.route('/qa', methods=['GET', 'POST'])
def qa():
    # Ensure QA system is initialized
    initialize_qa_system()
    
    answer = None
    question = None
    
    if request.method == 'POST':
        # Check if we should clear the conversation history
        if request.form.get('clear_history') == 'true':
            if qa_system is not None:
                qa_system.clear_conversation_history()
        else:
            question = request.form.get('question', '').strip()
            if question:
                try:
                    if qa_system is None:
                        answer = "Error: QA system is not available. Please try again later."
                    else:
                        answer = qa_system.ask(question)
                except Exception as e:
                    answer = f"Error processing question: {str(e)}"
    
    # Get conversation history
    conversation_history = []
    if qa_system is not None:
        conversation_history = qa_system.get_conversation_history()
    
    return render_template('qa.html', 
                         question=question,
                         answer=answer,
                         conversation_history=conversation_history)

if __name__ == '__main__':
    app.run(debug=True) 