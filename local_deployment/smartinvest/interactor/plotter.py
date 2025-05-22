import matplotlib
matplotlib.use('Agg')  # Set the backend to Agg before importing pyplot
import matplotlib.pyplot as plt
import base64
from io import BytesIO
from typing import Optional

class StockPlotter:
    """
    A class to handle stock data visualization.
    """
    
    @staticmethod
    def plot_stock_data(df, stock_id: str) -> Optional[str]:
        """
        Plot stock data and return the plot as a base64 encoded image.
        
        Args:
            df: DataFrame containing stock data
            stock_id: Stock identifier
            
        Returns:
            str: Base64 encoded image string if successful, None otherwise
        """
        if df is None or df.empty:
            return None
            
        try:
            # Create the plot
            plt.figure(figsize=(12, 6))
            plt.plot(df.index, df['Close'], label='Close Price')
            plt.title(f'{stock_id} Stock Price')
            plt.xlabel('Date')
            plt.ylabel('Price (VND)')
            plt.grid(True)
            plt.legend()
            
            # Save plot to a bytes buffer
            buffer = BytesIO()
            plt.savefig(buffer, format='png', bbox_inches='tight', dpi=100)
            buffer.seek(0)
            
            # Convert to base64 for HTML display
            chart_image = base64.b64encode(buffer.getvalue()).decode('utf-8')
            plt.close()
            
            return chart_image
            
        except Exception as e:
            print(f"Error plotting stock data: {str(e)}")
            return None 