import numpy as np
import matplotlib.pyplot as plt

k = 0.0

#k = 1.0
#k = 0.5
#k = 0.25
#k = 0.1
#k = 0.0

def read_data(filename):
    """Чтение данных из файла"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except:
        try:
            with open(filename, 'r', encoding='cp1251') as f:
                lines = f.readlines()
        except:
            with open(filename, 'r', encoding='latin-1') as f:
                lines = f.readlines()

    data = []
    for line in lines:
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


def plot_balance_modulation(data):
    """Построение двух графиков балансной модуляции"""
    if len(data) == 0:
        print("Нет данных для построения графика")
        return

    freqs = data[:, 0]
    signals = data[:, 1]
    powers = data[:, 2]

    # Создаем фигуру с двумя subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

    # График 1: Сигнал после балансной модуляции (первые 2000 точек)
    ax1.plot(signals[:2000], 'b-', linewidth=1)
    ax1.set_title(f'Сигнал после балансной модуляции (k={k})')
    ax1.set_xlabel('Отсчеты времени')
    ax1.set_ylabel('Амплитуда')
    ax1.grid(True, alpha=0.3)

    # График 2: СПМ - отношение линейной мощности к частоте
    ax2.plot(freqs, powers, 'r-', linewidth=1)
    ax2.set_title(f'СПМ балансной модуляции (k={k})')
    ax2.set_xlabel('Частота (Гц)')
    ax2.set_ylabel('Линейная мощность')
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()


def main():
    print(f"Балансная модуляция с k={k}")
    print("=" * 40)

    filename = "balance_modulation_k=0(1_6).txt"

    try:
        data = read_data(filename)
        if len(data) > 0:
            print(f"Прочитано {len(data)} точек данных")
            plot_balance_modulation(data)
        else:
            print("В файле нет данных")
    except FileNotFoundError:
        print(f"Файл {filename} не найден")


if __name__ == "__main__":
    main()