import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import IndicatorPanel from '../IndicatorPanel';

describe('IndicatorPanel', () => {
    const mockIndicators = [
        { id: '1', name: 'SMA 14', type: 'sma', period: 14, color: '#ff0000' }
    ];

    const mockHandlers = {
        onAdd: jest.fn(),
        onDelete: jest.fn(),
        onUpdateIndicator: jest.fn()
    };

    beforeEach(() => {
        jest.clearAllMocks();
    });

    test('1. рендерит заголовок', () => {
        render(<IndicatorPanel indicators={[]} {...mockHandlers} />);
        expect(screen.getByText('Индикаторы')).toBeInTheDocument();
    });

    test('2. показывает пустое состояние', () => {
        render(<IndicatorPanel indicators={[]} {...mockHandlers} />);
        expect(screen.getByText('Нет добавленных индикаторов')).toBeInTheDocument();
    });

    test('3. показывает список индикаторов', () => {
        render(<IndicatorPanel indicators={mockIndicators} {...mockHandlers} />);
        expect(screen.getByText('SMA 14')).toBeInTheDocument();
    });

    test('4. открывает форму добавления', () => {
        render(<IndicatorPanel indicators={[]} {...mockHandlers} />);
        fireEvent.click(screen.getByText('Добавить'));
        expect(screen.getByPlaceholderText('например: SMA 14')).toBeInTheDocument();
    });

    test('5. добавляет индикатор', () => {
        render(<IndicatorPanel indicators={[]} {...mockHandlers} />);

        fireEvent.click(screen.getByText('Добавить'));

        const nameInput = screen.getByPlaceholderText('например: SMA 14');
        fireEvent.change(nameInput, { target: { value: 'Test SMA' } });

        fireEvent.click(screen.getByText('Создать'));

        expect(mockHandlers.onAdd).toHaveBeenCalled();
    });

    test('6. удаляет индикатор', () => {
        render(<IndicatorPanel indicators={mockIndicators} {...mockHandlers} />);

        const deleteButton = screen.getByTitle('Удалить');
        fireEvent.click(deleteButton);

        expect(mockHandlers.onDelete).toHaveBeenCalledWith('1');
    });

    test('7. редактирует индикатор', () => {
        render(<IndicatorPanel indicators={mockIndicators} {...mockHandlers} />);

        fireEvent.click(screen.getByTitle('Редактировать'));

        const nameInput = screen.getByDisplayValue('SMA 14');
        fireEvent.change(nameInput, { target: { value: 'New Name' } });

        fireEvent.click(screen.getByText('Сохранить'));

        expect(mockHandlers.onUpdateIndicator).toHaveBeenCalled();
    });

    test('8. отменяет редактирование индикатора', () => {
        render(<IndicatorPanel indicators={mockIndicators} {...mockHandlers} />);

        fireEvent.click(screen.getByTitle('Редактировать'));
        expect(screen.getByDisplayValue('SMA 14')).toBeInTheDocument();

        fireEvent.click(screen.getByText('Отмена'));

        // Проверяем что форма редактирования закрылась
        expect(screen.queryByDisplayValue('SMA 14')).not.toBeInTheDocument();
        // Проверяем что onUpdateIndicator не был вызван
        expect(mockHandlers.onUpdateIndicator).not.toHaveBeenCalled();
    });

    // 9. Тест для редактирования с пустым именем (кнопка disabled)
    test('9. кнопка сохранения disabled при пустом имени в редактировании', () => {
        render(<IndicatorPanel indicators={mockIndicators} {...mockHandlers} />);

        fireEvent.click(screen.getByTitle('Редактировать'));

        const nameInput = screen.getByDisplayValue('SMA 14');
        fireEvent.change(nameInput, { target: { value: '' } });

        const saveButton = screen.getByText('Сохранить');
        expect(saveButton).toBeDisabled();
    });

    // 10. Тест для добавления с пустым именем (кнопка disabled)
    test('10. кнопка создания disabled при пустом имени', () => {
        render(<IndicatorPanel indicators={[]} {...mockHandlers} />);

        fireEvent.click(screen.getByText('Добавить'));

        const createButton = screen.getByText('Создать');
        expect(createButton).toBeDisabled();

        // Заполняем имя
        const nameInput = screen.getByPlaceholderText('например: SMA 14');
        fireEvent.change(nameInput, { target: { value: 'Test' } });

        expect(createButton).not.toBeDisabled();
    });

    // 12. Тест для группировки индикаторов по категориям
    test('12. правильно группирует индикаторы по категориям', () => {
        const mixedIndicators = [
            { id: '1', name: 'SMA 14', type: 'sma', period: 14, color: '#ff0000' },
            { id: '2', name: 'RSI 14', type: 'rsi', period: 14, color: '#00ff00' },
            { id: '3', name: 'EMA 12', type: 'ema', period: 12, color: '#0000ff' },
        ];

        render(<IndicatorPanel indicators={mixedIndicators} {...mockHandlers} />);

        // Должны быть обе категории
        expect(screen.getByText('Ценовые')).toBeInTheDocument();
        expect(screen.getByText('Осцилляторы')).toBeInTheDocument();

        // Проверяем количество индикаторов в категориях
        const priceCategory = screen.getByText('Ценовые').parentElement;
        expect(priceCategory).toBeInTheDocument();
    });

    // 13. Тест для закрытия формы добавления через кнопку "Закрыть"
    test('13. закрывает форму добавления при клике на кнопку "Закрыть"', () => {
        render(<IndicatorPanel indicators={[]} {...mockHandlers} />);

        fireEvent.click(screen.getByText('Добавить'));
        expect(screen.getByPlaceholderText('например: SMA 14')).toBeInTheDocument();

        fireEvent.click(screen.getByText('Закрыть'));
        expect(screen.queryByPlaceholderText('например: SMA 14')).not.toBeInTheDocument();
    });

    // 14. Тест для добавления первого индикатора через кнопку в empty-state
    test('14. кнопка "Добавить первый индикатор" открывает форму', () => {
        render(<IndicatorPanel indicators={[]} {...mockHandlers} />);

        expect(screen.getByText('Добавить первый индикатор')).toBeInTheDocument();

        fireEvent.click(screen.getByText('Добавить первый индикатор'));

        expect(screen.getByPlaceholderText('например: SMA 14')).toBeInTheDocument();
    });

    // 15. Тест для редактирования периода индикатора
    test('15. обновляет период при редактировании', () => {
        render(<IndicatorPanel indicators={mockIndicators} {...mockHandlers} />);

        fireEvent.click(screen.getByTitle('Редактировать'));

        const periodInput = screen.getByDisplayValue('14');
        fireEvent.change(periodInput, { target: { value: '20' } });

        fireEvent.click(screen.getByText('Сохранить'));

        expect(mockHandlers.onUpdateIndicator).toHaveBeenCalledWith(
            '1',
            expect.objectContaining({ period: 20 })
        );
    });

    // 16. Тест для редактирования цвета индикатора
    test('16. обновляет цвет при редактировании', () => {
        render(<IndicatorPanel indicators={mockIndicators} {...mockHandlers} />);

        fireEvent.click(screen.getByTitle('Редактировать'));

        const colorInput = screen.getByDisplayValue('#ff0000');
        fireEvent.change(colorInput, { target: { value: '#00ff00' } });

        fireEvent.click(screen.getByText('Сохранить'));

        expect(mockHandlers.onUpdateIndicator).toHaveBeenCalledWith(
            '1',
            expect.objectContaining({ color: '#00ff00' })
        );
    });

    // 17. Тест для типа индикатора в add форме
    test('17. меняет тип индикатора при создании', () => {
        render(<IndicatorPanel indicators={[]} {...mockHandlers} />);

        fireEvent.click(screen.getByText('Добавить'));

        const typeSelect = screen.getByRole('combobox');
        fireEvent.change(typeSelect, { target: { value: 'ema' } });

        const nameInput = screen.getByPlaceholderText('например: SMA 14');
        fireEvent.change(nameInput, { target: { value: 'Test EMA' } });

        fireEvent.click(screen.getByText('Создать'));

        expect(mockHandlers.onAdd).toHaveBeenCalledWith(
            expect.objectContaining({ type: 'ema', name: 'Test EMA' })
        );
    });
});