import numpy as np
import matplotlib.pyplot as plt


def read_fsk_1ghz_data(filename):
    """Чтение данных FSK-сигнала 1 GHz"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except:
        with open(filename, 'r', encoding='cp1251') as f:
            lines = f.readlines()

    data = []
    for line in lines:
        if 'Frequency' in line or 'Parameters' in line:
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


def plot_fsk_1ghz_signal(data):
    """Построение графиков FSK-сигнала 1 GHz"""
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
    ax1.set_title('FSK-сигнал с несущей 1 GHz')
    ax1.set_xlabel('Отсчеты времени')
    ax1.set_ylabel('Амплитуда')
    ax1.grid(True, alpha=0.3)

    # График 2: СПМ (увеличиваем область вокруг 1 GHz)
    ax2.plot(freqs, powers, 'r-', linewidth=1)
    ax2.set_title('СПМ FSK-сигнала (1 GHz несущая)')
    ax2.set_xlabel('Частота (Гц)')
    ax2.set_ylabel('Мощность')
    ax2.grid(True, alpha=0.3)

    # Фокусируемся на области вокруг 1 GHz как на скриншоте
    ax2.set_xlim(0.899e9, 1.1e9)  # 899 МГц - 1.1 GHz
    ax2.set_ylim(0, 0.07)  # По скриншоту максимум ~0.07

    plt.tight_layout()
    plt.show()

    # Анализ спектра
    print("Анализ FSK спектра 1 GHz:")
    print("Должны наблюдаться два пика на частотах:")
    print(f"Символ '0': {1e9 + 20000} Гц (1 GHz + 20 kHz)")
    print(f"Символ '1': {1e9 + 40000} Гц (1 GHz + 40 kHz)")


import numpy as np
import matplotlib.pyplot as plt


def calculate_bandwidth(freqs, powers, threshold_db=-3):
    """Автоматическое вычисление ширины спектра"""

    # Находим пиковую мощность
    peak_power = np.max(powers)
    peak_freq = freqs[np.argmax(powers)]

    # Преобразуем в dB если нужно
    if threshold_db < 0:
        threshold_power = peak_power * (10 ** (threshold_db / 10))
    else:
        threshold_power = threshold_db

    print(f"Пиковая мощность: {peak_power:.2e} на частоте {peak_freq:.0f} Гц")
    print(f"Пороговый уровень ({threshold_db} dB): {threshold_power:.2e}")

    # Находим границы спектра
    left_bound = None
    right_bound = None

    # Левая граница (до пика)
    for i in range(np.argmax(powers), 0, -1):
        if powers[i] <= threshold_power:
            left_bound = freqs[i]
            break

    # Правая граница (после пика)
    for i in range(np.argmax(powers), len(powers)):
        if powers[i] <= threshold_power:
            right_bound = freqs[i]
            break

    if left_bound and right_bound:
        bandwidth = right_bound - left_bound
        print(f"Левая граница: {left_bound:.0f} Гц")
        print(f"Правая граница: {right_bound:.0f} Гц")
        print(f"Ширина спектра: {bandwidth:.0f} Гц")
        return bandwidth, left_bound, right_bound
    else:
        print("Не удалось определить границы спектра")
        return None, None, None


def plot_with_bandwidth(freqs, powers, threshold_db=-3):
    """Построение графика с выделенной шириной спектра"""

    bandwidth, left_bound, right_bound = calculate_bandwidth(freqs, powers, threshold_db)

    plt.figure(figsize=(12, 6))
    plt.plot(freqs, powers, 'b-', linewidth=1, label='СПМ')

    if left_bound and right_bound:
        # Выделяем ширину спектра
        mask = (freqs >= left_bound) & (freqs <= right_bound)
        plt.fill_between(freqs[mask], 0, powers[mask], alpha=0.3, color='red',
                         label=f'Ширина спектра: {bandwidth:.0f} Гц')

        # Линии границ
        plt.axvline(left_bound, color='red', linestyle='--', alpha=0.7, linewidth=1)
        plt.axvline(right_bound, color='red', linestyle='--', alpha=0.7, linewidth=1)

        # Подписи
        plt.text(left_bound, np.max(powers) * 0.8, f'{left_bound:.0f} Гц',
                 rotation=90, ha='right')
        plt.text(right_bound, np.max(powers) * 0.8, f'{right_bound:.0f} Гц',
                 rotation=90, ha='left')

    peak_power = np.max(powers)
    threshold_power = peak_power * (10 ** (threshold_db / 10))
    plt.axhline(threshold_power, color='green', linestyle=':',
                label=f'Порог {threshold_db} dB')

    plt.title('Определение ширины спектра')
    plt.xlabel('Частота (Гц)')
    plt.ylabel('Мощность')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.ylim(0, peak_power * 1.1)
    plt.show()

    return bandwidth


# Пример использования с вашими данными
def analyze_fsk_bandwidth():
    """Анализ ширины спектра FSK сигнала"""

    data = read_fsk_1ghz_data("fsk_modulation_1Ghz(2_2).txt")
    if len(data) == 0:
        print("Нет данных для анализа")
        return

    freqs = data[:, 0]
    powers = data[:, 2]

    print("Анализ ширины спектра FSK сигнала")
    print("=" * 40)

    # Анализ с разными порогами
    for threshold in [-3, -6, -20]:
        print(f"\n--- Порог {threshold} dB ---")
        bandwidth = plot_with_bandwidth(freqs, powers, threshold)

        if bandwidth:
            print(f"Итоговая ширина спектра: {bandwidth / 1000:.1f} kHz")


def main():
    print("Анализ частотной манипуляции с несущей 1 GHz")
    print("=" * 55)

    filename = "fsk_modulation_1Ghz(2_2).txt"

    try:
        data = read_fsk_1ghz_data(filename)
        if len(data) > 0:
            print(f"Загружено {len(data)} точек данных")
            plot_fsk_1ghz_signal(data)
        else:
            print("В файле нет данных")
    except FileNotFoundError:
        print(f"Файл {filename} не найден")
        print("Сначала запустите C++ программу")


if __name__ == "__main__":
    main()
    analyze_fsk_bandwidth()