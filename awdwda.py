import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Расчётные функции
def f1(y, z):
    return z

def f2(y, z, rho0, rho1, V, eta, k, alpha, H, g):
    Fb = g * (rho0 / rho1 - 1)
    Fc = (eta * k) / (rho1 * V) * (1 + alpha * abs(y) / abs(H)) * z
    return Fb - Fc

def rk4_step(t, x, y, z, h, v, params):
    rho0, rho1, V, eta, k, alpha, H, g = params
    k1_y = h * f1(y, z)
    k1_z = h * f2(y, z, rho0, rho1, V, eta, k, alpha, H, g)

    k2_y = h * f1(y + k1_y / 2, z + k1_z / 2)
    k2_z = h * f2(y + k1_y / 2, z + k1_z / 2, rho0, rho1, V, eta, k, alpha, H, g)

    k3_y = h * f1(y + k2_y / 2, z + k2_z / 2)
    k3_z = h * f2(y + k2_y / 2, z + k2_z / 2, rho0, rho1, V, eta, k, alpha, H, g)

    k4_y = h * f1(y + k3_y, z + k3_z)
    k4_z = h * f2(y + k3_y, z + k3_z, rho0, rho1, V, eta, k, alpha, H, g)

    y_new = y + (k1_y + 2 * k2_y + 2 * k3_y + k4_y) / 6
    z_new = z + (k1_z + 2 * k2_z + 2 * k3_z + k4_z) / 6
    x_new = x + v * h

    return t + h, x_new, y_new, z_new

def run_simulation():
    try:
        # Сбор параметров
        values = {}
        for key, _, _ in param_info:
            val_str = entries[key].get().strip().replace(",", ".")
            if val_str == "":
                raise ValueError(f"Параметр '{key}' не задан.")
            values[key] = float(val_str)

        # Проверки реалистичности значений
        if not (800 <= values["rho0"] <= 1200):
            raise ValueError("Плотность воды должна быть в диапазоне 800–1200 кг/м³.")
        if not (800 <= values["rho1"] <= 2000):
            raise ValueError("Плотность лодки должна быть в диапазоне 800–2000 кг/м³.")
        if not (0.01 <= values["V"] <= 100):
            raise ValueError("Объём лодки должен быть в диапазоне 0.01–100 м³.")
        if values["H"] >= 0:
            raise ValueError("Начальная глубина должна быть отрицательной (под водой).")
        if not (0.00001 <= values["eta"] <= 1):
            raise ValueError("Коэффициент вязкости должен быть от 0.00001 до 1 Па·с.")
        if not (0.1 <= values["k"] <= 100):
            raise ValueError("Коэффициент сопротивления должен быть от 0.1 до 100.")
        if not (0 <= values["alpha"] <= 100):
            raise ValueError("Глубинный коэффициент должен быть от 0 до 100.")
        if not (9 <= values["g"] <= 10):
            raise ValueError("Ускорение свободного падения должно быть около 9.81 м/с².")
        if not (0.1 <= values["v"] <= 100):
            raise ValueError("Горизонтальная скорость должна быть в диапазоне 0.1–100 м/с.")
        if not (0.0001 <= values["h"] <= 1.0):
            raise ValueError("Шаг интегрирования должен быть от 0.001 до 1.0 с.")
        if not (1 <= values["max_time"] <= 10000):
            raise ValueError("Максимальное время расчёта должно быть от 1 до 10000 с.")

        # Извлечение
        rho0 = values["rho0"]
        rho1 = values["rho1"]
        V = values["V"]
        H = values["H"]
        eta = values["eta"]
        k = values["k"]
        alpha = values["alpha"]
        g = values["g"]
        v = values["v"]
        h = values["h"]
        max_time = values["max_time"]

        # Начальные условия
        y0, z0, t0, x0 = H, 0, 0, 0
        t, x, y, z = t0, x0, y0, z0
        time_points = [t]
        x_points = [x]
        y_points = [y]
        velocity_points = [z]

        params = (rho0, rho1, V, eta, k, alpha, H, g)

        while t < max_time:
            t, x, y, z = rk4_step(t, x, y, z, h, v, params)
            time_points.append(t)
            x_points.append(x)
            y_points.append(y)
            velocity_points.append(z)
            if y >= 0:
                print(t, y, x, z)
                break

        # Очистка графика
        for widget in plot_frame.winfo_children():
            widget.destroy()

        fig = Figure(figsize=(6, 5), dpi=100)
        ax = fig.add_subplot(111)
        ax.plot(x_points, y_points, color='green', linewidth=2.5, label='Траектория лодки')
        ax.axhline(0, color='blue', linestyle='--', linewidth=2, label='Поверхность воды')
        ax.set_title("Траектория всплытия", fontsize=14, fontweight='bold')
        ax.set_xlabel("Горизонтальное расстояние, м")
        ax.set_ylabel("Глубина, м")
        ax.grid(True, linestyle='--', alpha=0.5)
        ax.legend()

        canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    except ValueError as ve:
        messagebox.showerror("Ошибка валидации", str(ve))
    except Exception as e:
        messagebox.showerror("Ошибка", f"Произошла ошибка: {e}")

# Окно
root = tk.Tk()
root.title("Модель всплытия подводной лодки")
root.geometry("1000x600")
root.configure(bg="#f0f0f0")

# Стилизация ttk
style = ttk.Style(root)
style.theme_use("clam")
style.configure("TLabel", font=("Segoe UI", 10), background="#f0f0f0")
style.configure("TEntry", font=("Segoe UI", 10))
style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=6)

# Основная рамка
main_frame = ttk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

input_frame = ttk.Frame(main_frame)
input_frame.pack(side=tk.LEFT, padx=10, pady=10, anchor='n')

plot_frame = ttk.Frame(main_frame)
plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

# Параметры
param_info = [
    ("rho0", "Плотность воды (кг/м³)", 1025),
    ("rho1", "Плотность лодки (кг/м³)", 1000),
    ("V", "Объем лодки (м³)", 100.0),
    ("H", "Начальная глубина (м)", -50),
    ("eta", "Коэфф. вязкости (Па·с)", 0.001),
    ("k", "Коэфф. сопротивления", 0.5),
    ("alpha", "Глубинный коэфф.", 0.01),
    ("g", "Ускорение g (м/с²)", 9.81),
    ("v", "Гор. скорость (м/с)", 4),
    ("h", "Шаг интегрирования (с)", 0.1),
    ("max_time", "Макс. время расчета (с)", 1000),
]

entries = {}
for i, (key, label_text, default) in enumerate(param_info):
    label = ttk.Label(input_frame, text=label_text)
    label.grid(row=i, column=0, sticky="e", pady=3)
    entry = ttk.Entry(input_frame, width=15)
    entry.insert(0, str(default))
    entry.grid(row=i, column=1, pady=3, padx=5)
    entries[key] = entry

run_button = ttk.Button(input_frame, text="Построить график", command=run_simulation)
run_button.grid(row=len(param_info), column=0, columnspan=2, pady=15)

root.mainloop()
