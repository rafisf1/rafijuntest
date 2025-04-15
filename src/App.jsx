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

        // Process BTC data
        const btcPrices = btcData.prices.map(price => ({
          x: new Date(price[0]).toLocaleDateString(),
          y: price[1]
        }));

        // Process ETH data
        const ethPrices = ethData.prices.map(price => ({
          x: new Date(price[0]).toLocaleDateString(),
          y: price[1]
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
  }, []);

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          color: '#94a3b8' // slate-400 for better visibility in dark mode
        }
      },
      title: {
        display: true,
        text: '7-Day Price History',
        color: '#94a3b8' // slate-400
      }
    },
    scales: {
      y: {
        beginAtZero: false,
        grid: {
          color: 'rgba(148, 163, 184, 0.1)' // slate-400 with low opacity
        },
        ticks: {
          color: '#94a3b8' // slate-400
        }
      },
      x: {
        grid: {
          color: 'rgba(148, 163, 184, 0.1)' // slate-400 with low opacity
        },
        ticks: {
          color: '#94a3b8' // slate-400
        }
      }
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <header className="text-center mb-12">
          <h1 className="text-4xl font-bold text-white mb-2">
            Crypto Dashboard
          </h1>
          <p className="text-slate-400">Real-time cryptocurrency price tracking</p>
        </header>
        
        {/* Price Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-12">
          <div className="bg-gray-800 rounded-2xl shadow-lg p-8 border border-gray-700">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center">
                <div className="w-10 h-10 bg-orange-900/30 rounded-full flex items-center justify-center mr-3">
                  <svg className="w-6 h-6 text-orange-500" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z"/>
                    <path d="M11 7h2v7h-2zm0 8h2v2h-2z"/>
                  </svg>
                </div>
                <h2 className="text-xl font-semibold text-white">Bitcoin (BTC)</h2>
              </div>
              <span className="px-3 py-1 bg-orange-900/30 text-orange-400 rounded-full text-sm font-medium">
                Live
              </span>
            </div>
            <p className="text-4xl font-bold text-orange-500 mb-2">
              ${prices.bitcoin.toLocaleString()}
            </p>
            <p className="text-slate-400 text-sm">Updated every minute</p>
          </div>

          <div className="bg-gray-800 rounded-2xl shadow-lg p-8 border border-gray-700">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center">
                <div className="w-10 h-10 bg-blue-900/30 rounded-full flex items-center justify-center mr-3">
                  <svg className="w-6 h-6 text-blue-500" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z"/>
                    <path d="M11 7h2v7h-2zm0 8h2v2h-2z"/>
                  </svg>
                </div>
                <h2 className="text-xl font-semibold text-white">Ethereum (ETH)</h2>
              </div>
              <span className="px-3 py-1 bg-blue-900/30 text-blue-400 rounded-full text-sm font-medium">
                Live
              </span>
            </div>
            <p className="text-4xl font-bold text-blue-500 mb-2">
              ${prices.ethereum.toLocaleString()}
            </p>
            <p className="text-slate-400 text-sm">Updated every minute</p>
          </div>
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-gray-800 rounded-2xl shadow-lg p-6 border border-gray-700">
            <Line options={chartOptions} data={btcData} />
          </div>
          <div className="bg-gray-800 rounded-2xl shadow-lg p-6 border border-gray-700">
            <Line options={chartOptions} data={ethData} />
          </div>
        </div>

        {/* Footer */}
        <footer className="mt-12 text-center text-slate-400 text-sm">
          <p className="mb-2">Data provided by CoinGecko API • Refreshes every minute</p>
          <p className="text-slate-500">Built by Rafi and Jun</p>
        </footer>
      </div>
    </div>
  );
}

export default App; 