import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


def plot_tonal_modulation_spectrum(filename, figsize=(12, 8), focus_bandwidth=200000):
    """
    Отображает спектр тональной модуляции в линейном масштабе

    Parameters:
    -----------
    filename : str
        Путь к файлу с данными
    figsize : tuple
        Размер фигуры
    focus_bandwidth : float
        Ширина полосы частот для детального просмотра (в Гц)
    """

    # Чтение данных из файла
    try:
        df = pd.read_csv(filename, sep='\t', header=None,
                         names=['frequency', 'amplitude', 'power', 'inverse', 'log_power'])
    except Exception as e:
        print(f"Ошибка чтения файла: {e}")
        return

    # Основной график спектра
    plt.figure(figsize=figsize)

    # Полный спектр
    plt.subplot(2, 1, 1)
    n_half = len(df) // 2
    frequencies = df['frequency'][:n_half]
    power_linear = df['power'][:n_half]

    plt.plot(frequencies, power_linear, 'b-', linewidth=1.5)
    plt.xlabel('Частота (Гц)')
    plt.ylabel('Мощность (линейный масштаб)')
    plt.title('Спектр тональной модуляции - полный диапазон')
    plt.grid(True, alpha=0.3)
    plt.yscale('linear')

    # Детальный вид вокруг несущей частоты (50 кГц)
    plt.subplot(2, 1, 2)
    carrier_freq = 50000  # 50 кГц из вашего кода
    freq_min = carrier_freq - focus_bandwidth / 2
    freq_max = carrier_freq + focus_bandwidth / 2

    # Фильтруем данные вокруг несущей частоты
    mask = (frequencies >= max(0, freq_min)) & (frequencies <= freq_max)
    freq_focused = frequencies[mask]
    power_focused = power_linear[mask]

    plt.plot(freq_focused, power_focused, 'r-', linewidth=1.5)
    plt.xlabel('Частота (Гц)')
    plt.ylabel('Мощность (линейный масштаб)')
    plt.title(f'Детальный спектр вокруг несущей частоты {carrier_freq / 1000:.1f} кГц')
    plt.grid(True, alpha=0.3)
    plt.yscale('linear')

    # Добавляем вертикальную линию на несущей частоте
    plt.axvline(x=carrier_freq, color='green', linestyle='--', alpha=0.7,
                label=f'Несущая {carrier_freq / 1000:.1f} кГц')

    # Добавляем линии на боковых полосах
    modulation_freq = 1000  # 1 кГц из вашего кода
    upper_sideband = carrier_freq + modulation_freq
    lower_sideband = carrier_freq - modulation_freq

    plt.axvline(x=upper_sideband, color='orange', linestyle='--', alpha=0.7,
                label=f'Верхняя боковая {upper_sideband / 1000:.1f} кГц')
    plt.axvline(x=lower_sideband, color='orange', linestyle='--', alpha=0.7,
                label=f'Нижняя боковая {lower_sideband / 1000:.1f} кГц')

    plt.legend()

    plt.tight_layout()
    plt.show()

    # Анализ характеристик спектра
    analyze_spectrum_characteristics(frequencies, power_linear, carrier_freq, modulation_freq)


