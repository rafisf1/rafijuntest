import pandas as pd
import logging
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import numpy as np
import joblib

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def prepare_features(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series, pd.Series]:
    """
    Prepare features and targets for model training.
    
    Args:
        df (pd.DataFrame): Input DataFrame
        
    Returns:
        tuple: (X, y_price, y_dom) where X is the feature matrix and y's are the target variables
    """
    # Select features for the model (excluding price_sold and days_on_market)
    feature_columns = [col for col in df.columns 
                      if col not in ['price_sold', 'days_on_market']]
    
    X = df[feature_columns]
    y_price = df['price_sold']
    y_dom = df['days_on_market']
    
    logger.info(f"Selected {len(feature_columns)} features for the models")
    return X, y_price, y_dom

def train_models(X: pd.DataFrame, y_price: pd.Series, y_dom: pd.Series) -> tuple[RandomForestRegressor, RandomForestRegressor, dict]:
    """
    Train Random Forest models for both price and days on market prediction.
    
    Args:
        X (pd.DataFrame): Feature matrix
        y_price (pd.Series): Price target variable
        y_dom (pd.Series): Days on market target variable
        
    Returns:
        tuple: (price_model, dom_model, metrics)
    """
    # Split the data
    X_train, X_test, y_price_train, y_price_test, y_dom_train, y_dom_test = train_test_split(
        X, y_price, y_dom, test_size=0.2, random_state=42
    )
    
    # Initialize and train the price model
    price_model = RandomForestRegressor(n_estimators=100, random_state=42)
    price_model.fit(X_train, y_price_train)
    
    # Initialize and train the DOM model
    dom_model = RandomForestRegressor(n_estimators=100, random_state=42)
    dom_model.fit(X_train, y_dom_train)
    
    # Make predictions
    price_preds = price_model.predict(X_test)
    dom_preds = dom_model.predict(X_test)
    
    # Calculate metrics
    metrics = {
        'price': {
            'mse': mean_squared_error(y_price_test, price_preds),
            'rmse': np.sqrt(mean_squared_error(y_price_test, price_preds)),
            'mae': mean_absolute_error(y_price_test, price_preds),
            'r2': r2_score(y_price_test, price_preds)
        },
        'dom': {
            'mse': mean_squared_error(y_dom_test, dom_preds),
            'rmse': np.sqrt(mean_squared_error(y_dom_test, dom_preds)),
            'mae': mean_absolute_error(y_dom_test, dom_preds),
            'r2': r2_score(y_dom_test, dom_preds)
        }
    }
    
    # Log feature importance for both models
    for model_name, model in [('Price', price_model), ('DOM', dom_model)]:
        feature_importance = pd.DataFrame({
            'feature': X.columns,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        logger.info(f"\nTop 5 most important features for {model_name} prediction:")
        logger.info(feature_importance.head())
    
    return price_model, dom_model, metrics, X.columns

def process_real_estate_data(file_path: str) -> pd.DataFrame:
    """
    Process real estate data from CSV file.
    
    Args:
        file_path (str): Path to the CSV file
        
    Returns:
        pd.DataFrame: Processed DataFrame
    """
    try:
        # Read the CSV file
        logger.info(f"Reading data from {file_path}")
        df = pd.read_csv(file_path)
        
        # Log initial data shape
        logger.info(f"Initial data shape: {df.shape}")
        
        # Drop missing values
        df = df.dropna()
        logger.info(f"Shape after dropping missing values: {df.shape}")
        
        # Remove extreme outliers (properties sold for more than $10M)
        df = df[df["price_sold"] < 10_000_000]
        logger.info(f"Shape after removing price outliers: {df.shape}")
        
        # One-hot encode zipcode column
        logger.info("Performing one-hot encoding on zipcode column")
        original_columns = df.columns.tolist()
        df = pd.get_dummies(df, columns=["zipcode"], drop_first=True)
        new_columns = [col for col in df.columns if col not in original_columns]
        logger.info(f"Added {len(new_columns)} new columns for zipcode encoding")
        logger.info(f"Final data shape: {df.shape}")
        
        return df
        
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise
    except pd.errors.EmptyDataError:
        logger.error("The CSV file is empty")
        raise
    except KeyError:
        logger.error("Required column 'zipcode' not found in the data")
        raise
    except Exception as e:
        logger.error(f"An error occurred while processing the data: {str(e)}")
        raise

if __name__ == "__main__":
    # Define the path to your CSV file
    data_path = Path("data/la_real_estate.csv")
    
    try:
        # Process the data
        df = process_real_estate_data(str(data_path))
        
        # Display basic statistics
        print("\nBasic statistics of the processed data:")
        print(df.describe())
        
        # Display the new columns created from one-hot encoding
        zipcode_columns = [col for col in df.columns if col.startswith('zipcode_')]
        print(f"\nNumber of zipcode columns created: {len(zipcode_columns)}")
        print("First few zipcode columns:", zipcode_columns[:5])
        
        # Prepare features and train models
        X, y_price, y_dom = prepare_features(df)
        price_model, dom_model, metrics, feature_names = train_models(X, y_price, y_dom)
        
        # Save models and feature names
        models_dir = Path("models")
        models_dir.mkdir(exist_ok=True)
        
        joblib.dump(price_model, models_dir / "price_model.joblib")
        joblib.dump(dom_model, models_dir / "dom_model.joblib")
        joblib.dump(feature_names, models_dir / "feature_names.joblib")
        
        print("\nModels saved to 'models' directory")
        
        # Display model performance metrics
        print("\nPrice Model Performance Metrics:")
        print(f"Mean Squared Error: ${metrics['price']['mse']:,.2f}")
        print(f"Root Mean Squared Error: ${metrics['price']['rmse']:,.2f}")
        print(f"Mean Absolute Error: ${metrics['price']['mae']:,.2f}")
        print(f"R² Score: {metrics['price']['r2']:.4f}")
        
        print("\nDays on Market Model Performance Metrics:")
        print(f"Mean Squared Error: {metrics['dom']['mse']:.2f} days")
        print(f"Root Mean Squared Error: {metrics['dom']['rmse']:.2f} days")
        print(f"Mean Absolute Error: {metrics['dom']['mae']:.2f} days")
        print(f"R² Score: {metrics['dom']['r2']:.4f}")
        
    except Exception as e:
        logger.error(f"Failed to process data: {str(e)}") 