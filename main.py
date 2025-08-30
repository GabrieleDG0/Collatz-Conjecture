import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import mplcursors
import numpy as np
import random


class CollatzVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Congettura di Collatz")
        self.root.state("zoomed")

        # Variabili di stato
        self.sequence = []
        self.current_step = 0
        self.animation_job = None
        self.is_animating = False
        self.is_log_scale = True
        self.cursor = None  # Aggiungiamo riferimento al cursore

        # Setup GUI
        self.setup_modern_theme()
        self.create_layout()

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


    def create_layout(self):
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)

        # --- PANNELLO SUPERIORE (CONTROLLI) ---
        top_controls_frame = ttk.Frame(main_frame)
        top_controls_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        for i in range(4):
            top_controls_frame.grid_columnconfigure(i, weight=1, uniform="top_sections")

        # 1. Sezione Simulazione
        sim_frame = ttk.LabelFrame(top_controls_frame, text="SIMULAZIONE")
        sim_frame.grid(row=0, column=0, padx=(0, 5), pady=0, sticky="ew")
        sim_frame.grid_columnconfigure(0, weight=1)
        sim_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(sim_frame, text="NUMERO INIZIALE:").grid(row=0, column=0, padx=5, pady=5, sticky='ew')
        self.number_var = tk.StringVar(value="1")
        self.number_entry = ttk.Entry(sim_frame, textvariable=self.number_var, width=50, justify='center')
        self.number_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')

        random_btn = ttk.Button(sim_frame, text="RANDOM", command=self.generate_random_number)
        random_btn.grid(row=1, column=0, columnspan=2, padx=5, pady=(5, 2), sticky='ew')

        generate_btn = ttk.Button(sim_frame, text="GENERA SEQUENZA", command=self.generate_sequence, style="Accent.TButton")
        generate_btn.grid(row=2, column=0, columnspan=2, padx=5, pady=(2, 5), sticky='ew')

        # 2. Sezione Animazione
        anim_frame = ttk.LabelFrame(top_controls_frame, text="ANIMAZIONE")
        anim_frame.grid(row=0, column=1, padx=5, pady=0, sticky="ew")
        anim_frame.grid_columnconfigure(0, weight=1)
        self.play_btn = ttk.Button(anim_frame, text="▶ AVVIA", command=self.toggle_animation)
        self.play_btn.grid(row=0, column=0, padx=5, pady=(5, 2), sticky='ew')
        reset_btn = ttk.Button(anim_frame, text="🔄 RESET", command=self.reset_animation)
        reset_btn.grid(row=1, column=0, padx=5, pady=2, sticky='ew')
        self.scale_btn = ttk.Button(anim_frame, text="-> SCALA: LINEARE", command=self.toggle_scale)
        self.scale_btn.grid(row=2, column=0, padx=5, pady=(2,5), sticky='ew')

        # 3. Sezione Navigazione
        nav_frame = ttk.LabelFrame(top_controls_frame, text="NAVIGAZIONE")
        nav_frame.grid(row=0, column=2, padx=5, pady=0, sticky="nsew")
        nav_frame.grid_columnconfigure(0, weight=1)
        nav_frame.grid_columnconfigure(1, weight=1)
        prev_btn = ttk.Button(nav_frame, text="◀ PRECEDENTE", command=lambda: self.manual_step(-1))
        prev_btn.grid(row=0, column=0, padx=(5, 2), pady=(5, 2), sticky='ew')
        next_btn = ttk.Button(nav_frame, text="SUCCESSIVO ▶", command=lambda: self.manual_step(1))
        next_btn.grid(row=0, column=1, padx=(2, 5), pady=(5, 2), sticky='ew')
        ttk.Label(nav_frame, text="VELOCITÀ [ms/passo]").grid(row=1, column=0, columnspan=2, pady=(5, 2))
        self.speed_var = tk.DoubleVar(value=250)
        speed_scale = ttk.Scale(nav_frame, from_=1000, to=25, orient=tk.HORIZONTAL, variable=self.speed_var)
        speed_scale.grid(row=2, column=0, columnspan=2, padx=5, pady=(2, 5), sticky='ew')

        # 4. Sezione Altro
        other_frame = ttk.LabelFrame(top_controls_frame, text="ALTRO")
        other_frame.grid(row=0, column=3, padx=(5, 0), pady=0, sticky="ew")
        other_frame.grid_columnconfigure(0, weight=1)
        info_btn = ttk.Button(other_frame, text="CONGETTURA DI COLLATZ", command=self.show_info)
        info_btn.grid(row=0, column=0, padx=5, pady=(5, 2), sticky='ew')
        export_png_btn = ttk.Button(other_frame, text="ESPORTA PNG", command=self.export_chart)
        export_png_btn.grid(row=1, column=0, padx=5, pady=2, sticky='ew')
        export_csv_btn = ttk.Button(other_frame, text="ESPORTA CSV", command=self.export_csv)
        export_csv_btn.grid(row=2, column=0, padx=5, pady=(2, 5), sticky='ew')

        # --- PANNELLO LATERALE SINISTRO (INFO) ---
        left_info_frame = ttk.Frame(main_frame)
        left_info_frame.grid(row=1, column=0, sticky="ns", padx=(0, 10))

        stats_frame = ttk.LabelFrame(left_info_frame, text="STATISTICHE")
        stats_frame.pack(fill='x', pady=(0, 10))
        self.stats_label = ttk.Label(stats_frame, text="NUMERO INIZIALE: -\nLUNGHEZZA: -\nVALORE MASSIMO: -", font=("Consolas", 10))
        self.stats_label.pack(padx=10, pady=5, anchor='w')

        progress_frame = ttk.LabelFrame(left_info_frame, text="PROGRESSO")
        progress_frame.pack(fill='x', pady=(0, 10))
        self.progress_label = ttk.Label(
            progress_frame,
            text="PASSO: -/-\nVALORE: -\nF(n) = -",
            font=("Consolas", 10),
            width=38,
            anchor="w",   
            justify="left"
        )
        self.progress_label.pack(padx=10, pady=5, anchor='w')
        self.progress_bar = ttk.Progressbar(progress_frame, orient='horizontal', length=250, mode='determinate', style='TProgressbar')
        self.progress_bar.pack(padx=10, pady=(0, 10))

        seq_frame = ttk.LabelFrame(left_info_frame, text="SEQUENZA")
        seq_frame.pack(fill='both', expand=True)
        seq_scrollbar = ttk.Scrollbar(seq_frame, orient=tk.VERTICAL)
        self.seq_listbox = tk.Listbox(seq_frame, yscrollcommand=seq_scrollbar.set, font=("Consolas", 10), width=20)
        seq_scrollbar.config(command=self.seq_listbox.yview)
        seq_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.seq_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # --- GRAFICO PRINCIPALE ---
        plot_frame_container = ttk.Frame(main_frame)
        plot_frame_container.grid(row=1, column=1, sticky="nsew")
        plot_frame_container.grid_rowconfigure(0, weight=1)
        plot_frame_container.grid_columnconfigure(0, weight=1)
        self.setup_plot(plot_frame_container)

    def setup_plot(self, parent):
        plt.style.use('seaborn-v0_8-whitegrid')
        self.fig, self.ax = plt.subplots()
        self.fig.patch.set_facecolor('#ffffff')
        self.ax.set_facecolor('#fafbfc')
        self.canvas = FigureCanvasTkAgg(self.fig, parent)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        self.canvas.mpl_connect("button_press_event", self.on_click)

    def setup_cursor(self):
        """Configura il cursore click dopo aver creato il plot"""
        if self.cursor:
            self.cursor.remove()
        
        # Crea il cursore solo sui punti scatter (non sulle linee) - solo per click
        scatter_collections = [coll for coll in self.ax.collections if hasattr(coll, '_offsets')]
        if scatter_collections:
            # Cursore solo sui punti, solo per click (hover=False)
            self.cursor = mplcursors.cursor(scatter_collections, hover=True)
            
            @self.cursor.connect("add")
            def on_add(sel):
                # sel.target contiene le coordinate esatte del punto cliccato
                x_coord = int(sel.target[0])
                y_coord = int(sel.target[1])
                sel.annotation.set_text(f'Passo: {x_coord}\nValore: {y_coord:,}')
                sel.annotation.get_bbox_patch().set(facecolor="#ffffff", alpha=0.9)
                sel.annotation.arrow_patch.set(arrowstyle="simple", facecolor="black", alpha=.5)
                
                # Evidenzia anche nella sequenza
                self.highlight_sequence_item(x_coord)

    def generate_random_number(self):
        rand_num = random.randint(1, 100000000)
        self.number_var.set(str(rand_num))

    def generate_collatz_sequence(self, n):
        sequence, current = [n], n
        limit = 10000
        while current != 1 and len(sequence) < limit:
            current = current // 2 if current % 2 == 0 else 3 * current + 1
            sequence.append(current)
        if len(sequence) == limit and current != 1:
            messagebox.showwarning("Limite Raggiunto", f"La sequenza ha superato i {limit} passi e non ha ancora raggiunto 1.")
        return sequence

    def generate_sequence(self):
        self.stop_animation()
        try:
            num = int(self.number_var.get())
            if num <= 0:
                messagebox.showerror("Errore", "Inserisci un numero intero positivo!")
                return
            self.sequence = self.generate_collatz_sequence(num)
            self.reset_animation()
        except ValueError:
            messagebox.showerror("Errore", "Input non valido! Inserisci un numero intero.")

    def on_click(self, event):
        pass

    def highlight_sequence_item(self, idx):
        """Evidenzia un elemento specifico nella listbox senza modificare l'animazione"""
        if not self.sequence or idx >= len(self.sequence):
            return
            
        # Rimuovi highlight precedente e evidenzia solo l'elemento selezionato
        for i in range(self.seq_listbox.size()):
            if i == self.current_step:
                # Mantieni l'evidenziazione del passo corrente dell'animazione
                self.seq_listbox.itemconfig(i, {'bg': '#0078D7', 'fg': 'white'})
            elif i == idx:
                # Evidenzia l'elemento cliccato con un colore diverso
                self.seq_listbox.itemconfig(i, {'bg': '#e74c3c', 'fg': 'white'})
            else:
                # Elementi normali
                self.seq_listbox.itemconfig(i, {'bg': 'white', 'fg': 'black'})
        
        # Scorri per mostrare l'elemento evidenziato
        self.seq_listbox.see(idx)

    def update_all_displays(self):
        self.update_plot()
        self.update_info_panels()

    def update_plot(self):
        if not self.sequence: 
            return
        
        self.ax.clear()
        self.ax.set_facecolor('#fafbfc')
        self.ax.set_title(f"Sequenza di Collatz N = {self.sequence[0]:,}", fontsize=12, fontweight='bold', color='#2c3e50', pad=15)
        self.ax.set_xlabel("PASSI", fontsize=10, color='#34495e')

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
                            label=f'Passo Corrente: {current_val:,}')

        # Imposta scala secondo pulsante
        if self.is_log_scale:
            self.ax.set_yscale('log')
            self.ax.set_ylabel("VALORE (scala log)", fontsize=10, color='#34495e')
        else:
            self.ax.set_yscale('linear')
            self.ax.set_ylabel("VALORE (scala lineare)", fontsize=10, color='#34495e')

        if self.current_step < len(self.sequence):
            self.ax.legend(frameon=True, fancybox=True, shadow=True, facecolor='white', edgecolor='#bdc3c7')
        
        self.ax.grid(True, which="both", ls="--", linewidth=0.5, alpha=0.7)
        self.fig.tight_layout(pad=3.0)
        
        # Configura il cursore DOPO aver disegnato il grafico
        self.canvas.draw()
        self.setup_cursor()

    def update_info_panels(self):
        if not self.sequence: 
            return
        
        stats_text = (f"NUMERO INIZIALE: {self.sequence[0]:,}\n"
                      f"LUNGHEZZA: {len(self.sequence)-1:,}\n"
                      f"VALORE MASSIMO: {max(self.sequence):,}")
        self.stats_label.config(text=stats_text)

        current_val = self.sequence[self.current_step]
        op_text = ""
        if self.current_step < len(self.sequence) - 1:
            next_val = self.sequence[self.current_step + 1]
            if current_val % 2 == 0:
                op_text = f"f(n) = n/2  = {current_val} / 2 =\n\t    = {next_val}"
            else:
                op_text = f"f(n) = 3n+1 = 3 * {current_val} + 1 =\n\t    = {next_val}"

        progress_text = (f"PASSO: {self.current_step}/{len(self.sequence)-1}\n"
                         f"VALORE: {current_val:,}\n"
                         f"{op_text}")
        self.progress_label.config(text=progress_text)
        self.progress_bar['value'] = (self.current_step) / len(self.sequence) * 100

        # Aggiorna la listbox mantenendo le evidenziazioni
        self.seq_listbox.delete(0, tk.END)
        for i, val in enumerate(self.sequence):
            self.seq_listbox.insert(tk.END, f"{i: >3}: {val:,}")
        
        # Evidenzia solo il passo corrente dell'animazione
        self.seq_listbox.itemconfig(self.current_step, {'bg': '#0078D7', 'fg': 'white'})
        self.seq_listbox.see(self.current_step)

    def animate_step(self):
        if self.current_step < len(self.sequence) - 1:
            self.current_step += 1
            self.update_all_displays()
            self.animation_job = self.root.after(int(self.speed_var.get()), self.animate_step)
        else:
            self.stop_animation()

    def toggle_animation(self):
        if not self.sequence:
            messagebox.showwarning("Attenzione", "Prima genera una sequenza!")
            return
        if self.is_animating:
            self.stop_animation()
        else:
            self.start_animation()

    def start_animation(self):
        if self.current_step >= len(self.sequence) - 1:
            self.current_step = 0
        self.is_animating = True
        self.play_btn.config(text="⏸ PAUSA")
        self.animate_step()

    def stop_animation(self):
        if self.animation_job:
            self.root.after_cancel(self.animation_job)
            self.animation_job = None
        self.is_animating = False
        self.play_btn.config(text="▶ AVVIA")

    def manual_step(self, direction):
        if not self.sequence: 
            return
        self.stop_animation()
        new_step = self.current_step + direction
        if 0 <= new_step < len(self.sequence):
            self.current_step = new_step
            self.update_all_displays()

    def reset_animation(self):
        self.stop_animation()
        self.current_step = 0
        if self.sequence:
            self.update_all_displays()

    def toggle_scale(self):
        self.is_log_scale = not self.is_log_scale
        if self.is_log_scale:
            self.scale_btn.config(text="-> SCALA: LINEARE")
        else:
            self.scale_btn.config(text="-> SCALA: LOGARITMICA")
        self.update_plot()

    def export_chart(self):
        if not self.sequence:
            messagebox.showerror("Errore", "Nessun grafico da esportare.")
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("Immagine PNG", "*.png"), ("Immagine JPG", "*.jpg")],
            title="Salva grafico come...",
            initialfile=f"Collatz-Conjecture-N-{self.sequence[0]}.png"
        )
        if file_path:
            self.fig.savefig(file_path, dpi=300, bbox_inches='tight')
            messagebox.showinfo("Successo", f"Grafico salvato in:\n{file_path}")

    def export_csv(self):
        if not self.sequence:
            messagebox.showerror("Errore", "Nessuna sequenza da esportare.")
            return
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("File CSV", "*.csv"), ("File di testo", "*.txt")],
            title="Salva sequenza come...",
            initialfile=f"Collatz-Conjecture-N-{self.sequence[0]}.csv"
        )
        if file_path:
            with open(file_path, 'w', newline='') as f:
                f.write("Passo,Valore\n")
                for i, val in enumerate(self.sequence):
                    f.write(f"{i},{val}\n")
            messagebox.showinfo("Successo", f"Sequenza salvata in:\n{file_path}")

    def show_info(self):
        messagebox.showinfo("Formalismo matematico della Congettura di Collatz\n",
            "Definizione della funzione iterata\n"

            "Si definisce la funzione 𝑓: 𝑁→𝑁 come:\n"
            "𝑓(𝑛)={ \n"
            "\t𝑛/2, \t𝑠𝑒 𝑛≡0 (𝑚𝑜𝑑2)  (𝑛 𝑝𝑎𝑟𝑖)\n"
            "\t3𝑛+1, \t𝑠𝑒 𝑛≡1 (𝑚𝑜𝑑2)  (𝑛 𝑑𝑖𝑠𝑝𝑎𝑟𝑖)\n"
            "}\n"

            "\nA partire da un qualunque intero positivo 𝑛∈𝑁, si definisce la sequenza:\n"
            "𝑛_𝑘+1=𝑓(𝑛_𝑘),     𝑛∈𝑁+\n"

            "\nEnunciato della congettura\n"
            "La congettura di Collatz afferma che:\n"
            "∀𝑛∈𝑁+   ∃𝑘∈𝑁    :   𝑛_𝑘=1.\n"
            "Per ogni intero positivo, l’iterazione della funzione 𝑓 raggiunge sempre il valore 1")


if __name__ == "__main__":
    root = tk.Tk()
    app = CollatzVisualizer(root)
    root.after(100, app.generate_sequence)
    root.mainloop()