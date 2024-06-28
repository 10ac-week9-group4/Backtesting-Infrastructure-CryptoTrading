import { useEffect, useState } from 'react'
import { PaperClipIcon } from '@heroicons/react/20/solid'

// const results = {
// 	sharpe_ratio: -58.66063557429906,
// 	return: 0.0016255774658640904,
// 	max_drawdown: 0.023526728407521492,
// 	win_trade: 7,
// 	loss_trade: 3,
// 	total_trade: 11,
// 	start_portfolio: 100000,
// 	final_portfolio: 100162.6899433136,
// }

export default function BactestResults({ scene_key, resultsResponse }) {
	const [response, setResponse] = useState(resultsResponse)
	console.log(resultsResponse)
	// console.log(results)

	useEffect(() => {
		console.log(scene_key)
		console.log(resultsResponse)
		setResponse(resultsResponse)
		console.log('INSIDE BACKTEST RESULTS')
	}, [resultsResponse])

	// const listt = Object.entries(results)
	// console.log(listt)

	const displayMessage = () => {
		if (response && response.processing) {
			return (
				<div className="flex items-center justify-center h-96">
					<span className="ml-2 font-semibold text-gray-500">
						Loading results...
					</span>
				</div>
			)
		}
	}

	const renderResults = () => {
		if (response && !response.processing && response.backtest_results) {
			const results = response.backtest_results

      return Object.entries(results).map(([key, value]) => {
        return (
          <div
            key={key}
            className="px-4 py-3 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6"
          >
            <dt className="text-sm font-medium text-gray-900">
              {key.replace(/_/g, ' ')}
            </dt>
            <dd className="mt-1 text-sm leading-6 text-gray-700 sm:col-span-2 sm:mt-0">
              {value}
            </dd>
          </div>
        )
      })
		}
	}

	return (
		<div className="overflow-hidden bg-white shadow sm:rounded-lg">
			<div className="px-4 py-6 sm:px-6">
				<h3 className="text-base font-semibold leading-7 text-gray-900">
					Backtest Results
				</h3>
				<p className="mt-1 max-w-2xl text-sm leading-6 text-gray-500">
					The backtest results with various metrics will be displayed here.
				</p>
			</div>
			{displayMessage()}
			<div className="border-t border-gray-100">
				<dl className="divide-y divide-gray-100">{renderResults()}</dl>
			</div>
		</div>
	)
}
