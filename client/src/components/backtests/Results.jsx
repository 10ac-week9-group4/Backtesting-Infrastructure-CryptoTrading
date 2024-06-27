import React, { useState, useEffect } from 'react';

function Results({ sceneId }) {
  const [results, setResults] = useState({}); // Store the backtest results
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    console.log(sceneId)
    const eventSource = new EventSource(`http://localhost:8089/backtest_results/${sceneId}`);
    // console.log(eventSource)
    
    eventSource.onmessage = (event) => {
      const newResult = JSON.parse(event.data);
      setResults(newResult); 
      setIsLoading(false); 
      console.log(newResult)
      eventSource.onmessage = (event) => {
        if (event.data === "No results found for scene_id: <your_scene_id>") {
          console.log("No results found")
            // Display a "No results found" message to the user
        } else {
            const result = JSON.parse(event.data);
            console.log("RESULT", result)
            // Process and display the backtest result in the UI
        }
    };
    };

    eventSource.onerror = (error) => {
      console.error('Error receiving backtest results:', error);
      setError(error);
      setIsLoading(false);
    };

    return () => {
      eventSource.close(); // Clean up the EventSource on component unmount
    };
  }, [sceneId]);  // Re-run the effect if sceneId changes

  if (error) {
    return <div>Error: {error.message}</div>;
  }

  if (isLoading) {
    return <div>Loading backtest results...</div>;
  }

  return (
    <div>
      <h2>Backtest Results for Scene {sceneId}</h2>
      <table>
        <thead>
          <tr>
            <th>Metric</th>
            <th>Value</th>
          </tr>
        </thead>
        <tbody>
          {/* Map over the results object to create table rows */}
          {Object.entries(results).map(([key, value]) => (
            <tr key={key}>
              <td>{key}</td>
              <td>{value}</td>
            </tr>
          ))}
        </tbody>
      </table>
      {/* You can add more visualizations here (charts, graphs, etc.) */}
    </div>
  );
}

export default Results;
