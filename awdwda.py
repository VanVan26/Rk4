import tkinter as tk
from tkinter import ttk, messagebox
import math
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def derivs(state, t, params):
    x, y, vx, vy = state
    rho0, rho1_0, V, eta, k, alpha, H, g, mu, F_thrust, theta = params
    m_t = rho1_0 * V - mu * t
    m_t = max(m_t, 1e-5)
    rho1_t = m_t / V


    Fb = rho0 * V * g  # Архимедова сила
    Fg = rho1_t * V * g  # Сила тяжести
    Fc_x = eta * k * abs(vx)  # Сопротивление по x
    Fc_y = eta * k * (1 + alpha * abs(y) / abs(H)) * abs(vy)  # Сопротивление по y

    Fx_thrust = F_thrust * math.cos(math.radians(theta))
    Fy_thrust = F_thrust * math.sin(math.radians(theta))

    Fx = Fx_thrust - math.copysign(Fc_x, vx)
    Fy = Fy_thrust + (Fb - Fg) - math.copysign(Fc_y, vy)

    dxdt = vx
    dydt = vy
    dvxdt = Fx / m_t
    dvydt = Fy / m_t

    return [dxdt, dydt, dvxdt, dvydt]


def rk4_step(t, state, h, params):
    k1 = derivs(state, t, params)
    st2 = [state[i] + 0.5 * h * k1[i] for i in range(4)]
    k2 = derivs(st2, t + 0.5 * h, params)
    st3 = [state[i] + 0.5 * h * k2[i] for i in range(4)]
    k3 = derivs(st3, t + 0.5 * h, params)
    st4 = [state[i] + h * k3[i] for i in range(4)]
    k4 = derivs(st4, t + h, params)

    new_state = [
        state[i] + (h / 6) * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i])
        for i in range(4)
    ]
    return new_state


def run_simulation():
    try:
        values = {}
        for key, _, _ in param_info:
            val = entries[key].get().strip().replace(",", ".")
            if val == "":
                raise ValueError(f"Параметр '{key}' не задан.")
            values[key] = float(val)

        rho0 = values["rho0"]
        rho1_0 = values["rho1"]
        V = values["V"]
        H = values["H"]
        eta = values["eta"]
        k = values["k"]
        alpha = values["alpha"]
        g = values["g"]
        mu = values["mu"]
        F_thrust = values["F_thrust"]
        theta = values["theta"]
        h = values["h"]
        max_time = values["max_time"]

        state = [0.0, H, 0.0, 0.0]
        t = 0.0
        time_points, x_points, y_points = [t], [state[0]], [state[1]]

        params = (rho0, rho1_0, V, eta, k, alpha, H, g, mu, F_thrust, theta)

        while t < max_time and state[1] < 0:
            state = rk4_step(t, state, h, params)
            t += h
            time_points.append(t)
            x_points.append(state[0])
            y_points.append(state[1])
            print(state[0], state[1], state[2], state[3], t)

        for widget in plot_frame.winfo_children():
            widget.destroy()

        fig = Figure(figsize=(8, 6), dpi=100)
        ax1 = fig.add_subplot(111)
        ax1.plot(x_points, y_points, label='Траектория')
        ax1.axhline(0, color='blue', linestyle='--', label='Поверхность')
        ax1.set_xlabel('x, м')
        ax1.set_ylabel('y (глубина), м')
        ax1.legend()
        ax1.grid(True)

        canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        messagebox.showinfo("Результат", f"Время всплытия: {t:.1f} секунд")

    except Exception as e:
        messagebox.showerror("Ошибка", str(e))


root = tk.Tk()
root.title("Модель всплытия подлодки (реальные параметры)")
root.geometry("1100x650")

main_frame = ttk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
input_frame = ttk.Frame(main_frame)
input_frame.pack(side=tk.LEFT, padx=10)
plot_frame = ttk.Frame(main_frame)
plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

param_info = [
    ("rho0", "Плотность воды, кг/м³", 1025),
    ("rho1", "Плотность лодки, кг/м³", 1025),
    ("V", "Объём лодки, м³", 12250.0),
    ("H", "Начальная глубина, м", -300.0),
    ("eta", "Коэфф. вязкости, Па·с", 0.001),
    ("k", "Коэфф. сопротивления", 1.2),
    ("alpha", "Глубинный коэффициент α", 0.01),
    ("g", "Ускорение свободного падения", 9.81),
    ("mu", "Скорость сброса массы, кг/с", 2000.0),
    ("F_thrust", "Сила тяги, Н", 500000.0),
    ("theta", "Угол тяги, град", 5.0),
    ("h", "Шаг интегрирования, с", 0.01),
    ("max_time", "Макс. время, с", 300.0),
]

entries = {}
for i, (key, label, default) in enumerate(param_info):
    ttk.Label(input_frame, text=label).grid(row=i, column=0, sticky="e", pady=2)
    entry = ttk.Entry(input_frame, width=12)
    entry.insert(0, str(default))
    entry.grid(row=i, column=1, pady=2)
    entries[key] = entry

ttk.Button(input_frame, text="Запустить", command=run_simulation).grid(row=len(param_info), column=0, columnspan=2,
                                                                       pady=10)

root.mainloop()
