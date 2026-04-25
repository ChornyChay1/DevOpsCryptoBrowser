// src/__mocks__/lightweight-charts.js
// Кладёте этот файл в: <корень проекта>/__mocks__/lightweight-charts.js

const mockTimeScale = {
    getVisibleLogicalRange: jest.fn(() => null),
    setVisibleLogicalRange: jest.fn(),
    subscribeVisibleLogicalRangeChange: jest.fn(),
    scrollPosition: jest.fn(() => 0),
};

const makeSeries = () => ({ setData: jest.fn() });

export const createChart = jest.fn(() => {
    const seriesList = [];
    return {
        addSeries: jest.fn(() => {
            const s = makeSeries();
            seriesList.push(s);
            return s;
        }),
        removeSeries: jest.fn(),
        timeScale: jest.fn(() => mockTimeScale),
        applyOptions: jest.fn(),
        remove: jest.fn(),
        __seriesList: seriesList,
    };
});

export const CandlestickSeries = 'CandlestickSeries';
export const LineSeries = 'LineSeries';