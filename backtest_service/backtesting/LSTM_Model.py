import pandas as pd
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
from datetime import date
import yfinance as yf
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.layers import Dense, Dropout, LSTM
from tensorflow.keras.models import Sequential

# Global variables
START = "2020-01-01"
TODAY = date.today().strftime("%Y-%m-%d")

def load_data(ticker, start_date=START, end_date=TODAY):
    data = yf.download(ticker, start_date, end_date)
    data.reset_index(inplace=True)
    return data

def prepare_data(df, train_size=0.7):
    # Drop unnecessary columns
    df = df.drop(['Date', 'Adj Close'], axis=1)
    
    # Scale data using MinMaxScaler
    scaler = MinMaxScaler(feature_range=(0, 1))
    data_scaled = scaler.fit_transform(df.values)
    
    # Prepare training data
    x_train, y_train = [], []
    for i in range(100, data_scaled.shape[0]):
        x_train.append(data_scaled[i-100:i])
        y_train.append(data_scaled[i, 0])
    
    x_train, y_train = np.array(x_train), np.array(y_train)
    
    # Split data into training and testing sets
    split_index = int(train_size * len(data_scaled))
    x_test, y_test = data_scaled[split_index:], df.iloc[split_index:, 4:5].values
    
    return x_train, y_train, x_test, y_test, scaler

def build_lstm_model(input_shape):
    """
    Function to build an LSTM model using Keras Sequential API.

    Parameters:
    - input_shape (tuple): Shape of input data (number of time steps, number of features).

    Returns:
    - Sequential: Compiled LSTM model.
    """
    model = Sequential()
    model.add(LSTM(128, return_sequences=True, input_shape=input_shape))
    model.add(Dropout(0.2))
    model.add(LSTM(64, return_sequences=False))
    model.add(Dropout(0.2))
    model.add(Dense(1, activation="linear"))
    
    model.compile(optimizer='adam', loss='mean_squared_error', metrics=[tf.keras.metrics.MeanAbsoluteError()])
    
    return model

def train_model(model, x_train, y_train, epochs=50, batch_size=32):
    """
    Function to train an LSTM model.

    Parameters:
    - model (Sequential): Compiled LSTM model.
    - x_train (ndarray): Input training data.
    - y_train (ndarray): Target training data.
    - epochs (int): Number of epochs for training (default: 50).
    - batch_size (int): Batch size for training (default: 32).

    Returns:
    - None
    """
    model.fit(x_train, y_train, batch_size=batch_size, epochs=epochs)

def predict_and_plot(model, x_test, y_test, scaler):
    
    # Make predictions
    y_pred = model.predict(x_test)
    
    # Inverse transform predictions and actual values
    scaling_factor = scaler.scale_[0]
    y_pred = y_pred * scaling_factor
    y_test = y_test * scaling_factor
    
    # Plotting results
    plt.figure(figsize=(12, 6))
    plt.plot(y_test, 'b', label="Original Price")
    plt.plot(y_pred, 'r', label="Predicted Price")
    plt.xlabel('Time')
    plt.ylabel('Price')
    plt.legend()
    plt.grid(True)
    plt.show()

def main():
    # Load data
    ticker = 'BTC-USD'
    df = load_data(ticker)
    
    # Prepare data
    x_train, y_train, x_test, y_test, scaler = prepare_data(df)
    
    # Build LSTM model
    input_shape = (x_train.shape[1], x_train.shape[2])  # Shape of input data for LSTM
    model = build_lstm_model(input_shape)
    
    # Train model
    train_model(model, x_train, y_train)
    
    # Predict and plot results
    predict_and_plot(model, x_test, y_test, scaler)

if __name__ == "__main__":
    main()
