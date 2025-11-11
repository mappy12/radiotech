import numpy as np
import matplotlib.pyplot as plt


def read_quadrature_data(filename):
    """Чтение данных квадратурной модуляции"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except:
        with open(filename, 'r', encoding='cp1251') as f:
            lines = f.readlines()

    data = []
    for line in lines:
        if 'Frequency' in line:
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


def plot_quadrature_spm(data):
    """Построение графика СПМ квадратурной модуляции"""
    if len(data) == 0:
        print("Нет данных для построения графиков")
        return

    freqs = data[:, 0]
    signals = data[:, 1]
    powers = data[:, 2]

    # Создаем фигуру с двумя графиками
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

    # График 1: Сигнал во временной области
    ax1.plot(signals[:2000], 'b-', linewidth=1)
    ax1.set_title('Квадратурный сигнал (временная область)')
    ax1.set_xlabel('Отсчеты времени')
    ax1.set_ylabel('Амплитуда')
    ax1.grid(True, alpha=0.3)

    # График 2: СПМ - отношение линейной мощности к частоте
    ax2.plot(freqs, powers, 'r-', linewidth=1)
    ax2.set_title('СПМ квадратурной модуляции')
    ax2.set_xlabel('Частота (Гц)')
    ax2.set_ylabel('Линейная мощность')
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()

    # Анализ ширины спектра
    if len(data) > 0:
        # Фильтруем область вокруг несущей частоты 50 kHz
        mask = (freqs >= 30000) & (freqs <= 70000)
        freqs_filtered = freqs[mask]
        powers_filtered = powers[mask]

        if len(freqs_filtered) > 0:
            peak_power = np.max(powers_filtered)
            threshold = peak_power * 0.5  # -3 dB уровень

            above_threshold = powers_filtered >= threshold
            if np.any(above_threshold):
                left_idx = np.where(above_threshold)[0][0]
                right_idx = np.where(above_threshold)[0][-1]
                bandwidth = freqs_filtered[right_idx] - freqs_filtered[left_idx]

                print(f"Ширина спектра квадратурной модуляции: {bandwidth:.0f} Hz")
                print(f"Левая граница: {freqs_filtered[left_idx]:.0f} Hz")
                print(f"Правая граница: {freqs_filtered[right_idx]:.0f} Hz")

                # Дополнительный анализ с -6 dB
                threshold_6db = peak_power * 0.25
                above_threshold_6db = powers_filtered >= threshold_6db
                if np.any(above_threshold_6db):
                    left_idx_6db = np.where(above_threshold_6db)[0][0]
                    right_idx_6db = np.where(above_threshold_6db)[0][-1]
                    bandwidth_6db = freqs_filtered[right_idx_6db] - freqs_filtered[left_idx_6db]
                    print(f"Ширина спектра (-6 dB): {bandwidth_6db:.0f} Hz")


def main():
    print("Анализ квадратурной модуляции")
    print("=" * 40)

    filename = "quadrature_modulation_20(3_1).txt"

    try:
        data = read_quadrature_data(filename)
        if len(data) > 0:
            print(f"Загружено {len(data)} точек данных")
            plot_quadrature_spm(data)
        else:
            print("В файле нет данных")
    except FileNotFoundError:
        print(f"Файл {filename} не найден")
        print("Сначала запустите C++ программу")


if __name__ == "__main__":
    main()