// src/setupTests.js
import '@testing-library/jest-dom';

// Мок для localStorage
const localStorageMock = {
    getItem: jest.fn(),
    setItem: jest.fn(),
    clear: jest.fn(),
    removeItem: jest.fn()
};
global.localStorage = localStorageMock;
global.IS_REACT_ACT_ENVIRONMENT = true;

// Мок для ResizeObserver
global.ResizeObserver = class {
    observe() {}
    unobserve() {}
    disconnect() {}
};

// Мок для fetch
global.fetch = jest.fn();

// Глобальный мок для lightweight-charts
jest.mock('lightweight-charts', () => ({
    createChart: jest.fn().mockReturnValue({
        addSeries: jest.fn().mockReturnValue({
            setData: jest.fn(),
            applyOptions: jest.fn(),
        }),
        removeSeries: jest.fn(),
        applyOptions: jest.fn(),
        remove: jest.fn(),
        timeScale: jest.fn().mockReturnValue({
            getVisibleLogicalRange: jest.fn(),
            setVisibleLogicalRange: jest.fn(),
            subscribeVisibleLogicalRangeChange: jest.fn(),
            scrollPosition: jest.fn(),
        }),
    }),
    CandlestickSeries: jest.fn(),
    LineSeries: jest.fn(),
}));