import pandas as pd
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain.agents.types import AgentType
from langchain_core.callbacks import CallbackManager
from langchain_community.callbacks import get_openai_callback
import os
from dotenv import load_dotenv
import json
import logging
import re
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from typing import List, Dict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Rich console
console = Console()

# Load environment variables
load_dotenv()

class StockQASystem:
    def __init__(self, data_driver, model_type: str = "gemini"):
        """
        Initialize the Stock QA System.
        
        Args:
            data_driver: The DataDriver instance to access stock data
            model_type (str): The type of model to use ("openai" or "gemini")
        """
        self.data_driver = data_driver
        self.model_type = model_type.lower()
        self.conversation_history: List[Dict[str, str]] = []
        
        # Load initial data
        try:
            # Get available stocks from data_driver
            available_stocks = data_driver.get_available_stocks()
            if not available_stocks:
                raise ValueError("No stocks available in the data driver")
            
            # Get data for available stocks from current year
            current_year = pd.Timestamp.now().year
            data = data_driver.get_multiple_stocks_data(available_stocks, current_year)
            self.price_data = data["Close"]
            
            # Initialize the language model
            if self.model_type == "openai":
                self.llm = ChatOpenAI(temperature=0)
                self.agent_type = AgentType.OPENAI_FUNCTIONS
            else:  # default to gemini
                self.llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)
                self.agent_type = AgentType.ZERO_SHOT_REACT_DESCRIPTION
            # Create the agent with security settings
            self.agent = create_pandas_dataframe_agent(
                self.llm,
                self.price_data,
                verbose=True,
                agent_type=self.agent_type,
                allow_dangerous_code=True,  # Required for pandas operations
                max_iterations=30,  # Limit the number of iterations
                handle_parsing_errors=True,  # Handle parsing errors gracefully
            )
            
            logger.info(f"StockQASystem initialized successfully with {len(available_stocks)} stocks")
            
        except Exception as e:
            logger.error(f"Error initializing StockQASystem: {str(e)}")
            raise
    
    def ask(self, question: str) -> str:
        """
        Process a question about the stock data.
        
        Args:
            question (str): The question to process
            
        Returns:
            str: The answer to the question
        """
        try:
            # Add context to the question
            context = "You are a helpful assistant analyzing stock market data. "
            context += "The data provided is in a pandas DataFrame with stock prices. "
            context += "Please provide clear and concise answers based on the data. "
            context += "If you need to perform calculations, explain your reasoning. "
            
            full_question = f"{context}\n\nQuestion: {question}"
            
            # Process the question using the agent
            response = self.agent.run(full_question)
            
            # Add to conversation history
            self.conversation_history.append({
                "question": question,
                "answer": response
            })
            
            return response
        except Exception as e:
            error_msg = f"Sorry, I encountered an error while processing your question: {str(e)}"
            logger.error(f"Error processing question: {str(e)}")
            
            # Add error to conversation history
            self.conversation_history.append({
                "question": question,
                "answer": error_msg
            })
            
            return error_msg
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """
        Get the conversation history.
        
        Returns:
            List[Dict[str, str]]: List of conversation entries with questions and answers
        """
        return self.conversation_history
    
    def clear_conversation_history(self):
        """
        Clear the conversation history.
        """
        self.conversation_history = []
    
    def update_data(self, stocks: list = None, year: int = None):
        """
        Update the data used by the QA system.
        
        Args:
            stocks (list): List of stock symbols to include. If None, uses all available stocks
            year (int): Year of data to load. If None, uses current year
        """
        try:
            if stocks is None:
                stocks = self.data_driver.get_available_stocks()
                if not stocks:
                    raise ValueError("No stocks available in the data driver")
            
            if year is None:
                year = pd.Timestamp.now().year
                
            data = self.data_driver.get_multiple_stocks_data(stocks, year)
            self.price_data = data["Close"]
            
            # Recreate the agent with new data
            self.agent = create_pandas_dataframe_agent(
                self.llm,
                self.price_data,
                verbose=True,
                agent_type=AgentType.OPENAI_FUNCTIONS,
                allow_dangerous_code=True,
                max_iterations=3,
                handle_parsing_errors=True,
            )
            
            logger.info(f"Data updated successfully for {len(stocks)} stocks and year {year}")
            
        except Exception as e:
            logger.error(f"Error updating data: {str(e)}")
            raise

def main():
    # Example usage
    from datadriver.data_processing import read_stocks
    
    # Read the stock data
    stocks = ['ACB', 'BAB', 'BBS', 'BCM', 'BID']  # Example stocks
    data = read_stocks(stocks, 2025)
    
    # Initialize the QA system with Gemini
    qa_system = StockQASystem(data, model_type="gemini")
    
    # Example questions
    example_questions = [
        "What was the highest closing price for each stock?",
        "Which stock had the highest trading volume?",
        "What was the average daily return for each stock?",
        "Show me the price trend for BID over time",
        "What was the price range (high-low) for ACB on its most volatile day?",
        "Which stock had the most consistent closing prices (lowest standard deviation)?"
    ]
    
    console.print(Panel.fit(
        "[bold green]Welcome to the Stock Data Question Answering System![/bold green]\n\n"
        "You can ask questions about the stock data. Type 'quit' to exit.\n\n"
        "[bold yellow]Example questions:[/bold yellow]",
        title="Stock QA System",
        border_style="blue"
    ))
    
    for q in example_questions:
        console.print(f"- [cyan]{q}[/cyan]")
    
    while True:
        question = console.input("\n[bold green]Enter your question:[/bold green] ")
        if question.lower() == 'quit':
            break
            
        answer = qa_system.ask(question)

if __name__ == "__main__":
    main() 