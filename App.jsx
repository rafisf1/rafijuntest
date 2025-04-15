import React, { useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

function App() {
  const [prices, setPrices] = useState({ bitcoin: 0, ethereum: 0 });
  const [btcData, setBtcData] = useState({ labels: [], datasets: [] });
  const [ethData, setEthData] = useState({ labels: [], datasets: [] });

  // Fetch current prices
  useEffect(() => {
    const fetchPrices = async () => {
      try {
        const response = await fetch(
          'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd'
        );
        const data = await response.json();
        setPrices({
          bitcoin: data.bitcoin.usd,
          ethereum: data.ethereum.usd,
        });
      } catch (error) {
        console.error('Error fetching prices:', error);
      }
    };

    fetchPrices();
    const interval = setInterval(fetchPrices, 60000); // Update every minute
    return () => clearInterval(interval);
  }, []);

  // Fetch chart data
  useEffect(() => {
    const fetchChartData = async () => {
      try {
        // Fetch BTC data
        const btcResponse = await fetch(
          'https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days=7'
        );
        const btcData = await btcResponse.json();
        
        // Fetch ETH data
        const ethResponse = await fetch(
          'https://api.coingecko.com/api/v3/coins/ethereum/market_chart?vs_currency=usd&days=7'
        );
        const ethData = await ethResponse.json();

        // Format dates for both datasets
        const formatDate = (timestamp) => {
          const date = new Date(timestamp);
          const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
          return `${months[date.getMonth()]} ${date.getDate()}`;
        };

        // Process BTC data
        const btcPrices = btcData.prices.map(([timestamp, price]) => ({
          x: formatDate(timestamp),
          y: price
        }));

        // Process ETH data
        const ethPrices = ethData.prices.map(([timestamp, price]) => ({
          x: formatDate(timestamp),
          y: price
        }));

        setBtcData({
          labels: btcPrices.map(price => price.x),
          datasets: [{
            label: 'Bitcoin Price (USD)',
            data: btcPrices.map(price => price.y),
            borderColor: 'rgb(247, 147, 26)',
            backgroundColor: 'rgba(247, 147, 26, 0.1)',
            fill: true,
            tension: 0.4
          }]
        });

        setEthData({
          labels: ethPrices.map(price => price.x),
          datasets: [{
            label: 'Ethereum Price (USD)',
            data: ethPrices.map(price => price.y),
            borderColor: 'rgb(98, 126, 234)',
            backgroundColor: 'rgba(98, 126, 234, 0.1)',
            fill: true,
            tension: 0.4
          }]
        });
      } catch (error) {
        console.error('Error fetching chart data:', error);
      }
    };

    fetchChartData();
    // Fetch new data every 5 minutes
    const interval = setInterval(fetchChartData, 300000);
    return () => clearInterval(interval);
  }, []);

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: '7-Day Price History'
      }
    },
    scales: {
      y: {
        beginAtZero: false,
        ticks: {
          callback: function(value) {
            return '$' + value.toLocaleString();
          }
        }
      }
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-center text-gray-900 mb-8">
          Cryptocurrency Dashboard
        </h1>
        
        {/* Price Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-2">Bitcoin (BTC)</h2>
            <p className="text-3xl font-bold text-orange-500">
              ${prices.bitcoin.toLocaleString()}
            </p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-2">Ethereum (ETH)</h2>
            <p className="text-3xl font-bold text-blue-500">
              ${prices.ethereum.toLocaleString()}
            </p>
          </div>
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white rounded-lg shadow p-6">
            <Line options={chartOptions} data={btcData} />
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <Line options={chartOptions} data={ethData} />
          </div>
        </div>
      </div>
    </div>
  );
}

export default App; 