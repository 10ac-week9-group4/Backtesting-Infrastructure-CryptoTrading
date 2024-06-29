import { PhotoIcon, UserCircleIcon } from '@heroicons/react/24/solid'

const strategyOptions = [
	{
		id: 1,
		strategyName: 'SMACrossover',
		description:
			'This strategy uses a simple moving average crossover to determine when to buy and sell assets. It uses two moving averages, a short window and a long window. When the short window crosses above the long window, it generates a buy signal. When the short window crosses below the long window, it generates a sell signal.',
		parametersNames: ['shortWindow', 'longWindow'],
	},
	{
		id: 2,
		strategyName: 'RSI',
		description:
			'This strategy uses the Relative Strength Index (RSI) to determine when to buy and sell assets. The RSI is a momentum oscillator that measures the speed and change of price movements. When the RSI is above 70, it is considered overbought and generates a sell signal. When the RSI is below 30, it is considered oversold and generates a buy signal.',
		parametersNames: ['overboughtThreshold', 'oversoldThreshold'],
	},
	{
		id: 3,
		strategyName: 'MACD',
		description:
			'This strategy uses the Moving Average Convergence Divergence (MACD) to determine when to buy and sell assets. The MACD is a trend-following momentum indicator that shows the relationship between two moving averages of a security’s price. When the MACD line crosses above the signal line, it generates a buy signal. When the MACD line crosses below the signal line, it generates a sell signal.',
		parametersNames: ['shortWindow', 'longWindow', 'signalWindow'],
	},
]

export default function BacktestForm() {
	return (
		<form>
			<div className="border-b border-gray-900/10 pb-12">
				<h2 className="text-base font-semibold leading-7 text-gray-900">
					Backtest a strategy
				</h2>
				<p className="mt-1 text-sm leading-6 text-gray-600">
					This page allows you to backtest a strategy using historical data.
				</p>
			</div>

			<div className="mt-10 grid-rows-2">
				<div className="mt-10 grid grid-cols-1 gap-x-6 gap-y-8 sm:grid-cols-6 row-span-2">
					<div className="sm:col-span-2">
						<label
							htmlFor="country"
							className="block text-sm font-medium leading-6 text-gray-900"
						>
							Symbol
						</label>
						<div className="mt-2">
							<select
								id="country"
								name="country"
								autoComplete="country-name"
								className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:max-w-xs sm:text-sm sm:leading-6"
							>
								<option>United States</option>
								<option>Canada</option>
								<option>Mexico</option>
							</select>
						</div>
					</div>

					<div className="sm:col-span-2 sm:col-start-1">
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
								className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:max-w-xs sm:text-sm sm:leading-6"
							>
								<option>United States</option>
								<option>Canada</option>
								<option>Mexico</option>
							</select>
						</div>
					</div>

					<div className="sm:col-span-1 sm:col-start-1">
						<label
							htmlFor="city"
							className="block text-sm font-medium leading-6 text-gray-900"
						>
							City
						</label>
						<div className="mt-2">
							<input
								type="text"
								name="city"
								id="city"
								autoComplete="address-level2"
								className="block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-indigo-600 sm:text-sm sm:leading-6"
							/>
						</div>
					</div>
				</div>

				<div className="mt-6 sm:row-span-2">
					<div className="sm:col-span-3 relative">
						<p className="block mt-1 text-sm leading-6 text-gray-600">
							This strategy uses a simple moving average crossover to determine
							when to buy and sell assets. It uses two moving averages, a short
							window and a long window. When the short window crosses above the
							long window, it generates a buy signal. When the short window
							crosses below the long window, it generates a sell signal.
						</p>
					</div>
				</div>
			</div>

			<div className="mt-6 flex items-center justify-start gap-x-6">
				<button
					type="button"
					className="text-sm font-semibold leading-6 text-gray-900"
				>
					Cancel
				</button>
				<button
					type="submit"
					className="rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
				>
					Run backt
				</button>
			</div>
		</form>
	)
}
