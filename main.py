# ----------------------------- #
# COLLATZ CONJECTURE VISUALIZER #
# ----------------------------- #
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import mplcursors
import webbrowser
import numpy as np
import random

# ---------- #
# MAIN CLASS #
# ---------- #
class CollatzVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Collatz Conjecture")
        self.root.state("zoomed")

        # State variables
        self.sequence = []
        self.current_step = 0
        self.animation_job = None
        self.is_animating = False
        self.is_log_scale = True
        self.cursor = None

        # Setup GUI
        self.setup_modern_theme()
        self.create_layout()

    # Configure ttk theme and colors
    def setup_modern_theme(self):
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except tk.TclError:
            pass

        BG_COLOR = "#F0F0F0"
        TEXT_COLOR = "#1a1a1a"
        ACCENT_COLOR = "#0078D7"

        self.root.configure(bg=BG_COLOR)
        style.configure('.', background=BG_COLOR, foreground=TEXT_COLOR, font=('Segoe UI', 9))
        style.configure('TLabel', padding=2)
        style.configure('TButton', padding=(5, 5))
        style.configure('TLabelframe', padding=5)
        style.configure('TLabelframe.Label', font=('Segoe UI', 10, 'bold'), padding=(0, 5))
        style.map('TButton', background=[('active', ACCENT_COLOR)], foreground=[('active', 'white')])
        style.configure('Accent.TButton', foreground='white', background=ACCENT_COLOR)
        style.map('Accent.TButton', background=[('active', '#005a9e')])
        style.configure('TProgressbar', troughcolor=BG_COLOR, background=ACCENT_COLOR, thickness=20)

    # Build main GUI layout: controls, info panels, plot
    def create_layout(self):
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)

        # --- TOP PANEL (CONTROLS) ---
        top_controls_frame = ttk.Frame(main_frame)
        top_controls_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        for i in range(4):
            top_controls_frame.grid_columnconfigure(i, weight=1, uniform="top_sections")

        # 1. Simulation section
        sim_frame = ttk.LabelFrame(top_controls_frame, text="SIMULATION")
        sim_frame.grid(row=0, column=0, padx=(0, 5), pady=0, sticky="ew")
        sim_frame.grid_columnconfigure(0, weight=1)
        sim_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(sim_frame, text="NUMBER:").grid(row=0, column=0, padx=5, pady=5, sticky='ew')
        self.number_var = tk.StringVar(value="1")
        self.number_entry = ttk.Entry(sim_frame, textvariable=self.number_var, width=50, justify='center')
        self.number_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        random_btn = ttk.Button(sim_frame, text="RANDOM", command=self.generate_random_number)
        random_btn.grid(row=1, column=0, columnspan=2, padx=5, pady=(5, 2), sticky='ew')

        generate_btn = ttk.Button(sim_frame, text="GENERATE SEQUENCE", command=self.generate_sequence, style="Accent.TButton")
        generate_btn.grid(row=2, column=0, columnspan=2, padx=5, pady=(2, 5), sticky='ew')

        # 2. Animation section
        anim_frame = ttk.LabelFrame(top_controls_frame, text="ANIMATION")
        anim_frame.grid(row=0, column=1, padx=5, pady=0, sticky="ew")
        anim_frame.grid_columnconfigure(0, weight=1)
        self.play_btn = ttk.Button(anim_frame, text="▶ START", command=self.toggle_animation)
        self.play_btn.grid(row=0, column=0, padx=5, pady=(5, 2), sticky='ew')
        reset_btn = ttk.Button(anim_frame, text="🔄 RESET", command=self.reset_animation)
        reset_btn.grid(row=1, column=0, padx=5, pady=2, sticky='ew')
        self.scale_btn = ttk.Button(anim_frame, text="-> SCALE: LINEAR", command=self.toggle_scale)
        self.scale_btn.grid(row=2, column=0, padx=5, pady=(2,5), sticky='ew')

        # 3. Navigation section
        nav_frame = ttk.LabelFrame(top_controls_frame, text="NAVIGATION")
        nav_frame.grid(row=0, column=2, padx=5, pady=0, sticky="nsew")
        nav_frame.grid_columnconfigure(0, weight=1)
        nav_frame.grid_columnconfigure(1, weight=1)
        prev_btn = ttk.Button(nav_frame, text="◀ PREVIOUS", command=lambda: self.manual_step(-1))
        prev_btn.grid(row=0, column=0, padx=(5, 2), pady=(5, 2), sticky='ew')
        next_btn = ttk.Button(nav_frame, text="NEXT ▶", command=lambda: self.manual_step(1))
        next_btn.grid(row=0, column=1, padx=(2, 5), pady=(5, 2), sticky='ew')
        ttk.Label(nav_frame, text="SPEED [ms/step]").grid(row=1, column=0, columnspan=2, pady=(5, 2))
        self.speed_var = tk.DoubleVar(value=250)
        speed_scale = ttk.Scale(nav_frame, from_=1000, to=25, orient=tk.HORIZONTAL, variable=self.speed_var)
        speed_scale.grid(row=2, column=0, columnspan=2, padx=5, pady=(2, 5), sticky='ew')

        # 4. Other section
        other_frame = ttk.LabelFrame(top_controls_frame, text="OTHER")
        other_frame.grid(row=0, column=3, padx=(5, 0), pady=0, sticky="ew")
        other_frame.grid_columnconfigure(0, weight=1)
        info_btn = ttk.Button(other_frame, text="READ MORE", command=self.show_info)
        info_btn.grid(row=0, column=0, padx=5, pady=(5, 2), sticky='ew')
        export_png_btn = ttk.Button(other_frame, text="EXPORT PNG", command=self.export_chart)
        export_png_btn.grid(row=1, column=0, padx=5, pady=2, sticky='ew')
        export_csv_btn = ttk.Button(other_frame, text="EXPORT CSV", command=self.export_csv)
        export_csv_btn.grid(row=2, column=0, padx=5, pady=(2, 5), sticky='ew')

        # --- LEFT PANEL ---
        left_info_frame = ttk.Frame(main_frame)
        left_info_frame.grid(row=1, column=0, sticky="ns", padx=(0, 10))

        # Statistics frame
        stats_frame = ttk.LabelFrame(left_info_frame, text="STATISTICS")
        stats_frame.pack(fill='x', pady=(0, 10))
        self.stats_label = ttk.Label(stats_frame, text="STARTING NUMBER: -\nLENGTH: -\nMAXIMUM VALUE: -", font=("Consolas", 10))
        self.stats_label.pack(padx=10, pady=5, anchor='w')

        # Progress frame
        progress_frame = ttk.LabelFrame(left_info_frame, text="PROGRESS")
        progress_frame.pack(fill='x', pady=(0, 10))
        self.progress_label = ttk.Label(
            progress_frame,
            text="STEP: -/-\nVALUE: -\nF(n) = -",
            font=("Consolas", 10),
            width=38,
            anchor="w",   
            justify="left"
        )
        # Progress bar
        self.progress_label.pack(padx=10, pady=5, anchor='w')
        self.progress_bar = ttk.Progressbar(progress_frame, orient='horizontal', length=250, mode='determinate', style='TProgressbar')
        self.progress_bar.pack(padx=10, pady=(0, 10))

        # Sequence frame
        seq_frame = ttk.LabelFrame(left_info_frame, text="SEQUENCE")
        seq_frame.pack(fill='both', expand=True)
        seq_scrollbar = ttk.Scrollbar(seq_frame, orient=tk.VERTICAL)
        self.seq_listbox = tk.Listbox(seq_frame, yscrollcommand=seq_scrollbar.set, font=("Consolas", 10), width=20)
        seq_scrollbar.config(command=self.seq_listbox.yview)
        seq_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.seq_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # --- MAIN GRAPH ---
        plot_frame_container = ttk.Frame(main_frame)
        plot_frame_container.grid(row=1, column=1, sticky="nsew")
        plot_frame_container.grid_rowconfigure(0, weight=1)
        plot_frame_container.grid_columnconfigure(0, weight=1)
        self.setup_plot(plot_frame_container)

    # Initialize matplotlib figure and embed in Tkinter
    def setup_plot(self, parent):
        plt.style.use('seaborn-v0_8-whitegrid')
        self.fig, self.ax = plt.subplots()
        self.fig.patch.set_facecolor('#ffffff')
        self.ax.set_facecolor('#fafbfc')
        self.canvas = FigureCanvasTkAgg(self.fig, parent)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        self.canvas.mpl_connect("button_press_event", self.on_click)

    # Configure interactive mplcursors on scatter points
    def setup_cursor(self):
        # Configure cursor after creating the plot
        if self.cursor:
            self.cursor.remove()
        
        #  Creates the cursor only on scatter points (not on lines) - 
        scatter_collections = [coll for coll in self.ax.collections if hasattr(coll, '_offsets')]
        if scatter_collections:
            # Cursor on points for hover (hover=True)
            self.cursor = mplcursors.cursor(scatter_collections, hover=True)
            
            @self.cursor.connect("add")
            def on_add(sel):
                # sel.target contains the exact co-ordinates of the clicked point
                x_coord = int(sel.target[0])
                y_coord = int(sel.target[1])
                sel.annotation.set_text(f'Step: {x_coord}\nValue: {y_coord:,}')
                sel.annotation.get_bbox_patch().set(facecolor="#ffffff", alpha=0.9)
                sel.annotation.arrow_patch.set(arrowstyle="simple", facecolor="black", alpha=.5)
                
                # Also highlight in the sequence
                self.highlight_sequence_item(x_coord)

    def generate_random_number(self):
        rand_num = random.randint(1, 100000000)
        self.number_var.set(str(rand_num))

    # Compute Collatz sequence starting from n (up to 10,000 steps)
    def generate_collatz_sequence(self, n):
        sequence, current = [n], n
        limit = 10000
        while current != 1 and len(sequence) < limit:
            current = current // 2 if current % 2 == 0 else 3 * current + 1
            sequence.append(current)
        if len(sequence) == limit and current != 1:
            messagebox.showwarning("Limit Reached", f"The sequence has exceeded {limit} steps, and has not yet reached 1.")
        return sequence

    # Validate input, generate sequence, and reset animation
    def generate_sequence(self):
        self.stop_animation()
        try:
            num = int(self.number_var.get())
            if num <= 0:
                messagebox.showerror("Error", "Please enter a positive integer!")
                return
            self.sequence = self.generate_collatz_sequence(num)
            self.reset_animation()
        except ValueError:
            messagebox.showerror("Error", "Invalid input! Please enter an integer.")

    # Placeholder for future plot click handling
    def on_click(self, event):
        pass

    # Highlight specific item in Listbox (red for clicked, blue for current step)
    def highlight_sequence_item(self, idx):
        if not self.sequence or idx >= len(self.sequence):
            return
            
        # Remove previous highlight and hightlight only the selected element
        for i in range(self.seq_listbox.size()):
            if i == self.current_step:
                # Keep the current animation step highlighted
                self.seq_listbox.itemconfig(i, {'bg': '#0078D7', 'fg': 'white'})
            elif i == idx:
                # Highlight the clicked item with a different color
                self.seq_listbox.itemconfig(i, {'bg': '#e74c3c', 'fg': 'white'})
            else:
                # Normal items
                self.seq_listbox.itemconfig(i, {'bg': 'white', 'fg': 'black'})
        
        # Scroll to show the highlighted item
        self.seq_listbox.see(idx)

    def update_all_displays(self):
        self.update_plot()
        self.update_info_panels()

    # Redraw plot with current sequence, steps, and highlight current point
    # Handles linear/log scale and mplcursors
    def update_plot(self):
        if not self.sequence: 
            return
        
        self.ax.clear()
        self.ax.set_facecolor('#fafbfc')
        self.ax.set_title(f"Collatz Sequence N = {self.sequence[0]:,}", fontsize=12, fontweight='bold', color='#2c3e50', pad=15)
        self.ax.set_xlabel("STEPS", fontsize=10, color='#34495e')

        visible_seq = self.sequence[:self.current_step + 1]
        steps = list(range(len(visible_seq)))
        
        if len(visible_seq) > 1:
            self.ax.plot(steps, visible_seq, color='#0078D7', linewidth=2.5, alpha=0.8, zorder=2)
        if len(visible_seq) > 0:
            self.ax.scatter(steps, visible_seq, c='#f39c12', s=40, alpha=0.7, edgecolors='white', linewidth=1, zorder=4)

        if self.current_step < len(self.sequence):
            current_val = self.sequence[self.current_step]
            self.ax.scatter([self.current_step], [current_val], c='#e74c3c', s=120,
                            edgecolors='#2c3e50', linewidth=2, zorder=6,
                            label=f'Current step: {current_val:,}')

        # Set log/linear scale
        if self.is_log_scale:
            self.ax.set_yscale('log')
            self.ax.set_ylabel("VALUE (log scale)", fontsize=10, color='#34495e')
        else:
            self.ax.set_yscale('linear')
            self.ax.set_ylabel("VALUE (linear scale)", fontsize=10, color='#34495e')

        if self.current_step < len(self.sequence):
            self.ax.legend(frameon=True, fancybox=True, shadow=True, facecolor='white', edgecolor='#bdc3c7')
        
        self.ax.grid(True, which="both", ls="--", linewidth=0.5, alpha=0.7)
        self.fig.tight_layout(pad=3.0)
        
        # Setup cursor only after drawing the graph
        self.canvas.draw()
        self.setup_cursor()

    # Update stats, progress, and sequence Listbox  
    def update_info_panels(self):
        if not self.sequence: 
            return
        
        stats_text = (f"STARTING NUMBER: {self.sequence[0]:,}\n"
                      f"LENGTH: {len(self.sequence)-1:,}\n"
                      f"MAXIMUM VALUE: {max(self.sequence):,}")
        self.stats_label.config(text=stats_text)

        current_val = self.sequence[self.current_step]
        op_text = ""
        if self.current_step < len(self.sequence) - 1:
            next_val = self.sequence[self.current_step + 1]
            if current_val % 2 == 0:
                op_text = f"f(n) = n/2  = {current_val} / 2 =\n\t    = {next_val}"
            else:
                op_text = f"f(n) = 3n+1 = 3 * {current_val} + 1 =\n\t    = {next_val}"

        progress_text = (f"STEP: {self.current_step}/{len(self.sequence)-1}\n"
                         f"VALUE: {current_val:,}\n"
                         f"{op_text}")
        self.progress_label.config(text=progress_text)
        self.progress_bar['value'] = (self.current_step) / len(self.sequence) * 100

        # Update listbox while keeping the highlights
        self.seq_listbox.delete(0, tk.END)
        for i, val in enumerate(self.sequence):
            self.seq_listbox.insert(tk.END, f"{i: >3}: {val:,}")
        
        # Highlight only the current step of the animation
        self.seq_listbox.itemconfig(self.current_step, {'bg': '#0078D7', 'fg': 'white'})
        self.seq_listbox.see(self.current_step)

    # Perform one animation step and schedule next
    def animate_step(self):
        if self.current_step < len(self.sequence) - 1:
            self.current_step += 1
            self.update_all_displays()
            self.animation_job = self.root.after(int(self.speed_var.get()), self.animate_step)
        else:
            self.stop_animation()

    # Start or stop animation based on current state
    def toggle_animation(self):
        if not self.sequence:
            messagebox.showwarning("Warning", "Generate a sequence first!")
            return
        if self.is_animating:
            self.stop_animation()
        else:
            self.start_animation()

    # Begin animation from current step (or reset to 0)
    def start_animation(self):
        if self.current_step >= len(self.sequence) - 1:
            self.current_step = 0
        self.is_animating = True
        self.play_btn.config(text="⏸ PAUSE")
        self.animate_step()

    # Stop animation and reset play button
    def stop_animation(self):
        if self.animation_job:
            self.root.after_cancel(self.animation_job)
            self.animation_job = None
        self.is_animating = False
        self.play_btn.config(text="▶ START")

    # Move one step forward/backward manually
    def manual_step(self, direction):
        if not self.sequence: 
            return
        self.stop_animation()
        new_step = self.current_step + direction
        if 0 <= new_step < len(self.sequence):
            self.current_step = new_step
            self.update_all_displays()

    # Reset animation and parameters
    def reset_animation(self):
        self.stop_animation()
        self.current_step = 0
        if self.sequence:
            self.update_all_displays()

    # Switch between logarithmic and linear y-axis scale
    def toggle_scale(self):
        self.is_log_scale = not self.is_log_scale
        if self.is_log_scale:
            self.scale_btn.config(text="-> LINEAR SCALE")
        else:
            self.scale_btn.config(text="-> LOGARITHMIC SCALE")
        self.update_plot()

    # Save current plot as PNG/JPG
    def export_chart(self):
        if not self.sequence:
            messagebox.showerror("Error", "No chart to export.")
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG Image", "*.png"), ("JPG Image", "*.jpg")],
            title="Save chart as...",
            initialfile=f"Collatz-Conjecture-N-{self.sequence[0]}.png"
        )
        if file_path:
            self.fig.savefig(file_path, dpi=300, bbox_inches='tight')
            messagebox.showinfo("Success", f"Chart saved in:\n{file_path}")

    # Save current sequence as CSV/TXT file
    def export_csv(self):
        if not self.sequence:
            messagebox.showerror("Error", "No sequence to export.")
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV File", "*.csv"), ("Text File", "*.txt")],
            title="Save sequence as...",
            initialfile=f"Collatz-Conjecture-N-{self.sequence[0]}.csv"
        )
        if file_path:
            with open(file_path, 'w', newline='') as f:
                f.write("Step,Value\n")
                for i, val in enumerate(self.sequence):
                    f.write(f"{i},{val}\n")
            messagebox.showinfo("Success", f"Sequence saved in:\n{file_path}")

    # Open Collatz Wikipedia page in web browser
    def show_info(self):
        url = "https://en.wikipedia.org/wiki/Collatz_conjecture"
        webbrowser.open(url)


if __name__ == "__main__":
    root = tk.Tk()
    app = CollatzVisualizer(root)
    root.after(100, app.generate_sequence)
    root.mainloop()

