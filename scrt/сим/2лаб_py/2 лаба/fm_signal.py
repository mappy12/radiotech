import numpy as np
import matplotlib.pyplot as plt


def read_fm_data(filename):
    """Чтение данных ЧМ-сигнала"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except:
        with open(filename, 'r', encoding='cp1251') as f:
            lines = f.readlines()

    data = []
    for line in lines:
        if 'Frequency' in line or 'Parameters' in line or 'Bandwidth' in line:
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


def plot_fm_signal(data, m_value):
    """Построение графиков ЧМ-сигнала"""
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
    ax1.set_title(f'ЧМ-сигнал (m = {m_value})')
    ax1.set_xlabel('Отсчеты времени')
    ax1.set_ylabel('Амплитуда')
    ax1.grid(True, alpha=0.3)

    # График 2: СПМ
    ax2.plot(freqs, powers, 'r-', linewidth=1)
    ax2.set_title(f'СПМ ЧМ-сигнала (m = {m_value})')
    ax2.set_xlabel('Частота (Гц)')
    ax2.set_ylabel('Мощность')
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim(1.8e6, 2.2e6)  # Около несущей 2 МГц

    plt.tight_layout()
    plt.show()

    # Анализ ширины спектра
    total_power = np.sum(powers)
    cumulative_power = np.cumsum(powers)
    idx_90 = np.where(cumulative_power >= 0.9 * total_power)[0]

    if len(idx_90) > 0:
        bandwidth_90 = freqs[idx_90[0]]
        print(f"Ширина полосы (90% мощности): {bandwidth_90:.0f} Гц")

    # Теоретическая ширина спектра
    theoretical_bw = 2 * (m_value * 10 + 10)  # 2*(m*FMOD + FMOD)
    print(f"Теоретическая ширина спектра: ~{theoretical_bw:.0f} Гц")


def main():
    print("Анализ ЧМ-модуляции")
    print("=" * 40)

    # Автоматически ищем файл с любым значением m
    import glob
    import re

    fm_files = glob.glob("fm_signal_m_10000_FMOD2.txt")

    if fm_files:
        for filename in fm_files:
            # Извлекаем значение m из имени файла
            match = re.search(r'm_([0-9.]+)', filename)
            if match:
                m_value = float(match.group(1))
                print(f"Найден файл: {filename} (m = {m_value})")

                data = read_fm_data(filename)
                if len(data) > 0:
                    print(f"Загружено {len(data)} точек данных")
                    plot_fm_signal(data, m_value)
                    break
    else:
        print("Файлы ЧМ-сигнала не найдены")
        print("Сначала запустите C++ программу")


if __name__ == "__main__":
    main()