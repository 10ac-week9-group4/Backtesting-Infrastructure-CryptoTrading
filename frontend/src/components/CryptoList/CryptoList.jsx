import React from 'react';
import './CryptoList.css'; // Assuming you have a CSS file for stylingCryptoList.css

const cryptoData = [
    { name: 'Bitcoin', symbol: 'BTC', weight: 0.607994 },
    { name: 'Ethereum', symbol: 'ETH', weight: 0.204847 },
    { name: 'Tether USD1', symbol: 'USD1', weight: 0.057246 },
    { name: 'BNB', symbol: 'BNB', weight: 0.042742 },
    { name: 'Solana', symbol: 'SOL', weight: 0.031767 },
    { name: 'USDC', symbol: 'USDC', weight: 0.016555 },
    { name: 'Toncoin', symbol: 'TON', weight: 0.009463 },
    { name: 'XRP', symbol: 'XRP', weight: 0.013373 },
    { name: 'Dogecoin', symbol: 'DOGE', weight: 0.008975 },
    { name: 'Cardano', symbol: 'ADA', weight: 0.007037 }
];

const CryptoList = () => {
    return (
        <div className="crypto-list">
            <h2>Cryptocurrency List</h2>
            <table>
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Symbol</th>
                        <th>Weight</th>
                    </tr>
                </thead>
                <tbody>
                    {cryptoData.map((crypto, index) => (
                        <tr key={index}>
                            <td>{crypto.name}</td>
                            <td>{crypto.symbol}</td>
                            <td>{crypto.weight}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

export default CryptoList;
