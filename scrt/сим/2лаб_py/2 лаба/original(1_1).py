import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


def plot_modulation_data(filename, plot_type='both', figsize=(12, 8)):
    """
    Отображает графики данных амплитудной модуляции из файла

    Parameters:
    -----------
    filename : str
        Путь к файлу с данными
    plot_type : str
        Тип графика: 'time' - временная область,
                    'freq' - частотная область,
                    'both' - оба графика (по умолчанию)
    figsize : tuple
        Размер фигуры
    """

    # Чтение данных из файла
    try:
        # Используем pandas для удобного чтения данных
        df = pd.read_csv(filename, sep='\t', header=None,
                         names=['frequency', 'amplitude', 'power', 'inverse', 'log_power'])
    except Exception as e:
        print(f"Ошибка чтения файла: {e}")
        return

    # Создание графиков
    if plot_type in ['both', 'time']:
        # График во временной области
        plt.figure(figsize=figsize)

        plt.subplot(2, 1, 1)
        plt.plot(df.index * (1e6 / len(df)), df['amplitude'], 'b-', linewidth=1)
        plt.xlabel('Время (отсчеты)')
        plt.ylabel('Амплитуда')
        plt.title('Сигнал во временной области')
        plt.grid(True, alpha=0.3)

        # Детальный просмотр части сигнала (первые 1000 точек)
        plt.subplot(2, 1, 2)
        n_points = min(1000, len(df))
        plt.plot(df.index[:n_points] * (1e6 / len(df)), df['amplitude'][:n_points], 'b-', linewidth=1)
        plt.xlabel('Время (отсчеты)')
        plt.ylabel('Амплитуда')
        plt.title('Сигнал во временной области (первые 1000 точек)')
        plt.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.show()

    if plot_type in ['both', 'freq']:
        # График в частотной области
        plt.figure(figsize=figsize)

        plt.subplot(2, 1, 1)
        # Отображаем только первую половину спектра (симметричный)
        n_half = len(df) // 2
        plt.plot(df['frequency'][:n_half], df['power'][:n_half], 'r-', linewidth=1)
        plt.xlabel('Частота (Гц)')
        plt.ylabel('Мощность')
        plt.title('Спектр сигнала')
        plt.grid(True, alpha=0.3)

        plt.subplot(2, 1, 2)
        # Логарифмическая шкала мощности
        plt.plot(df['frequency'][:n_half], df['log_power'][:n_half], 'r-', linewidth=1)
        plt.xlabel('Частота (Гц)')
        plt.ylabel('Мощность (дБ)')
        plt.title('Спектр сигнала (логарифмическая шкала)')
        plt.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.show()

    if plot_type == 'comprehensive':
        # Комплексный график со всей информацией
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))

        # Временная область
        axes[0, 0].plot(df.index * (1e6 / len(df)), df['amplitude'], 'b-', linewidth=1)
        axes[0, 0].set_xlabel('Время (отсчеты)')
        axes[0, 0].set_ylabel('Амплитуда')
        axes[0, 0].set_title('Сигнал во временной области')
        axes[0, 0].grid(True, alpha=0.3)

        # Детальный вид временной области
        n_points = min(500, len(df))
        axes[0, 1].plot(df.index[:n_points] * (1e6 / len(df)), df['amplitude'][:n_points], 'b-', linewidth=1.5)
        axes[0, 1].set_xlabel('Время (отсчеты)')
        axes[0, 1].set_ylabel('Амплитуда')
        axes[0, 1].set_title('Детальный вид (первые 500 точек)')
        axes[0, 1].grid(True, alpha=0.3)

        # Спектр
        n_half = len(df) // 2
        axes[1, 0].plot(df['frequency'][:n_half], df['power'][:n_half], 'r-', linewidth=1)
        axes[1, 0].set_xlabel('Частота (Гц)')
        axes[1, 0].set_ylabel('Мощность')
        axes[1, 0].set_title('Спектр сигнала')
        axes[1, 0].grid(True, alpha=0.3)

        # Логарифмический спектр
        axes[1, 1].plot(df['frequency'][:n_half], df['log_power'][:n_half], 'r-', linewidth=1)
        axes[1, 1].set_xlabel('Частота (Гц)')
        axes[1, 1].set_ylabel('Мощность (дБ)')
        axes[1, 1].set_title('Спектр (логарифмическая шкала)')
        axes[1, 1].grid(True, alpha=0.3)

        plt.tight_layout()
        plt.show()

    # Вывод основной информации о сигнале
    print(f"Общее количество точек: {len(df)}")
    print(f"Диапазон амплитуд: от {df['amplitude'].min():.4f} до {df['amplitude'].max():.4f}")
    print(f"Максимальная мощность: {df['power'].max():.2e}")
    print(f"Диапазон частот: от {df['frequency'].min():.0f} Гц до {df['frequency'].max():.0f} Гц")


# Пример использования
if __name__ == "__main__":
    # Замените 'samples.txt' на путь к вашему файлу
    plot_modulation_data('Original(1).txt', plot_type='both')

    # Для более детального анализа
    # plot_modulation_data('samples.txt', plot_type='comprehensive')