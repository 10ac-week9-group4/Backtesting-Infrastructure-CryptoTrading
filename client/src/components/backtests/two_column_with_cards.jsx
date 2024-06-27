/*
  This example requires some changes to your config:
  
  ```
  // tailwind.config.js
  module.exports = {
    // ...
    plugins: [
      // ...
      require('@tailwindcss/forms'),
    ],
  }
  ```
*/
import { PhotoIcon, UserCircleIcon } from '@heroicons/react/24/solid'

export default function Example() {
	return (
		<div className="space-y-10 divide-y divide-gray-900/10">
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
			<div className="grid grid-cols-1 gap-x-8 gap-y-8 md:grid-cols-5">
				<form className="bg-white shadow-sm ring-1 ring-gray-900/5 sm:rounded-xl md:col-span-2">
					<div className="px-4 py-6 sm:p-8">
						<div className="grid max-w-2xl grid-cols-1 gap-x-6 gap-y-8 sm:grid-cols-6">
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
					</div>
					<div className="flex items-center justify-start gap-x-6 border-t border-gray-900/10 px-4 py-4 sm:px-8">
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
							Run Backtests
						</button>
					</div>
				</form>

				<div className="mt-5 px-4 sm:px-0 sm:col-span-2">
					<h2 className="text-base font-semibold leading-7 text-gray-900">
						Description
					</h2>
					<p className="mt-1 text-sm leading-6 text-gray-600">
						This strategy uses a simple moving average crossover to determine
						when to buy and sell assets. It uses two moving averages, a short
						window and a long window. When the short window crosses above the
						long window, it generates a buy signal. When the short window
						crosses below the long window, it generates a sell signal.{' '}
					</p>
				</div>
			</div>
		</div>
	)
}
