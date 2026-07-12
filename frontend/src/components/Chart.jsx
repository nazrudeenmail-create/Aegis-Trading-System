import React, { useEffect, useRef } from 'react';
import { createChart, CandlestickSeries } from 'lightweight-charts';

export function Chart({ data, colors }) {
  const chartContainerRef = useRef();
  const chartRef = useRef();

  useEffect(() => {
    const handleResize = () => {
      if (chartRef.current && chartContainerRef.current) {
        chartRef.current.applyOptions({ width: chartContainerRef.current.clientWidth });
      }
    };

    if (chartContainerRef.current) {
      const chart = createChart(chartContainerRef.current, {
        width: chartContainerRef.current.clientWidth,
        height: 400,
        layout: {
          background: { color: 'transparent' },
          textColor: '#94a3b8',
        },
        grid: {
          vertLines: { color: '#1e293b' },
          horzLines: { color: '#1e293b' },
        },
        timeScale: {
          timeVisible: true,
          secondsVisible: false,
        },
      });

      chartRef.current = chart;

      const candlestickSeries = chart.addSeries(CandlestickSeries, {
        upColor: colors?.up || '#34d399',
        downColor: colors?.down || '#f87171',
        borderVisible: false,
        wickUpColor: colors?.up || '#34d399',
        wickDownColor: colors?.down || '#f87171',
      });

      if (data && data.length > 0) {
        // Data should be { time: string/timestamp, open: number, high: number, low: number, close: number }
        // The API returns timestamp, open, high, low, close, volume
        const formattedData = data.map(d => {
          let timeVal = d.time;
          if (typeof d.time !== 'number') {
            timeVal = new Date(d.timestamp || d.time).getTime() / 1000;
          }
          return {
            time: timeVal,
            open: d.open,
            high: d.high,
            low: d.low,
            close: d.close,
          };
        }).sort((a, b) => a.time - b.time);

        // Remove duplicates if any
        const uniqueData = formattedData.filter((v, i, a) => a.findIndex(t => (t.time === v.time)) === i);

        candlestickSeries.setData(uniqueData);
      }

      window.addEventListener('resize', handleResize);

      return () => {
        window.removeEventListener('resize', handleResize);
        chart.remove();
      };
    }
  }, [data, colors]);

  return <div ref={chartContainerRef} className="w-full" />;
}
