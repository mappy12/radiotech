import numpy as np
import matplotlib.pyplot as plt


def read_fsk_experiments(filename):
    """Чтение данных экспериментов FSK"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        with open(filename, 'r', encoding='cp1251') as f:
            content = f.read()

    experiments = []
    sections = content.split('FSK Experiment')

    for section in sections[1:]:  # Пропускаем первый пустой элемент
        lines = section.strip().split('\n')
        if len(lines) < 3:
            continue

        # Извлекаем параметры из заголовка
        header = lines[0]
        params = {}

        # Парсим параметры
        if 'NP=' in header:
            np_val = int(header.split('NP=')[1].split(',')[0])
            params['NP'] = np_val

        data = []
        for line in lines[2:]:  # Пропускаем заголовок и "Frequency..."
            if line.strip() and 'Frequency' not in line:
                parts = line.replace(',', '.').split()
                if len(parts) >= 3:
                    try:
                        freq = float(parts[0])
                        signal = float(parts[1])
                        power = float(parts[2])
                        data.append((freq, signal, power))
                    except:
                        continue

        if data:
            experiments.append({
                'header': header,
                'data': np.array(data),
                'params': params
            })

    return experiments


def plot_fsk_comparison(experiments):
    """Сравнение СПМ для разных скоростей передачи"""
    if not experiments:
        print("Нет данных для построения графиков")
        return

    n_experiments = len(experiments)
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    axes = axes.flatten()

    bandwidths = []

    for idx, exp in enumerate(experiments):
        if idx >= 4:
            break

        data = exp['data']
        freqs = data[:, 0]
        powers = data[:, 2]

        # График СПМ
        axes[idx].plot(freqs, powers, 'b-', linewidth=1)
        axes[idx].set_title(exp['header'][:50] + '...')
        axes[idx].set_xlabel('Частота (Гц)')
        axes[idx].set_ylabel('Мощность')
        axes[idx].grid(True, alpha=0.3)
        axes[idx].set_xlim(40000, 60000)  # Около несущей 50 kHz

        # Вычисление ширины спектра
        peak_power = np.max(powers)
        threshold = peak_power * 0.5  # -3 dB

        mask = (freqs >= 40000) & (freqs <= 60000)
        freqs_filtered = freqs[mask]
        powers_filtered = powers[mask]

        if len(freqs_filtered) > 0:
            above_threshold = powers_filtered >= threshold
            if np.any(above_threshold):
                left_idx = np.where(above_threshold)[0][0]
                right_idx = np.where(above_threshold)[0][-1]
                bandwidth = freqs_filtered[right_idx] - freqs_filtered[left_idx]
                bandwidths.append(bandwidth)

                axes[idx].axvline(freqs_filtered[left_idx], color='red', linestyle='--', alpha=0.7)
                axes[idx].axvline(freqs_filtered[right_idx], color='red', linestyle='--', alpha=0.7)
                axes[idx].text(45000, peak_power * 0.8, f'BW: {bandwidth:.0f} Hz',
                               bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))

    plt.tight_layout()
    plt.show()

    # Анализ влияния скорости передачи
    if bandwidths:
        print("Влияние скорости передачи на ширину спектра:")
        print("NP\tСкорость (симв/сек)\tШирина спектра (Hz)")
        print("-" * 50)
        for i, exp in enumerate(experiments[:len(bandwidths)]):
            np_val = exp['params'].get('NP', 0)
            symbol_rate = 1e6 / np_val if np_val > 0 else 0  # FS = 1 MHz
            print(f"{np_val}\t{symbol_rate:.0f}\t\t\t{bandwidths[i]:.0f}")


def analyze_msk(experiments):
    """Анализ минимальной частотной манипуляции"""
    msk_sections = []
    for exp in experiments:
        if 'MSK' in exp['header'] or 'h=0.5' in exp['header']:
            msk_sections.append(exp)

    if msk_sections:
        msk_data = msk_sections[0]
        freqs = msk_data['data'][:, 0]
        powers = msk_data['data'][:, 2]

        plt.figure(figsize=(12, 6))
        plt.plot(freqs, powers, 'g-', linewidth=1.5)
        plt.title('СПМ минимальной частотной манипуляции (MSK, h=0.5)')
        plt.xlabel('Частота (Гц)')
        plt.ylabel('Мощность')
        plt.grid(True, alpha=0.3)
        plt.xlim(40000, 60000)

        # Анализ ширины спектра MSK
        peak_power = np.max(powers)
        threshold = peak_power * 0.5

        mask = (freqs >= 40000) & (freqs <= 60000)
        freqs_filtered = freqs[mask]
        powers_filtered = powers[mask]

        if len(freqs_filtered) > 0:
            above_threshold = powers_filtered >= threshold
            if np.any(above_threshold):
                left_idx = np.where(above_threshold)[0][0]
                right_idx = np.where(above_threshold)[0][-1]
                bandwidth = freqs_filtered[right_idx] - freqs_filtered[left_idx]

                plt.axvline(freqs_filtered[left_idx], color='red', linestyle='--', alpha=0.7,
                            label=f'Левая граница: {freqs_filtered[left_idx]:.0f} Гц')
                plt.axvline(freqs_filtered[right_idx], color='red', linestyle='--', alpha=0.7,
                            label=f'Правая граница: {freqs_filtered[right_idx]:.0f} Гц')
                plt.legend()

                print(f"\nMSK анализ:")
                print(f"Ширина спектра: {bandwidth:.0f} Hz")
                print(f"Теоретическая ширина для MSK: ~{1.0 / msk_sections[0]['params'].get('NP', 500) * 1e6:.0f} Hz")

        plt.show()


def main():
    print("Исследование влияния скорости передачи на СПМ FSK")
    print("и анализ минимальной частотной манипуляции (MSK)")
    print("=" * 70)

    filename = "fsk_variable_rate.txt"

    try:
        experiments = read_fsk_experiments(filename)
        if experiments:
            print(f"Загружено {len(experiments)} экспериментов")
            plot_fsk_comparison(experiments)
            analyze_msk(experiments)
        else:
            print("Нет данных экспериментов")
    except FileNotFoundError:
        print(f"Файл {filename} не найден")


if __name__ == "__main__":
    main()