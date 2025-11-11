import numpy as np
import matplotlib.pyplot as plt


def plot_am_spectrum(filename):
    """
    Построение спектра АМ сигнала из файла данных
    """
    # Читаем данные из файла
    data = np.loadtxt(filename, delimiter='\t')

    # Извлекаем столбцы
    frequencies = data[:, 0]  # Частота в Гц
    amplitude = data[:, 1]  # Амплитуда сигнала
    power = data[:, 2]  # Мощность (спектральная плотность)

    # Основные параметры из твоего C++ кода
    fs = 1e6  # Частота дискретизации 1 МГц
    fc = 50000  # Несущая частота 50 кГц
    f_mod = 1000  # Частота модуляции 1 кГц

    # Строим графики
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))

    # 1. Сигнал во временной области (первые 1000 отсчетов)
    n_show = min(1000, len(amplitude))
    time_axis = np.arange(n_show) / fs * 1000  # время в мс
    ax1.plot(time_axis, amplitude[:n_show], 'b-', linewidth=1)
    ax1.set_xlabel('Время (мс)')
    ax1.set_ylabel('Амплитуда')
    ax1.set_title('АМ сигнал во временной области')
    ax1.grid(True, alpha=0.3)

    # 2. Спектр мощности (полный диапазон)
    n_half = len(frequencies) // 2
    ax2.plot(frequencies[:n_half], power[:n_half], 'r-', linewidth=1)
    ax2.set_xlabel('Частота (Гц)')
    ax2.set_ylabel('Мощность')
    ax2.set_title('Спектр мощности АМ сигнала')
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim(0, 100000)  # До 100 кГц

    # 3. Спектр мощности вокруг несущей (детальный вид)
    mask = (frequencies[:n_half] >= fc - 5000) & (frequencies[:n_half] <= fc + 5000)
    ax3.plot(frequencies[:n_half][mask], power[:n_half][mask], 'g-', linewidth=2)
    ax3.set_xlabel('Частота (Гц)')
    ax3.set_ylabel('Мощность')
    ax3.set_title('Детальный вид вокруг несущей 50 кГц')
    ax3.grid(True, alpha=0.3)

    # Отмечаем несущую и боковые полосы
    ax3.axvline(x=fc, color='red', linestyle='--', alpha=0.7, label='Несущая 50 кГц')
    ax3.axvline(x=fc + f_mod, color='orange', linestyle='--', alpha=0.7, label='Боковые ±1 кГц')
    ax3.axvline(x=fc - f_mod, color='orange', linestyle='--', alpha=0.7)
    ax3.legend()

    # 4. Спектр в логарифмическом масштабе (дБ)
    power_db = 10 * np.log10(np.maximum(power[:n_half], 1e-20))
    ax4.plot(frequencies[:n_half], power_db, 'purple', linewidth=1)
    ax4.set_xlabel('Частота (Гц)')
    ax4.set_ylabel('Мощность (дБ)')
    ax4.set_title('Спектр мощности в дБ')
    ax4.grid(True, alpha=0.3)
    ax4.set_xlim(0, 100000)

    plt.tight_layout()
    plt.show()

    # Анализ характеристик
    print("\n" + "=" * 50)
    print("АНАЛИЗ СПЕКТРА АМ СИГНАЛА")
    print("=" * 50)

    # Находим несущую и боковые полосы
    carrier_idx = np.argmin(np.abs(frequencies[:n_half] - fc))
    upper_idx = np.argmin(np.abs(frequencies[:n_half] - (fc + f_mod)))
    lower_idx = np.argmin(np.abs(frequencies[:n_half] - (fc - f_mod)))

    carrier_power = power[:n_half][carrier_idx]
    upper_power = power[:n_half][upper_idx]
    lower_power = power[:n_half][lower_idx]

    print(f"Несущая частота ({fc} Гц): {carrier_power:.2e}")
    print(f"Верхняя боковая ({fc + f_mod} Гц): {upper_power:.2e}")
    print(f"Нижняя боковая ({fc - f_mod} Гц): {lower_power:.2e}")

    # Коэффициент модуляции
    if carrier_power > 0:
        m = np.sqrt(2 * (upper_power + lower_power) / carrier_power)
        print(f"Коэффициент модуляции: {m:.3f} ({m * 100:.1f}%)")
        print(f"Ожидаемый: 0.750 (75.0%)")


# Использование:
# Убедись, что файл с данными называется 'samples.txt' и лежит в той же папке
plot_am_spectrum('start(2_1).txt')