// src/components/Chart.jsx
import React, { useEffect, useRef } from 'react';
import { createChart, CandlestickSeries, LineSeries } from 'lightweight-charts';

function Chart({ candles, indicators }) {
    const mainChartRef = useRef();
    const subChartRef = useRef();
    const mainSeriesRef = useRef();
    const subSeriesRef = useRef({});
    const indicatorSeriesRef = useRef({});

    useEffect(() => {
        if (!mainChartRef.current) return;

        const mainChart = createChart(mainChartRef.current, {
            layout: {
                background: { color: '#ffffff' },
                textColor: '#000000',
            },
            grid: {
                vertLines: { color: '#f0f0f0' },
                horzLines: { color: '#f0f0f0' },
            },
            width: mainChartRef.current.clientWidth,
            height: 300,
            timeScale: {
                borderColor: '#e0e0e0',
                visible: true,
            },
            crosshair: {
                mode: 0,
            },
        });

        mainSeriesRef.current = mainChart.addSeries(CandlestickSeries, {
            upColor: '#00c853',
            downColor: '#ff3d00',
            borderDownColor: '#ff3d00',
            borderUpColor: '#00c853',
            wickDownColor: '#000000',
            wickUpColor: '#000000',
        });

        const handleResize = () => {
            if (mainChartRef.current) {
                mainChart.applyOptions({
                    width: mainChartRef.current.clientWidth,
                });
            }
        };

        window.addEventListener('resize', handleResize);

        return () => {
            window.removeEventListener('resize', handleResize);
            mainChart.remove();
        };
    }, []);

    useEffect(() => {
        if (!subChartRef.current) return;

        const subChart = createChart(subChartRef.current, {
            layout: {
                background: { color: '#ffffff' },
                textColor: '#000000',
            },
            grid: {
                vertLines: { color: '#f0f0f0' },
                horzLines: { color: '#f0f0f0' },
            },
            width: subChartRef.current.clientWidth,
            height: 150,
            timeScale: {
                borderColor: '#e0e0e0',
                visible: true,
            },
            crosshair: {
                mode: 0,
            },
        });

        const handleResize = () => {
            if (subChartRef.current) {
                subChart.applyOptions({
                    width: subChartRef.current.clientWidth,
                });
            }
        };

        window.addEventListener('resize', handleResize);

        subSeriesRef.current.chart = subChart;

        return () => {
            window.removeEventListener('resize', handleResize);
            subChart.remove();
        };
    }, []);

    useEffect(() => {
        if (!candles.length || !mainSeriesRef.current) return;

        const chartData = candles.map((c, index) => ({
            time: Math.floor(c.timestamp / 1000), // конвертируем мс в секунды
            open: c.open,
            high: c.high,
            low: c.low,
            close: c.close,
        }));

        mainSeriesRef.current.setData(chartData);
    }, [candles]);

    useEffect(() => {
        if (!candles.length || !mainSeriesRef.current) return;

        // Очищаем старые серии
        Object.values(indicatorSeriesRef.current).forEach(series => {
            if (mainSeriesRef.current && mainSeriesRef.current.chart) {
                try {
                    mainSeriesRef.current.chart.removeSeries(series);
                } catch (e) {}
            }
        });

        if (subSeriesRef.current.chart) {
            Object.values(subSeriesRef.current).forEach(series => {
                if (series !== subSeriesRef.current.chart) {
                    try {
                        subSeriesRef.current.chart.removeSeries(series);
                    } catch (e) {}
                }
            });
        }

        indicatorSeriesRef.current = {};
        subSeriesRef.current = { chart: subSeriesRef.current.chart };

        const priceIndicators = indicators.filter(ind => ['sma', 'ema', 'wma'].includes(ind.type));
        const oscillatorIndicators = indicators.filter(ind => !['sma', 'ema', 'wma'].includes(ind.type));

        // Функция для подготовки данных индикатора
        const prepareIndicatorData = (indicatorId) => {
            const data = [];

            candles.forEach((c, index) => {
                const value = c.indicators?.[indicatorId];
                // Проверяем что value не null и не undefined
                if (value !== null && value !== undefined) {
                    data.push({
                        time: Math.floor(c.timestamp / 1000),
                        value: value
                    });
                }
            });

            return data;
        };

        console.log('Candles:', candles);
        console.log('Indicators:', indicators);

        // Добавляем ценовые индикаторы на основной график
        priceIndicators.forEach(ind => {
            try {
                console.log(`Processing price indicator ${ind.name} with id ${ind.id}`);
                const indicatorData = prepareIndicatorData(ind.id);

                console.log(`Indicator ${ind.name} data:`, indicatorData);

                if (indicatorData.length > 0 && mainSeriesRef.current && mainSeriesRef.current.chart) {
                    const lineSeries = mainSeriesRef.current.chart.addSeries(LineSeries, {
                        color: ind.color || '#000000',
                        lineWidth: 2,
                        priceLineVisible: false,
                        lastValueVisible: true,
                        crosshairMarkerVisible: true,
                        crosshairMarkerRadius: 4,
                    });

                    lineSeries.setData(indicatorData);
                    indicatorSeriesRef.current[ind.id] = lineSeries;

                    console.log(`✅ Added price indicator ${ind.name} with ${indicatorData.length} points`);
                } else {
                    console.warn(`⚠️ No valid data for price indicator ${ind.name}`);
                }
            } catch (error) {
                console.error(`❌ Error creating price indicator ${ind.name}:`, error);
            }
        });

        // Добавляем осцилляторы на нижний график
        if (subSeriesRef.current.chart && oscillatorIndicators.length > 0) {
            oscillatorIndicators.forEach(ind => {
                try {
                    console.log(`Processing oscillator ${ind.name} with id ${ind.id}`);
                    const indicatorData = prepareIndicatorData(ind.id);

                    console.log(`Oscillator ${ind.name} data:`, indicatorData);

                    if (indicatorData.length > 0) {
                        const lineSeries = subSeriesRef.current.chart.addSeries(LineSeries, {
                            color: ind.color || '#000000',
                            lineWidth: 2,
                            priceLineVisible: false,
                            lastValueVisible: true,
                            crosshairMarkerVisible: true,
                            crosshairMarkerRadius: 4,
                        });

                        lineSeries.setData(indicatorData);
                        subSeriesRef.current[ind.id] = lineSeries;

                        console.log(`✅ Added oscillator ${ind.name} with ${indicatorData.length} points`);
                    } else {
                        console.warn(`⚠️ No valid data for oscillator ${ind.name}`);
                    }
                } catch (error) {
                    console.error(`❌ Error creating oscillator ${ind.name}:`, error);
                }
            });
        }

        // Подгоняем масштаб
        setTimeout(() => {
            if (mainSeriesRef.current && mainSeriesRef.current.chart) {
                try {
                    mainSeriesRef.current.chart.timeScale().fitContent();
                } catch (e) {}
            }
            if (subSeriesRef.current.chart) {
                try {
                    subSeriesRef.current.chart.timeScale().fitContent();
                } catch (e) {}
            }
        }, 100);

    }, [candles, indicators]);

    return (
        <div className="chart-wrapper">
            <div ref={mainChartRef} className="main-chart" />
            {indicators.some(ind => !['sma', 'ema', 'wma'].includes(ind.type)) && (
                <>
                    <div className="chart-divider" />
                    <div ref={subChartRef} className="sub-chart" />
                </>
            )}
        </div>
    );
}

export default Chart;