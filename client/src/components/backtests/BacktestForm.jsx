import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

import BactestResults from "./BacktestResults";

const strategies = [
	{
    "name": "SMACrossOver",
		"full_name": "SMA Crossover",
    "parameters": {
      "pfast": "Short Window",
      "pslow": "Long Window",
      // "interval": "interval"
    },
    "description": "This strategy uses a simple moving average crossover to determine when to buy and sell assets. It uses two moving averages, a short window and a long window. When the short window crosses above the long window, it generates a buy signal. When the short window crosses below the long window, it generates a sell signal."
  },
	{
		"name": "MACDCrossover",
		"full_name": "MACD Crossover",
		"parameters": {
			"fastperiod": "Short Window",
			"slowperiod": "Long Window",
			"signalperiod": "Signal Window"
		},
		"description": "This strategy uses a MACD crossover to determine when to buy and sell assets. It uses three moving averages, a short window, a long window, and a signal window. When the MACD line crosses above the signal line, it generates a buy signal. When the MACD line crosses below the signal line, it generates a sell signal."
	},
	{
		"name": "BollingerBands",

		"parameters": {
			"period": "Window",
			"devfactor": "Standard Deviation"
		},
		"description": "This strategy uses Bollinger Bands to determine when to buy and sell assets. It uses a moving average and a standard deviation to calculate the upper and lower bands. When the price crosses below the lower band, it generates a buy signal. When the price crosses above the upper band, it generates a sell signal."
	}

]

const renderParameterFields = (strategy) => {
	const fields = []
	for (const [key, value] of Object.entries(strategy.parameters)) {
		// console.log(key, value)
		fields.push(
			<div key={key} className="sm:col-span-3">
				<label
					htmlFor={key}
					className="block text-sm font-medium leading-6 text-gray-900"
				>
					Parameter: {value}
				</label>
				<div className="mt-2">
					<input
						type="text"
						name={key}
						id={key}
						autoComplete="address-level2"
						className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
					/>
				</div>
			</div>
		)
	}
	return fields
}


