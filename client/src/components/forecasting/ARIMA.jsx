import React, { useState, useEffect } from 'react';
import yfinance as yf;
import { Line } from 'react-chartjs-2';
import { DateTime } from 'luxon';
import statsmodels.api as sm

function ForecastingUI() {
  const [chartData, setChartData] = useState(null);

  useEffect(() => {
    const fetchDataAndForecast = async () => {
      const ticker = 'AAPL';
      const startDate = DateTime.now().minus({ years: 1 }).toISODate();
      const endDate = DateTime.now().toISODate();
      const forecastHorizon = 5;

      const data = await yf.download(ticker, start=startDate, end=endDate);
      const tsData = data['Adj Close'];
      const trainData = tsData.iloc[:-forecastHorizon];
      
      // ARIMA Model Fitting
      const model = sm.tsa.ARIMA(trainData, order=(5, 1, 0)); // Example ARIMA(5,1,0) model
      const modelFit = model.fit();

      // Forecasting
      const forecast = modelFit.forecast(steps=forecastHorizon);
      const forecastDates = Array.from({ length: forecastHorizon }, (_, i) =>
        DateTime.fromJSDate(trainData.index.max()).plus({ days: i + 1 }).toISODate()
      );

      // Prepare Chart Data
      setChartData({
        labels: [...trainData.index.map(date => date.toISOString().slice(0, 10)), ...forecastDates],
        datasets: [
          { label: 'Actual', data: tsData.values, fill: false, borderColor: 'blue' },
          { label: 'Forecast', data: [...trainData.values, ...forecast], fill: false, borderColor: 'red' }
        ]
      });
    };

    fetchDataAndForecast();
  }, []); 

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">AAPL Stock Price Forecast</h1>
      {chartData && <Line data={chartData} />}
    </div>
  );
}
