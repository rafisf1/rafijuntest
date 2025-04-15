import pandas as pd
import numpy as np
from pathlib import Path

def generate_sample_data(n_samples: int = 1000) -> pd.DataFrame:
    """
    Generate sample real estate data with realistic values.
    
    Args:
        n_samples (int): Number of samples to generate
        
    Returns:
        pd.DataFrame: Generated sample data
    """
    # Set random seed for reproducibility
    np.random.seed(42)
    
    # Generate sample data
    data = {
        'price_sold': np.random.lognormal(mean=13, sigma=0.5, size=n_samples),  # Most prices between 100k and 2M
        'days_on_market': np.random.lognormal(mean=3.5, sigma=0.5, size=n_samples),  # Most DOM between 10 and 60 days
        'zipcode': np.random.choice([
            '90001', '90002', '90003', '90004', '90005',  # Downtown LA
            '90006', '90007', '90008', '90010', '90011',  # South LA
            '90012', '90013', '90014', '90015', '90016',  # Central LA
            '90017', '90018', '90019', '90020', '90021',  # Mid-City
            '90022', '90023', '90024', '90025', '90026',  # West LA
            '90027', '90028', '90029', '90030', '90031',  # East LA
            '90032', '90033', '90034', '90035', '90036',  # Mid-Wilshire
            '90037', '90038', '90039', '90040', '90041',  # Northeast LA
            '90042', '90043', '90044', '90045', '90046',  # South Central
            '90047', '90048', '90049', '90050', '90051'   # Westside
        ], size=n_samples),
        'bedrooms': np.random.choice([1, 2, 3, 4, 5], size=n_samples, p=[0.1, 0.3, 0.4, 0.15, 0.05]),
        'bathrooms': np.random.choice([1, 1.5, 2, 2.5, 3, 3.5, 4], size=n_samples, p=[0.1, 0.2, 0.3, 0.2, 0.1, 0.05, 0.05]),
        'square_feet': np.random.lognormal(mean=7, sigma=0.3, size=n_samples),  # Most between 800 and 3000 sq ft
        'year_built': np.random.randint(1900, 2024, size=n_samples),
        'lot_size': np.random.lognormal(mean=7, sigma=0.5, size=n_samples),  # Most between 4000 and 10000 sq ft
        'property_type': np.random.choice(['Single Family', 'Condo', 'Townhouse'], size=n_samples, p=[0.6, 0.3, 0.1]),
        'has_pool': np.random.choice([0, 1], size=n_samples, p=[0.7, 0.3]),
        'has_garage': np.random.choice([0, 1], size=n_samples, p=[0.2, 0.8]),
        'has_central_air': np.random.choice([0, 1], size=n_samples, p=[0.1, 0.9]),
        'has_fireplace': np.random.choice([0, 1], size=n_samples, p=[0.4, 0.6])
    }
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Round numeric columns to reasonable values
    df['price_sold'] = df['price_sold'].round(0)
    df['days_on_market'] = df['days_on_market'].round(0)
    df['square_feet'] = df['square_feet'].round(0)
    df['lot_size'] = df['lot_size'].round(0)
    df['bathrooms'] = df['bathrooms'].round(1)
    
    # Add some missing values randomly (about 5% of the data)
    mask = np.random.random(n_samples) < 0.05
    for col in df.columns:
        if col not in ['zipcode', 'property_type']:  # Don't add missing values to categorical columns
            df.loc[mask, col] = np.nan
    
    return df

if __name__ == "__main__":
    # Create data directory if it doesn't exist
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Generate sample data
    print("Generating sample real estate data...")
    df = generate_sample_data(n_samples=1000)
    
    # Save to CSV
    output_path = data_dir / "la_real_estate.csv"
    df.to_csv(output_path, index=False)
    
    print(f"\nSample data has been generated and saved to: {output_path}")
    print("\nData Preview:")
    print(df.head())
    print("\nData Info:")
    print(df.info())
    print("\nBasic Statistics:")
    print(df.describe()) 