export default function BacktestForm() {
	const [scene_key, setSceneKey] = useState("")
	const [message, setMessage] = useState("")
	const [strategy, setStrategy] = useState(strategies[0].name)
	const [resultsResponse, setResultsResponse] = useState({})
	const navigate = useNavigate()
	const handleSubmit = async (e) => {
		e.preventDefault()
		setResultsResponse({})
		// get form data using FormData
		const formData = new FormData(e.target)
		const data = {}
		for (let [key, value] of formData.entries()) {
			data[key] = value
		}
		console.log(data)
		console.log(e.target.symbol.value)
		console.log("Form submitted")

		// get the parameters in one object under key parameters
		const parameters = {}
		// and convert the parameter values to integers
		for (const [key, value] of Object.entries(data)) {
			if (key !== "symbol" && key !== "country" && key !== "start_date" && key !== "end_date" && key !== "cash" && key !== "commission") {
				parameters[key] = parseInt(value)
			}
		}

	

		const backtestData = {
			asset: data.symbol,
			strategy: strategies[0].name,
			parameters: parameters,
			start_date: data.start_date,
			end_date: data.end_date,
			cash: data.cash,
			commission: data.commission
		}


		// send the data to the backend
		try {
			const response = await axios.post("http://localhost:8089/backtest_scene", backtestData)
			
			// console.log(response.data)

			if (response.status === 200) {
				console.log("Backtest successful")
				setSceneKey(response.data.scene_key)
				// fetch the backtest results
				const backtest_res = await axios.get(`http://localhost:8089/backtest_results/${response.data.scene_key}`)

				console.log(backtest_res.data)
				// console.log("HELLO")
				setMessage(backtest_res.data.message)

				// navigate to the backtest results page
				

				// navigate(`/backtests/${response.data.scene_key}`)
			}
		} catch (error) {
			console.error(error)
		}
	}

	const [assets, setAssets] = useState([]);
	const fetch_assets = async () => {
		try {
			const response = await axios.get("http://localhost:8089/assets")
			setAssets(response.data.assets)
			// console.log(response.data.assets)
		} catch (error) {
			console.error(error)
		}
	}

	const handleCheckResults = async () => {
		console.log("Checking results")
		try {
			const response = await axios.get(`http://localhost:8089/get_results/${scene_key}`)
			console.log(response.data)

			setResultsResponse(response.data)
			setMessage(response.data.message)
		} catch (error) {
			console.error(error)
		}
	}
	console.log(strategy)

	useEffect(() => {
		fetch_assets()
	}, [])

	return (
		<div className="space-y-10">
			<div className="mt-2 sm:row-span-2">
				<div className="sm:col-span-3 relative">
					<h2 className="text-base font-semibold leading-7 text-gray-900">
						Backtest a strategy
					</h2>
					<p className="mt-1 text-sm leading-6 text-gray-600">
						This page allows you to backtest a strategy using historical data.
					</p>
				</div>
			</div>
			<div className="grid grid-cols-1 gap-x-8 gap-y-8 md:grid-cols-2">
				<form onSubmit={handleSubmit} className="bg-white shadow-sm ring-1 ring-gray-900/5 sm:rounded-xl md:col-span-1">
					<div className="px-4 py-6 sm:p-8">
						<div className="grid max-w-2xl grid-cols-1 gap-x-6 gap-y-8 sm:grid-cols-6">
							<div className="sm:col-span-3">
								<label
									htmlFor="symbol"
									className="block text-sm font-medium leading-6 text-gray-900"
								>
									Asset
								</label>
								<div className="mt-2">
									<select
										id="symbol"
										name="symbol"
										autoComplete="symbol"
										className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:max-w-xs sm:text-sm sm:leading-6"
									>
										{
											assets.map(asset => (
												<option key={asset.TickerSymbol} value={asset.TickerSymbol}>{asset.TickerSymbol} {" "} ({asset.AssetName})</option>
											))
										}
									</select>
								</div>
							</div>

							<div className="sm:col-span-3">
								<label
									htmlFor="country"
									className="block text-sm font-medium leading-6 text-gray-900"
								>
									Strategy
								</label>
								<div className="mt-2">
									<select
										id="country"
										name="country"
										autoComplete="country-name"
										onChange={(e) => setStrategy(e.target.value) }
										className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:max-w-xs sm:text-sm sm:leading-6"
									>
										{
											strategies.map(strategy => (
												<option key={strategy.name} value={strategy.name}>{strategy.name}</option>
											))
										}
									</select>
								</div>
							</div>

							<div className="sm:col-span-3">
								<label
									htmlFor="start_date"
									className="block text-sm font-medium leading-6 text-gray-900"
								>
									Start Date
								</label>
								<div className="mt-2">
									<input
										type="date"
										name="start_date"
										id="start_date"
										autoComplete="address-level2"
										className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
									/>
								</div>
							</div>

              <div className="sm:col-span-3">
								<label
									htmlFor="end_date"
									className="block text-sm font-medium leading-6 text-gray-900"
								>
									End Date
								</label>
								<div className="mt-2">
									<input
										type="text"
										name="end_date"
										id="end_date"
										autoComplete="address-level2"
										className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
									/>
								</div>
							</div>

              <div className="sm:col-span-3 sm:col-start-1">
								<label
									htmlFor="cash"
									className="block text-sm font-medium leading-6 text-gray-900"
								>
									Cash
								</label>
								<div className="mt-2">
									<input
										type="text"
										name="cash"
										id="cash"
										autoComplete="address-level2"
										className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
									/>
								</div>
							</div>

              <div className="sm:col-span-3">
								<label
									htmlFor="commission"
									className="block text-sm font-medium leading-6 text-gray-900"
								>
									Commission
								</label>
								<div className="mt-2">
									<input
										type="text"
										name="commission"
										id="commission"
										autoComplete="address-level2"
										className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
									/>
								</div>
							</div>

              {
								renderParameterFields(strategies.find(s => s.name === strategy))
							}

						</div>
					</div>
					<div className="flex items-center justify-start gap-x-6 border-t border-gray-900/10 px-4 py-4 sm:px-8">
						<button
							type="button"
							className="text-sm font-semibold leading-6 text-gray-900"
						>
							Clear
						</button>
						<button
							type="submit"
							className="rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
						>
							Run Backtests
						</button>
					</div>
					
					
				</form>
				


				<div >
				{
						scene_key && !resultsResponse.backtest_results && (
						<div className="px-4 sm:p-3 flex">
							<button
							onClick={handleCheckResults}
							className="rounded-md bg-teal-500 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
						>
							Check Results
						</button>
						<p className="pl-2 mt-1 text-sm leading-6 text-gray-600">
							{message}
						</p>
						
					</div>
						)
					}
					<BactestResults scene_key={scene_key} resultsResponse={resultsResponse} />

				</div>
			</div>
			

			
		</div>
	)
}
