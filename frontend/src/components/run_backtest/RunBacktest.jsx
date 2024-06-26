import React, { useState } from 'react';
import './RunBacktest.css'; 
import axios from 'axios';

const BASE_URL = "http://localhost:5000"; 

const RunBacktestForm = ({ setIsLoading, User }) => {
    const [asset, setAsset] = useState('');
    const [strategy, setStrategy] = useState('');
    const [startDate, setStartDate] = useState('');
    const [endDate, setEndDate] = useState('');
    const [cash, setCash] = useState('');
    const [commission, setCommission] = useState('');

    const runTest = async (e) => {
        e.preventDefault();
        try {
            setIsLoading(true);
            const response = await axios.post(`${BASE_URL}/get_backtest_scene`, {
                asset,
                strategy,
                start_date: startDate,
                end_date: endDate,
                cash: parseFloat(cash),
                commission: parseFloat(commission),
                user_id: User.id,
            });
            console.log(response.data);
            const { data } = response;
            if (data !== undefined) {
                if (data.success) {
                    alert(data.message); // Display success message
                } else {
                    alert(data.error); // Display error message
                }
            } else {
                alert("Something went wrong"); // Fallback error message
            }
        } catch (error) {
            console.error(error);
            alert(error.message); // Display network or other errors
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="backtest-form">
            <form onSubmit={runTest}>
                <div className="form-group">
                    <label htmlFor="assetInput">Asset:</label>
                    <input
                        type="text"
                        id="assetInput"
                        value={asset}
                        onChange={(e) => setAsset(e.target.value)}
                        required
                    />
                </div>
                <div className="form-group">
                    <label htmlFor="strategyInput">Strategy:</label>
                    <input
                        type="text"
                        id="strategyInput"
                        value={strategy}
                        onChange={(e) => setStrategy(e.target.value)}
                        required
                    />
                </div>
                <div className="form-group">
                    <label htmlFor="startDateInput">Start Date:</label>
                    <input
                        type="date"
                        id="startDateInput"
                        value={startDate}
                        onChange={(e) => setStartDate(e.target.value)}
                        required
                    />
                </div>
                <div className="form-group">
                    <label htmlFor="endDateInput">End Date:</label>
                    <input
                        type="date"
                        id="endDateInput"
                        value={endDate}
                        onChange={(e) => setEndDate(e.target.value)}
                        required
                    />
                </div>
                <div className="form-group">
                    <label htmlFor="cashInput">Initial Cash:</label>
                    <input
                        type="number"
                        id="cashInput"
                        min="100"
                        step="any"
                        value={cash}
                        onChange={(e) => setCash(e.target.value)}
                        required
                    />
                </div>
                <div className="form-group">
                    <label htmlFor="commissionInput">Commission:</label>
                    <input
                        type="number"
                        id="commissionInput"
                        step="any"
                        value={commission}
                        onChange={(e) => setCommission(e.target.value)}
                        required
                    />
                </div>
                <div className="btn-div">
                    <button type="submit">Run</button>
                </div>
            </form>
        </div>
    );
};

export default RunBacktestForm;
