import numpy as np
import matplotlib.pyplot as plt


def read_fsk_2ghz_data(filename):
    """Чтение данных FSK-сигнала 2 GHz"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except:
        with open(filename, 'r', encoding='cp1251') as f:
            lines = f.readlines()

    data = []
    for line in lines:
        if 'Frequency' in line or 'Parameters' in line or 'Expected' in line:
            continue
        parts = line.replace(',', '.').split()
        if len(parts) >= 3:
            try:
                freq = float(parts[0])
                signal = float(parts[1])
                power = float(parts[2])
                data.append((freq, signal, power))
            except:
                continue

    return np.array(data)


def plot_fsk_2ghz_signal(data):
    """Построение графиков FSK-сигнала 2 GHz"""
    if len(data) == 0:
        print("Нет данных для построения графиков")
        return

    freqs = data[:, 0]
    signals = data[:, 1]
    powers = data[:, 2]

    # Создаем фигуру с двумя графиками
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))

    # График 1: Сигнал во временной области
    ax1.plot(signals[:5000], 'b-', linewidth=1)
    ax1.set_title('FSK-сигнал с несущей 2 GHz')
    ax1.set_xlabel('Отсчеты времени')
    ax1.set_ylabel('Амплитуда')
    ax1.grid(True, alpha=0.3)

    # График 2: СПМ (область вокруг 2 GHz)
    ax2.plot(freqs, powers, 'r-', linewidth=1)
    ax2.set_title('СПМ FSK-сигнала (2 GHz несущая)')
    ax2.set_xlabel('Частота (Гц)')
    ax2.set_ylabel('Мощность')
    ax2.grid(True, alpha=0.3)

    # Фокусируемся на области вокруг 2 GHz
    ax2.set_xlim(1.9e9, 2.1e9)  # 1.9 GHz - 2.1 GHz
    ax2.set_ylim(0, 0.07)

    plt.tight_layout()
    plt.show()

    # Анализ спектра
    print("Анализ FSK спектра 2 GHz:")
    print("Ожидаемые частоты:")
    print(f"Символ '0': {2e9 + 20000} Гц (2 GHz + 20 kHz)")
    print(f"Символ '1': {2e9 + 40000} Гц (2 GHz + 40 kHz)")
    print(f"Расстояние между символами: {40000 - 20000} Hz")


def calculate_bandwidth_2ghz(data):
    """Вычисление ширины спектра для 2 GHz сигнала"""
    if len(data) == 0:
        return

    freqs = data[:, 0]
    powers = data[:, 2]

    # Фильтруем только область вокруг 2 GHz
    mask = (freqs >= 1.9e9) & (freqs <= 2.1e9)
    freqs_filtered = freqs[mask]
    powers_filtered = powers[mask]

    if len(freqs_filtered) == 0:
        print("Нет данных в диапазоне 1.9-2.1 GHz")
        return

    # Находим пиковую мощность
    peak_power = np.max(powers_filtered)
    threshold_power = peak_power * 0.5  # -3 dB уровень

    # Находим границы
    left_idx = np.where(powers_filtered >= threshold_power)[0][0]
    right_idx = np.where(powers_filtered >= threshold_power)[0][-1]

    left_freq = freqs_filtered[left_idx]
    right_freq = freqs_filtered[right_idx]
    bandwidth = right_freq - left_freq

    print(f"\nШирина спектра (-3 dB): {bandwidth:.0f} Hz")
    print(f"Левая граница: {left_freq:.0f} Hz")
    print(f"Правая граница: {right_freq:.0f} Hz")

    return bandwidth


def main():
    print("Анализ частотной манипуляции с несущей 2 GHz")
    print("=" * 55)

    filename = "fsk_modulation_2Ghz(2_2).txt"

    try:
        data = read_fsk_2ghz_data(filename)
        if len(data) > 0:
            print(f"Загружено {len(data)} точек данных")
            plot_fsk_2ghz_signal(data)
            calculate_bandwidth_2ghz(data)
        else:
            print("В файле нет данных")
    except FileNotFoundError:
        print(f"Файл {filename} не найден")
        print("Сначала запустите C++ программу")


if __name__ == "__main__":
    main()