def analyze_spectrum_characteristics(frequencies, power, carrier_freq, modulation_freq):
    """
    Анализ характеристик спектра тональной модуляции
    """
    print("\n" + "=" * 60)
    print("АНАЛИЗ СПЕКТРА ТОНАЛЬНОЙ МОДУЛЯЦИИ")
    print("=" * 60)

    # Находим пик на несущей частоте
    carrier_idx = np.argmin(np.abs(frequencies - carrier_freq))
    carrier_power = power[carrier_idx]

    # Ищем боковые полосы
    upper_sideband_freq = carrier_freq + modulation_freq
    lower_sideband_freq = carrier_freq - modulation_freq

    upper_idx = np.argmin(np.abs(frequencies - upper_sideband_freq))
    lower_idx = np.argmin(np.abs(frequencies - lower_sideband_freq))

    upper_power = power[upper_idx]
    lower_power = power[lower_idx]

    print(f"Несущая частота: {carrier_freq:.1f} Гц")
    print(f"Мощность несущей: {carrier_power:.2e}")
    print(f"\nВерхняя боковая полоса: {upper_sideband_freq:.1f} Гц")
    print(f"Мощность верхней боковой: {upper_power:.2e}")
    print(f"\nНижняя боковая полоса: {lower_sideband_freq:.1f} Гц")
    print(f"Мощность нижней боковой: {lower_power:.2e}")

    # Коэффициент модуляции
    if carrier_power > 0:
        modulation_index = (upper_power + lower_power) / (2 * carrier_power)
        print(f"\nКоэффициент модуляции: {modulation_index:.4f}")

        # Теоретическое значение для 75% модуляции
        theoretical_index = 0.75
        print(f"Теоретический коэффициент (75%): {theoretical_index:.4f}")
        print(f"Отклонение: {abs(modulation_index - theoretical_index) / theoretical_index * 100:.2f}%")


def plot_comparison_spectrum(filename):
    """
    Сравнение линейного и логарифмического масштабов
    """
    df = pd.read_csv(filename, sep='\t', header=None,
                     names=['frequency', 'amplitude', 'power', 'inverse', 'log_power'])

    n_half = len(df) // 2
    frequencies = df['frequency'][:n_half]
    power_linear = df['power'][:n_half]
    power_log = df['log_power'][:n_half]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

    # Линейный масштаб
    ax1.plot(frequencies, power_linear, 'b-', linewidth=1.5)
    ax1.set_xlabel('Частота (Гц)')
    ax1.set_ylabel('Мощность (линейный масштаб)')
    ax1.set_title('Спектр тональной модуляции - линейный масштаб')
    ax1.grid(True, alpha=0.3)
    ax1.set_yscale('linear')

    # Логарифмический масштаб для сравнения
    ax2.plot(frequencies, power_log, 'r-', linewidth=1.5)
    ax2.set_xlabel('Частота (Гц)')
    ax2.set_ylabel('Мощность (дБ)')
    ax2.set_title('Спектр тональной модуляции - логарифмический масштаб')
    ax2.grid(True, alpha=0.3)
    ax2.set_yscale('linear')

    plt.tight_layout()
    plt.show()


# Упрощенная версия для быстрого просмотра
def quick_tonal_spectrum(filename):
    """
    Быстрый просмотр спектра тональной модуляции
    """
    data = np.loadtxt(filename, delimiter='\t')
    freq = data[:, 0]
    power = data[:, 2]

    n_half = len(freq) // 2
    freq_half = freq[:n_half]
    power_half = power[:n_half]

    plt.figure(figsize=(10, 6))
    plt.plot(freq_half, power_half, 'b-', linewidth=1)
    plt.xlabel('Частота (Гц)')
    plt.ylabel('Мощность (линейный масштаб)')
    plt.title('Спектр тональной модуляции')
    plt.grid(True, alpha=0.3)
    plt.yscale('linear')

    # Показываем основные компоненты
    carrier_freq = 50000
    modulation_freq = 1000

    plt.axvline(x=carrier_freq, color='red', linestyle='--', alpha=0.7,
                label='Несущая 50 кГц')
    plt.axvline(x=carrier_freq + modulation_freq, color='green', linestyle='--', alpha=0.7,
                label='Боковые полосы')
    plt.axvline(x=carrier_freq - modulation_freq, color='green', linestyle='--', alpha=0.7)

    plt.legend()
    plt.show()


# Пример использования
if __name__ == "__main__":
    # Основной анализ
    plot_tonal_modulation_spectrum('Original(1).txt')

    # Сравнение масштабов
    # plot_comparison_spectrum('samples.txt')

    # Быстрый просмотр
    # quick_tonal_spectrum('samples.txt')