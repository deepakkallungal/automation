import subprocess
import platform
import time
import threading
import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt


def ping(host):
    """Ping the given host once and return the response time in milliseconds."""
    param = "-n" if platform.system().lower() == "windows" else "-c"
    command = ["ping", param, "1", host]
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, universal_newlines=True)
        if platform.system().lower() == "windows":
            idx = output.find("time=")
            if idx != -1:
                return float(output[idx + 5:output.find("ms", idx)])
        else:
            idx = output.find("time=")
            if idx != -1:
                return float(output[idx + 5:output.find(" ms", idx)])
    except subprocess.CalledProcessError:
        return None
    return None


def format_elapsed(seconds):
    """Convert seconds into HH:MM:SS format."""
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hrs:02d}:{mins:02d}:{secs:02d}"


def live_dual_ping_plot(hosts):
    """Continuously ping two hosts and display live results in two stacked graphs."""
    plt.ion()
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    plt.subplots_adjust(hspace=0.4)

    x_data_1, y_data_1 = [], []
    x_data_2, y_data_2 = [], []
    seq = 0
    orange_1 = red_1 = orange_2 = red_2 = 0
    start_time = time.time()

    print(f"\nStarting continuous ping to {hosts[0]} and {hosts[1]} (Close graph window to stop)\n")

    try:
        while plt.fignum_exists(fig.number):
            seq += 1
            elapsed = format_elapsed(time.time() - start_time)

            # Ping both hosts
            response_1 = ping(hosts[0])
            response_2 = ping(hosts[1])

            # Handle first host
            if response_1 is not None:
                y_data_1.append(response_1)
                if response_1 > 200:
                    red_1 += 1
                elif response_1 > 150:
                    orange_1 += 1
            else:
                y_data_1.append(None)

            # Handle second host
            if response_2 is not None:
                y_data_2.append(response_2)
                if response_2 > 200:
                    red_2 += 1
                elif response_2 > 150:
                    orange_2 += 1
            else:
                y_data_2.append(None)

            x_data_1.append(seq)
            x_data_2.append(seq)

            # --- Update first plot (host 1) ---
            ax1.clear()
            ax1.set_title(
                f"{hosts[0]} | Orange (>150ms): {orange_1} | Red (>200ms): {red_1} | Time Elapsed: {elapsed}"
            )
            ax1.set_xlabel("Ping Sequence")
            ax1.set_ylabel("Time (ms)")
            ax1.grid(True)
            ax1.plot(x_data_1, y_data_1, color="blue", linestyle="-", marker="o", markersize=4)
            for i, t in zip(x_data_1, y_data_1):
                if t is None:
                    continue
                if t > 200:
                    ax1.plot(i, t, marker="o", color="red", markersize=8)
                elif t > 150:
                    ax1.plot(i, t, marker="o", color="orange", markersize=8)
            ax1.set_xlim(left=0, right=max(10, seq + 5))
            if any(y for y in y_data_1 if y):
                ax1.set_ylim(bottom=0, top=max(250, max(y for y in y_data_1 if y is not None) + 50))

            # --- Update second plot (host 2) ---
            ax2.clear()
            ax2.set_title(
                f"{hosts[1]} | Orange (>150ms): {orange_2} | Red (>200ms): {red_2} | Time Elapsed: {elapsed}"
            )
            ax2.set_xlabel("Ping Sequence")
            ax2.set_ylabel("Time (ms)")
            ax2.grid(True)
            ax2.plot(x_data_2, y_data_2, color="green", linestyle="-", marker="o", markersize=4)
            for i, t in zip(x_data_2, y_data_2):
                if t is None:
                    continue
                if t > 200:
                    ax2.plot(i, t, marker="o", color="red", markersize=8)
                elif t > 150:
                    ax2.plot(i, t, marker="o", color="orange", markersize=8)
            ax2.set_xlim(left=0, right=max(10, seq + 5))
            if any(y for y in y_data_2 if y):
                ax2.set_ylim(bottom=0, top=max(250, max(y for y in y_data_2 if y is not None) + 50))

            plt.pause(1)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        plt.ioff()
        plt.show()


def start_monitoring(ip1, ip2):
    """Start the monitoring in a background thread."""
    if not ip1 or not ip2:
        messagebox.showerror("Error", "Please enter both IP addresses!")
        return

    threading.Thread(target=live_dual_ping_plot, args=((ip1, ip2),), daemon=True).start()


def create_gui():
    """Create the Tkinter GUI."""
    root = tk.Tk()
    root.title("Dual Ping Monitor")
    root.geometry("400x230")
    root.resizable(False, False)

    tk.Label(root, text="Enter First IP Address:", font=("Arial", 10)).pack(pady=5)
    ip1_entry = tk.Entry(root, width=30, font=("Arial", 10))
    ip1_entry.insert(0, "8.8.8.8")
    ip1_entry.pack(pady=5)

    tk.Label(root, text="Enter Second IP Address:", font=("Arial", 10)).pack(pady=5)
    ip2_entry = tk.Entry(root, width=30, font=("Arial", 10))
    ip2_entry.insert(0, "192.168.29.1")
    ip2_entry.pack(pady=5)

    def on_start():
        ip1 = ip1_entry.get().strip()
        ip2 = ip2_entry.get().strip()
        if not ip1 or not ip2:
            messagebox.showerror("Error", "Please enter both IP addresses!")
            return
        start_monitoring(ip1, ip2)

    start_button = tk.Button(
        root,
        text="Start Monitoring",
        font=("Arial", 11, "bold"),
        bg="#4CAF50",
        fg="white",
        command=on_start,
    )
    start_button.pack(pady=15)

    info_label = tk.Label(root, text="(Close the graph window to stop monitoring)", font=("Arial", 9), fg="gray")
    info_label.pack()

    root.mainloop()


if __name__ == "__main__":
    create_gui()
