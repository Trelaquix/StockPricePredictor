# -*- coding: utf-8 -*-
"""Copy of StockPricePredictor.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1fhMN1FjUVBf4TS0RJolxjOkJOpFPzPov
"""

!pip install --upgrade pandas # Upgrade of pandas is necessary to use DataReader
!pip install --upgrade pandas-datareader # Upgrade of pandas-datareader is necessary to use DataReader
from matplotlib import ticker
import pandas as pd
import numpy as np
import math
import pandas_datareader as web
import datetime
from datetime import date
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
import requests
import io
import matplotlib.pyplot as plt
import seaborn as sns
import tensorflow
pd.core.common.is_list_like = pd.api.types.is_list_like
import pandas_datareader
# Set style for plotting
plt.style.use('fivethirtyeight')

# For reading stock data from yahoo
# from pandas_datareader.data import Datareader # pip install pandas_datareader

# Insert Stock data
# ticker = "AAPL"
start = datetime.now() - relativedelta(years=10) # Get date 10 years ago from today
end = date.today()

# Get the stock quote
df = web.DataReader('TSLA', 'yahoo', start, end)
df

plt.figure(figsize=(12,6))
plt.plot(df["Close"], label = 'TSLA Closing Price History')
plt.title('Closing Price History')
plt.xlabel('Date', fontsize=16)
plt.ylabel('Close Price USD ($)', fontsize=16)

# Place moving averages for 10, 30 and 60 days in new columns in the dataframe
ma_day = [10, 30, 60]

for ma in ma_day:
  column_name = f"MA for {ma} days"
  df2 = df
  df2[column_name] = df2['Close'].rolling(ma).mean()

df2

plt.figure(figsize=(12,6))
plt.plot(df["Close"], label='Closing Price')
plt.plot(df["MA for 10 days"], label='10 Day Moving Average')
plt.plot(df["MA for 30 days"], label='30 Day Moving Average')
plt.plot(df["MA for 60 days"], label='60 Day Moving Average')
plt.title("Stock Closing Price and Moving Average")
plt.xlabel('Time')
plt.ylabel('Price')
plt.legend()
plt.show()

# Create training and test dataset
# Create new dataframe with only Close column
data = df.filter(['Close'])

# Convert the dataframe to a numpy array
dataset = data.values

# Get number of rows to train the model on
training_data_len = int(np.ceil(len(dataset)*.7))
training_data_len

# Scale the data
# !pip install sklearn
from sklearn.preprocessing import MinMaxScaler

scaler = MinMaxScaler(feature_range=(0,1))
scaled_data = scaler.fit_transform(dataset)

scaled_data

# Create the training dataset
# Create the scaled training into data set
train_data = scaled_data[0:int(training_data_len), :]
# Split the data into x_train and y_train datasets
x_train = []
y_train = []

for i in range(60, len(train_data)):
  x_train.append(train_data[i-60:i,0])
  y_train.append(train_data[i,0])

# Convert the x_train and y_train to numpy arrays
x_train, y_train = np.array(x_train), np.array(y_train)

# Reshape the data
x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))
# x_train.shape

from keras.models import Sequential
from keras.layers import Dense, Dropout, LSTM

# Build the LSTM model - (Long short-term memory (LSTM) is an artificial recurrent neural network (RNN))
model = Sequential()
#Ver1
# model.add(LSTM(128, return_sequences=True, input_shape=(x_train.shape[1],1)))
# model.add(LSTM(64, return_sequences=False))
# model.add(Dense(25))
# model.add(Dense(1))

#Ver3
model.add(LSTM(50, return_sequences=True, input_shape=(x_train.shape[1],1)))
model.add(LSTM(50, return_sequences=False))
model.add(Dense(25))
model.add(Dense(1))

#Ver5
# model.add(LSTM(units=50, activation = 'relu', return_sequences=True, input_shape=(x_train.shape[1],1)))
# model.add(Dropout(0.2))

# model.add(LSTM(units=60, activation = 'relu', return_sequences=True))
# model.add(Dropout(0.3))

# model.add(LSTM(units=80, activation = 'relu', return_sequences=True))
# model.add(Dropout(0.4))

# model.add(LSTM(units=120, activation = 'relu'))
# model.add(Dropout(0.5))

# model.add(Dense(units=1))


# Compile the model
model.compile(optimizer='adam', loss='mean_squared_error')

# Train the model
model.fit(x_train, y_train, batch_size=1, epochs=1)

# Wait 45 seconds or so for model fit to run, it will spool up at about 20 seconds

# Create the testing dataset
# Create a new array containing scaled values from index 1543 to 2002
test_data = scaled_data[training_data_len - 60: , :]

# Create the data sets x_test and y_test
x_test = []
y_test = dataset[training_data_len:, :]
for i in range(60, len(test_data)):
  x_test.append(test_data[i-60:i, 0])

# Convert the data to a numpy array
x_test = np.array(x_test)

# Reshape the data
x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))

# Get the models predicted price values
predictions = model.predict(x_test)
predictions = scaler.inverse_transform(predictions)

# Get the root mean squared error (RMSE)
rmse = np.sqrt(np.mean(((predictions - y_test) ** 2)))
rmse

mape = np.mean(np.abs((y_test - predictions) / y_test)) * 100
mape

# Remove pandas warning on copy of a slice which is immaterial in this case
pd.options.mode.chained_assignment = None # default='warn'
# Plot the data
train = data[:training_data_len]
valid = data[training_data_len:]
valid['Predictions'] = predictions

# Visualize the data
plt.figure(figsize=(12,6))
plt.title('Stock Price Forecast LSTM Model')
plt.xlabel('Date', fontsize=13)
plt.ylabel('Close Price USD ($)', fontsize=13)
plt.plot(train['Close'])
plt.plot(valid[['Close', 'Predictions']])
plt.legend(['Train', 'Val', 'Predictions'], loc='upper left')
plt.show()

valid

# Try to predict closing price for next closing price

# Get the quote
# df = web.DataReader('TSLA', data_source='yahoo', start='2012-01-01', end='2022-04-12')


# Create a new dataframe
new_df = df.filter(['Close'])
# Get the last 60 days closing price values and convert the dataframe to an array
last_60_days = new_df[-60:].values
# Scale the data to be values between 0 and 1
last_60_days_scaled = scaler.transform(last_60_days)
# Create an empty list
X_test = []
# Append the past 60 days
X_test.append(last_60_days_scaled)
# Convert X_test dataset to a numpy array
X_test = np.array(X_test)
# Reshape the data
X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))
# Get the predicted scaled price
predicted_price = model.predict(X_test)
# Undo the sdcaling
predicted_price = scaler.inverse_transform(predicted_price)
print(predicted_price)

# Get actual price
actual_price = web.DataReader('TSLA', data_source='yahoo', start='2022-04-12', end='2022-04-12')
print(actual_price['Close'])

scaler.scale_

plt.figure(figsize=(12,6))
plt.plot(y_test, 'b', label = 'Original Price')
y_predicted = model.predict(x_test)
scale_factor = 1/0.00081653
y_predict0ed = y_predicted * scale_factor
plt.plot(y_predicted, 'r', label = 'Predicted Price')
plt.xlabel('Time')
plt.ylabel('Price')
plt.legend()
plt.show()