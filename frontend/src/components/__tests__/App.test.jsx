// src/components/__tests__/App.test.jsx

jest.mock('../Chart', () => () => <div data-testid="chart" />);

import React from 'react';
import { render, screen, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import App from '../../App';

const mockIndicator = { id: '1', name: 'SMA 14', type: 'sma', period: 14, color: '#ff0000' };

function setupFetch(indicators = [mockIndicator]) {
    global.fetch = jest.fn(() => Promise.resolve({
        ok: true,
        json: () => Promise.resolve({
            candles: [{ timestamp: 1700000000000, open: 100, high: 110, low: 90, close: 105, indicators: {} }],
            indicators,
        }),
    }));
}

beforeEach(() => {
    process.env.REACT_APP_API_URL = 'http://localhost:5000';
    setupFetch();
});

afterEach(() => {
    jest.restoreAllMocks();
    jest.useRealTimers();
});

// renderApp без фейковых таймеров — промисы резолвятся нормально
const renderApp = async () => {
    await act(async () => { render(<App />); });
    // ждём пока данные загрузятся
    await waitFor(() => expect(global.fetch).toHaveBeenCalled());
};

describe('App', () => {
    it('рендерится без ошибок', async () => {
        await renderApp();
        expect(document.querySelector('.app')).toBeInTheDocument();
    });

    it('запрашивает данные при монтировании', async () => {
        await renderApp();
        expect(global.fetch).toHaveBeenCalledWith('http://localhost:5000/data');
    });

    it('показывает загрузку во время запроса', async () => {
        global.fetch = jest.fn(() => new Promise(() => {}));
        await act(async () => { render(<App />); });
        expect(screen.getByText('Загрузка...')).toBeInTheDocument();
    });

    it('скрывает загрузку после получения данных', async () => {
        await renderApp();
        expect(screen.queryByText('Загрузка...')).not.toBeInTheDocument();
    });

    it('повторно запрашивает данные каждые 5 секунд', async () => {
        jest.useFakeTimers();
        setupFetch();
        await act(async () => { render(<App />); });
        const before = global.fetch.mock.calls.length;
        await act(async () => { jest.advanceTimersByTime(5000); });
        expect(global.fetch.mock.calls.length).toBeGreaterThan(before);
    });

    it('очищает интервал при размонтировании', async () => {
        const spy = jest.spyOn(global, 'clearInterval');
        let unmount;
        await act(async () => { ({ unmount } = render(<App />)); });
        unmount();
        expect(spy).toHaveBeenCalled();
    });

    it('не падает при сетевой ошибке', async () => {
        global.fetch = jest.fn(() => Promise.reject(new Error('fail')));
        const spy = jest.spyOn(console, 'error').mockImplementation(() => {});
        await act(async () => { render(<App />); });
        await waitFor(() => expect(spy).toHaveBeenCalled());
    });

    it('handleAddIndicator — открывает форму, заполняет и сабмитит', async () => {
        await renderApp();

        await act(async () => {
            await userEvent.click(screen.getByText('Добавить'));
        });

        await waitFor(() => screen.getByPlaceholderText('например: SMA 14'));
        await userEvent.type(screen.getByPlaceholderText('например: SMA 14'), 'Test SMA');

        global.fetch = jest.fn()
            .mockResolvedValueOnce({ ok: true })
            .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve({ candles: [], indicators: [] }) });

        await act(async () => {
            await userEvent.click(screen.getByText('Создать'));
        });

        expect(global.fetch).toHaveBeenCalledWith(
            'http://localhost:5000/indicator',
            expect.objectContaining({ method: 'POST' })
        );
    });

    it('handleDeleteIndicator — клик по кнопке удаления', async () => {
        await renderApp();
        await waitFor(() => screen.getByTitle('Удалить'));

        global.fetch = jest.fn()
            .mockResolvedValueOnce({ ok: true })
            .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve({ candles: [], indicators: [] }) });

        await act(async () => {
            await userEvent.click(screen.getByTitle('Удалить'));
        });

        expect(global.fetch).toHaveBeenCalledWith(
            'http://localhost:5000/indicator/1',
            expect.objectContaining({ method: 'DELETE' })
        );
    });

    it('handleUpdateIndicator — редактирование и сохранение', async () => {
        await renderApp();
        await waitFor(() => screen.getByTitle('Редактировать'));

        await act(async () => {
            await userEvent.click(screen.getByTitle('Редактировать'));
        });

        await waitFor(() => screen.getByPlaceholderText('Название'));
        const nameInput = screen.getByPlaceholderText('Название');
        await userEvent.clear(nameInput);
        await userEvent.type(nameInput, 'Updated SMA');

        global.fetch = jest.fn()
            .mockResolvedValueOnce({ ok: true })
            .mockResolvedValueOnce({ ok: true, json: () => Promise.resolve({ candles: [], indicators: [] }) });

        await act(async () => {
            await userEvent.click(screen.getByText('Сохранить'));
        });

        expect(global.fetch).toHaveBeenCalledWith(
            'http://localhost:5000/indicator/1',
            expect.objectContaining({ method: 'PUT' })
        );
    });

    it('handleAddIndicator не падает при ошибке сети', async () => {
        await renderApp();
        await act(async () => { await userEvent.click(screen.getByText('Добавить')); });
        await waitFor(() => screen.getByPlaceholderText('например: SMA 14'));
        await userEvent.type(screen.getByPlaceholderText('например: SMA 14'), 'Test');

        global.fetch = jest.fn(() => Promise.reject(new Error('fail')));
        const spy = jest.spyOn(console, 'error').mockImplementation(() => {});
        await act(async () => { await userEvent.click(screen.getByText('Создать')); });
        expect(spy).toHaveBeenCalled();
    });

    it('handleDeleteIndicator не падает при ошибке сети', async () => {
        await renderApp();
        await waitFor(() => screen.getByTitle('Удалить'));

        global.fetch = jest.fn(() => Promise.reject(new Error('fail')));
        const spy = jest.spyOn(console, 'error').mockImplementation(() => {});
        await act(async () => { await userEvent.click(screen.getByTitle('Удалить')); });
        expect(spy).toHaveBeenCalled();
    });
});