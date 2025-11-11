import numpy as np
import matplotlib.pyplot as plt


def read_fsk_4ghz_data(filename):
    """Чтение данных FSK-сигнала 4 GHz"""
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


def plot_fsk_4ghz_signal(data):
    """Построение графиков FSK-сигнала 4 GHz"""
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
    ax1.set_title('FSK-сигнал с несущей 4 GHz')
    ax1.set_xlabel('Отсчеты времени')
    ax1.set_ylabel('Амплитуда')
    ax1.grid(True, alpha=0.3)

    # График 2: СПМ (область вокруг 4 GHz)
    ax2.plot(freqs, powers, 'r-', linewidth=1)
    ax2.set_title('СПМ FSK-сигнала (4 GHz несущая)')
    ax2.set_xlabel('Частота (Гц)')
    ax2.set_ylabel('Мощность')
    ax2.grid(True, alpha=0.3)

    # Фокусируемся на области вокруг 4 GHz
    ax2.set_xlim(3.9e9, 4.1e9)  # 3.9 GHz - 4.1 GHz
    ax2.set_ylim(0, 0.07)

    plt.tight_layout()
    plt.show()

    # Анализ спектра
    print("Анализ FSK спектра 4 GHz:")
    print("Ожидаемые частоты:")
    print(f"Символ '0': {4e9 + 20000:.0f} Гц (4 GHz + 20 kHz)")
    print(f"Символ '1': {4e9 + 40000:.0f} Гц (4 GHz + 40 kHz)")
    print(f"Расстояние между символами: {40000 - 20000} Hz")


def calculate_bandwidth_4ghz(data):
    """Вычисление ширины спектра для 4 GHz сигнала"""
    if len(data) == 0:
        return

    freqs = data[:, 0]
    powers = data[:, 2]

    # Фильтруем только область вокруг 4 GHz
    mask = (freqs >= 3.9e9) & (freqs <= 4.1e9)
    freqs_filtered = freqs[mask]
    powers_filtered = powers[mask]

    if len(freqs_filtered) == 0:
        print("Нет данных в диапазоне 3.9-4.1 GHz")
        return

    # Находим пиковую мощность
    peak_power = np.max(powers_filtered)
    threshold_power = peak_power * 0.5  # -3 dB уровень

    # Находим границы
    above_threshold = powers_filtered >= threshold_power
    if np.any(above_threshold):
        left_idx = np.where(above_threshold)[0][0]
        right_idx = np.where(above_threshold)[0][-1]

        left_freq = freqs_filtered[left_idx]
        right_freq = freqs_filtered[right_idx]
        bandwidth = right_freq - left_freq

        print(f"\nШирина спектра (-3 dB): {bandwidth:.0f} Hz ({bandwidth / 1000:.1f} kHz)")
        print(f"Левая граница: {left_freq:.0f} Hz")
        print(f"Правая граница: {right_freq:.0f} Hz")

        # Дополнительный анализ с -6 dB
        threshold_power_6db = peak_power * 0.25  # -6 dB уровень
        above_threshold_6db = powers_filtered >= threshold_power_6db
        if np.any(above_threshold_6db):
            left_idx_6db = np.where(above_threshold_6db)[0][0]
            right_idx_6db = np.where(above_threshold_6db)[0][-1]
            bandwidth_6db = freqs_filtered[right_idx_6db] - freqs_filtered[left_idx_6db]
            print(f"Ширина спектра (-6 dB): {bandwidth_6db:.0f} Hz ({bandwidth_6db / 1000:.1f} kHz)")

        return bandwidth
    else:
        print("Не удалось определить границы спектра")
        return None


def compare_bandwidths():
    """Сравнение ширины спектра для разных несущих частот"""
    frequencies = [1e9, 2e9, 4e9]
    bandwidths = []

    for freq in frequencies:
        filename = f"fsk_{int(freq / 1e9)}ghz.txt"
        try:
            data = read_fsk_4ghz_data(filename)  # Используем ту же функцию чтения
            if len(data) > 0:
                print(f"\n--- Анализ для {int(freq / 1e9)} GHz ---")
                bw = calculate_bandwidth_4ghz(data)
                if bw:
                    bandwidths.append(bw)
        except FileNotFoundError:
            print(f"Файл {filename} не найден")

    if bandwidths:
        print(f"\nСравнение ширины спектра:")
        for i, (freq, bw) in enumerate(zip(frequencies[:len(bandwidths)], bandwidths)):
            print(f"{int(freq / 1e9)} GHz: {bw / 1000:.1f} kHz")


def main():
    print("Анализ частотной манипуляции с несущей 4 GHz")
    print("=" * 55)

    filename = "fsk_modulation_4Ghz(2_2).txt"

    try:
        data = read_fsk_4ghz_data(filename)
        if len(data) > 0:
            print(f"Загружено {len(data)} точек данных")
            plot_fsk_4ghz_signal(data)
            calculate_bandwidth_4ghz(data)

            # Сравнение с другими частотами
            print("\n" + "=" * 50)
            compare_bandwidths()
        else:
            print("В файле нет данных")
    except FileNotFoundError:
        print(f"Файл {filename} не найден")
        print("Сначала запустите C++ программу")


if __name__ == "__main__":
    main()