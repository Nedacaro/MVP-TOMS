import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import math
import random
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import os
from PIL import Image, ImageTk

class DatabaseHelper:
    def __init__(self):
        self.conn = None
        self.current_table = []
        self.column_names = []
        self.point_columns = []
        self.epochs = []
    

    def connect(self, db_path):
        try:
            self.conn = sqlite3.connect(db_path)
            cursor = self.conn.cursor()
            
            cursor.execute("PRAGMA table_info(Данные)")
            columns_info = cursor.fetchall()
            self.column_names = [col[1] for col in columns_info]
            
            cursor.execute("SELECT * FROM Данные ORDER BY Эпоха")
            rows = cursor.fetchall()
            
            self.current_table = []
            for row in rows:
                row_dict = {}
                for i, col in enumerate(self.column_names):
                    val = row[i]
                    if isinstance(val, str):
                        val = val.replace(',', '.')
                        try:
                            val = float(val) if '.' in val else (int(val) if val.isdigit() else val)
                        except:
                            pass
                    row_dict[col] = val
                self.current_table.append(row_dict)
            
            exclude = ["Эпоха", "ID", "Mu", "Alpha", "id", "сглаживание", "погрешность", "количество_блоков", "изображения"]
            self.point_columns = [col for col in self.column_names if col not in exclude]
            self.epochs = [row["Эпоха"] for row in self.current_table]
            
            self.ensure_mu_alpha_columns()
            
            return True
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось подключиться: {e}")
            return False
    

    def ensure_mu_alpha_columns(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute("PRAGMA table_info(Данные)")
            columns = [col[1] for col in cursor.fetchall()]
            
            if "Mu" not in columns:
                cursor.execute("ALTER TABLE Данные ADD COLUMN Mu REAL")
            if "Alpha" not in columns:
                cursor.execute("ALTER TABLE Данные ADD COLUMN Alpha REAL")
            self.conn.commit()
        except:
            pass
    

    def renumber_epochs(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT rowid, Эпоха FROM Данные ORDER BY Эпоха")
            rows = cursor.fetchall()
            
            for new_num, (rowid, old_epoch) in enumerate(rows, start=1):
                cursor.execute("UPDATE Данные SET Эпоха = ? WHERE rowid = ?", (new_num, rowid))
            
            self.conn.commit()
            self.load_data()  
            return True
        except Exception as e:
            print(f"Ошибка перенумерации: {e}")
            return False
    

    def get_values_for_epoch(self, epoch):
        for row in self.current_table:
            if row["Эпоха"] == epoch:
                values = []
                for col in self.point_columns:
                    val = row[col]
                    if isinstance(val, str):
                        val = float(val.replace(',', '.'))
                    values.append(float(val))
                return values
        return []
    
    def get_point_columns(self):
        return self.point_columns
    

    def get_error_value(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT погрешность FROM Значения LIMIT 1")
            row = cursor.fetchone()
            if row:
                return float(row[0])
        except:
            pass
        return 0.0009
    

    def save_error_value(self, error):
        try:
            cursor = self.conn.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS Значения (погрешность REAL)")
            cursor.execute("DELETE FROM Значения")
            cursor.execute("INSERT INTO Значения (погрешность) VALUES (?)", (error,))
            self.conn.commit()
        except:
            pass    
    

    def get_smoothing_values(self):
        return [0.1, 0.4, 0.7, 0.9]
    

    def add_row(self, values):
        try:
            cursor = self.conn.cursor()
            columns = ', '.join([f"[{col}]" for col in self.column_names])
            placeholders = ', '.join(['?' for _ in self.column_names])
            query = f"INSERT INTO Данные ({columns}) VALUES ({placeholders})"
            cursor.execute(query, values)
            self.conn.commit()
            self.load_data()
            return True
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось добавить строку: {e}")
            return False
    

    def insert_row_at_position(self, values, position):
        try:
            cursor = self.conn.cursor()
            
            cursor.execute("UPDATE Данные SET Эпоха = Эпоха + 1 WHERE Эпоха >= ?", (position,))
            
            columns = ', '.join([f"[{col}]" for col in self.column_names])
            placeholders = ', '.join(['?' for _ in self.column_names])
            
            values_with_epoch = list(values)
            epoch_index = self.column_names.index("Эпоха") if "Эпоха" in self.column_names else 0
            values_with_epoch[epoch_index] = position
            
            query = f"INSERT INTO Данные ({columns}) VALUES ({placeholders})"
            cursor.execute(query, values_with_epoch)
            
            self.conn.commit()
            self.load_data()
            return True
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось вставить строку: {e}")
            return False
    

    def delete_row(self, epoch):
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM Данные WHERE Эпоха = ?", (epoch,))
            self.conn.commit()
            
            cursor.execute("UPDATE Данные SET Эпоха = Эпоха - 1 WHERE Эпоха > ?", (epoch,))
            self.conn.commit()
            
            self.load_data()
            return True
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось удалить строку: {e}")
            return False
    

    def update_cell(self, epoch, column_name, new_value):
        try:
            cursor = self.conn.cursor()
            
            try:
                test_val = str(new_value).replace(',', '.')
                if test_val.replace('.', '').replace('-', '').isdigit():
                    new_value = float(test_val)
                elif test_val.isdigit():
                    new_value = int(test_val)
            except:
                pass
            
            query = f"UPDATE Данные SET [{column_name}] = ? WHERE Эпоха = ?"
            cursor.execute(query, (new_value, epoch))
            self.conn.commit()
            self.load_data()
            return True
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить: {e}")
            return False
    

    def load_data(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM Данные ORDER BY Эпоха")
        rows = cursor.fetchall()
        
        self.current_table = []
        for row in rows:
            row_dict = {}
            for i, col in enumerate(self.column_names):
                val = row[i]
                if isinstance(val, str):
                    val = val.replace(',', '.')
                    try:
                        val = float(val) if '.' in val else (int(val) if val.isdigit() else val)
                    except:
                        pass
                row_dict[col] = val
            self.current_table.append(row_dict)
        
        self.epochs = [row["Эпоха"] for row in self.current_table]
    

    def update_mu_alpha_in_db(self, epoch, mu, alpha):
        try:
            cursor = self.conn.cursor()
            cursor.execute("UPDATE Данные SET Mu = ?, Alpha = ? WHERE Эпоха = ?", (mu, alpha, epoch))
            self.conn.commit()
        except:
            pass
    
    def get_mu_alpha_from_db(self):
        mu_values = []
        alpha_values = []
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT Mu, Alpha FROM Данные ORDER BY Эпоха")
            rows = cursor.fetchall()
            for row in rows:
                mu_values.append(float(row[0]) if row[0] is not None else 0)
                alpha_values.append(float(row[1]) if row[1] is not None else 0)
        except:
            pass
        return mu_values, alpha_values




class MonitoringApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Мониторинг техногенных объектов")
        self.root.geometry("1500x900")
        self.root.configure(bg='#1e1e2e')
        
        self.db = DatabaseHelper()
        self.E = 0.0009
        self.ALPHA_VALUES = [0.1, 0.4, 0.7, 0.9]
        
        self.mu_values = []
        self.alpha_values = []
        self.mu_plus_values = []
        self.mu_minus_values = []
        self.alpha_plus_values = []
        self.alpha_minus_values = []
        self.R_values = []
        self.L_values = []
        self.status_values = []
        
        self.forecast_mu = {a: 0 for a in self.ALPHA_VALUES}
        self.forecast_alpha = {a: 0 for a in self.ALPHA_VALUES}
        self.forecast_mu_plus = {a: 0 for a in self.ALPHA_VALUES}
        self.forecast_mu_minus = {a: 0 for a in self.ALPHA_VALUES}
        self.forecast_alpha_plus = {a: 0 for a in self.ALPHA_VALUES}
        self.forecast_alpha_minus = {a: 0 for a in self.ALPHA_VALUES}
        
        self.forecast_tables = {}
        
        self.forecast_mu_value = 0
        self.forecast_alpha_value = 0
        self.forecast_mu_plus_val = 0
        self.forecast_mu_minus_val = 0
        self.forecast_alpha_plus_val = 0
        self.forecast_alpha_minus_val = 0
        self.forecast_R = 0
        self.forecast_L = 0
        self.forecast_status = ""
        
        self.block_points = {"А": [], "Б": []}
        self.current_block = "А"
        
        self.block_points_level2 = {"А": [], "Б": []}
        self.current_block_level2 = "А"
        self.block_m_values = []
        self.block_a_values = []
        self.block_m_plus_values = []
        self.block_m_minus_values = []
        self.block_a_plus_values = []
        self.block_a_minus_values = []
        self.block_epochs_level2 = []
        self.block_forecast_tables_level2 = {}
        
        self.object_image = None
        self.object_image_path = None
        
        self.current_point_values = None
        self.current_point_name = None
        
        self.setup_ui()
    

    def show_quick_help(self):
        """Быстрая справка для пользователя"""
        help_text = """╔══════════════════════════════════════════════════════════════════╗
║                    📖 БЫСТРАЯ СПРАВКА                                ║
╚══════════════════════════════════════════════════════════════════╝

🔹 ОСНОВНЫЕ ПОНЯТИЯ:
   μ (мю) - длина вектора (общая интенсивность параметров)
   α (альфа) - угол поворота (структурное изменение)
   E - погрешность измерений (по умолчанию 0.0009)

🔹 СТАТУСЫ:
   L < R  →  НОРМА (зелёный)
   L ≈ R  →  ПРЕДАВАРИЯ (оранжевый)  
   L > R  →  АВАРИЯ (красный)

🔹 ВКЛАДКИ:
   1. Загрузка данных - открыть БД, добавить/удалить строки
   2. Общий анализ - графики, прогнозы, таблица статусов
   3. Анализ блоков - группировка точек в блоки А и Б
   4. Выбор точки - прогноз для одной конкретной точки

🔹 КАК РАБОТАТЬ:
   1. Открыть БД (кнопка "Открыть БД")
   2. Нажать "Рассчитать μ и α"
   3. Перейти на вкладку 2 для просмотра графиков

🔹 ПРОГНОЗ:
   Формула: прогноз = α × среднее + (1-α) × последнее
   α = 0.1 (медленный) ... 0.9 (быстрый)

🔹 ФОРМУЛЫ:
   μ = √(x₁² + x₂² + ...)
   R = (μ⁺ - μ⁻)/2  (ширина коридора)
   L = |μ - μ₀|     (отклонение от эталона)

════════════════════════════════════════════════════════════════════
"""
        messagebox.showinfo("Справка", help_text)


    def setup_ui(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.setup_data_tab()      
        self.setup_level1_tab()    
        self.setup_level2_tab()    
        self.setup_level3_tab()    
    
    def setup_data_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="1. Загрузка данных")
        
        top_frame = tk.Frame(tab, bg='#2a2a3e')
        top_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(top_frame, text="Открыть БД", command=self.load_database,
                 bg='#5a5a8a', fg='white', font=('Arial', 10, 'bold'),
                 padx=20, pady=5).pack(side=tk.LEFT, padx=5)
        
        tk.Button(top_frame, text="Сохранить изменения", command=self.save_changes,
                 bg='#5a5a8a', fg='white', font=('Arial', 10, 'bold'),
                 padx=20, pady=5).pack(side=tk.LEFT, padx=5)
        
        tk.Button(top_frame, text="Добавить строку", command=self.add_row,
                 bg='#5a5a8a', fg='white', font=('Arial', 10, 'bold'),
                 padx=20, pady=5).pack(side=tk.LEFT, padx=5)
        
        tk.Button(top_frame, text="Удалить строку", command=self.delete_row,
                 bg='#5a5a8a', fg='white', font=('Arial', 10, 'bold'),
                 padx=20, pady=5).pack(side=tk.LEFT, padx=5)
        
        tk.Button(top_frame, text="Рассчитать μ и α", command=self.calculate_mu_alpha,
                 bg='#4a4a6a', fg='white', font=('Arial', 10, 'bold'),
                 padx=20, pady=5).pack(side=tk.LEFT, padx=5)
        
        tk.Button(top_frame, text="Редактировать ячейку", command=self.edit_selected_cell,
                 bg='#5a5a8a', fg='white', font=('Arial', 10, 'bold'),
                 padx=20, pady=5).pack(side=tk.LEFT, padx=5)
        
        params_frame = tk.Frame(top_frame, bg='#2a2a3e')
        params_frame.pack(side=tk.LEFT, padx=20)
        
        tk.Label(params_frame, text="Погрешность E:", bg='#2a2a3e', fg='#ccccff').pack(side=tk.LEFT)
        self.error_entry = tk.Entry(params_frame, width=10)
        self.error_entry.pack(side=tk.LEFT, padx=5)
        self.error_entry.insert(0, str(self.E))
        
        tk.Button(params_frame, text="Применить", command=self.apply_error,
                 bg='#4a4a6a', fg='white').pack(side=tk.LEFT, padx=10)
        
        tk.Button(top_frame, text=" ❓ ", 
                  command=self.show_quick_help,
                  bg='#4a4a6a', fg='white', font=('Arial', 10, 'bold'),
                  padx=15, pady=5).pack(side=tk.LEFT, padx=20)
        
        table_frame = tk.Frame(tab)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        scroll_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
        scroll_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        
        self.data_tree = ttk.Treeview(table_frame, yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        scroll_y.config(command=self.data_tree.yview)
        scroll_x.config(command=self.data_tree.xview)
        
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.data_tree.pack(fill=tk.BOTH, expand=True)
        
        image_object_frame = tk.LabelFrame(tab, text="Изображение объекта мониторинга", 
                                            bg='#2a2a3e', fg='#ccccff', font=('Arial', 10, 'bold'))
        image_object_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        btn_select_image = tk.Button(image_object_frame, text="📷 Выбрать изображение", 
                                      command=self.select_object_image,
                                      bg='#5a5a8a', fg='white', padx=15, pady=5)
        btn_select_image.pack(anchor='w', padx=10, pady=5)
        
        self.object_image_label = tk.Label(image_object_frame, bg='#1e1e2e', 
                                            text="Изображение не выбрано\n\nНажмите кнопку выше,\nчтобы выбрать фото объекта",
                                            font=('Arial', 10), fg='#8888aa')
        self.object_image_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.status_label = tk.Label(tab, text="Готов", bg='#1e1e2e', fg='#8888aa')
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)
    



    def edit_selected_cell(self):
        selected = self.data_tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Сначала выберите строку в таблице!")
            return
        
        item = selected[0]
        values = list(self.data_tree.item(item, 'values'))
        cols = self.data_tree["columns"]
        
        col_window = tk.Toplevel(self.root)
        col_window.title("Выберите колонку для редактирования")
        col_window.geometry("300x400")
        col_window.configure(bg='#1e1e2e')
        col_window.grab_set()
        col_window.transient(self.root)
        
        tk.Label(col_window, text="Выберите колонку для редактирования:", 
                 bg='#1e1e2e', fg='white', font=('Arial', 10)).pack(pady=10)
        
        listbox = tk.Listbox(col_window, bg='#2a2a3e', fg='white', font=('Arial', 10), height=15)
        listbox.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        for i, col in enumerate(cols):
            listbox.insert(tk.END, f"{i+1}. {col} (текущее: {values[i]})")
        
        def on_select():
            sel = listbox.curselection()
            if not sel:
                messagebox.showwarning("Внимание", "Выберите колонку!")
                return
            col_index = sel[0]
            col_name = cols[col_index]
            current_value = values[col_index]
            col_window.destroy()
            
            try:
                epoch = int(values[0])
            except:
                epoch = values[0]
            
            edit_window = tk.Toplevel(self.root)
            edit_window.title(f"Редактирование: {col_name}")
            edit_window.geometry("400x180")
            edit_window.configure(bg='#1e1e2e')
            edit_window.grab_set()
            edit_window.transient(self.root)
            edit_window.focus_force()
            
            edit_window.update_idletasks()
            x = (edit_window.winfo_screenwidth() // 2) - (400 // 2)
            y = (edit_window.winfo_screenheight() // 2) - (180 // 2)
            edit_window.geometry(f"+{x}+{y}")
            
            tk.Label(edit_window, text=f"Измените значение для колонки '{col_name}':", 
                     bg='#1e1e2e', fg='white', font=('Arial', 10)).pack(pady=15)
            
            entry = tk.Entry(edit_window, width=35, font=('Arial', 11))
            entry.insert(0, str(current_value))
            entry.pack(pady=10, padx=20)
            entry.select_range(0, tk.END)
            entry.focus_set()
            
            def save_edit():
                new_value = entry.get().strip()
                if not new_value:
                    messagebox.showerror("Ошибка", "Значение не может быть пустым!")
                    return
                
                if self.db.update_cell(epoch, col_name, new_value):
                    new_values = list(values)
                    new_values[col_index] = new_value
                    self.data_tree.item(item, values=new_values)
                    edit_window.destroy()
                    
                    self.status_label.config(text="Данные изменены, пересчёт μ и α...")
                    self.root.update()
                    self.calculate_mu_alpha()
                    self.status_label.config(text=f"Значение '{col_name}' для эпохи {epoch} обновлено")
                    messagebox.showinfo("Успех", f"Значение успешно обновлено!\nμ и α пересчитаны.")
                else:
                    messagebox.showerror("Ошибка", "Не удалось сохранить изменение!")
            
            def cancel_edit():
                edit_window.destroy()
            
            btn_frame = tk.Frame(edit_window, bg='#1e1e2e')
            btn_frame.pack(pady=15)
            
            tk.Button(btn_frame, text="Сохранить", command=save_edit,
                      bg='#5a5a8a', fg='white', padx=25, pady=5, font=('Arial', 10)).pack(side=tk.LEFT, padx=15)
            
            tk.Button(btn_frame, text="Отмена", command=cancel_edit,
                      bg='#8a5a5a', fg='white', padx=25, pady=5, font=('Arial', 10)).pack(side=tk.LEFT, padx=15)
            
            entry.bind("<Return>", lambda e: save_edit())
            entry.bind("<Escape>", lambda e: cancel_edit())
        
        tk.Button(col_window, text="Выбрать", command=on_select,
                  bg='#5a5a8a', fg='white', padx=20, pady=5).pack(pady=10)
    



    def select_object_image(self):
        file_path = filedialog.askopenfilename(
            title="Выберите изображение объекта мониторинга",
            filetypes=[("Изображения", "*.png *.jpg *.jpeg *.bmp *.gif"), ("Все файлы", "*.*")]
        )
        if file_path:
            self.object_image_path = file_path
            self.display_object_image(file_path)
            self.status_label.config(text=f"Изображение загружено: {os.path.basename(file_path)}")
    
    def display_object_image(self, image_path):
        try:
            label_width = self.object_image_label.winfo_width()
            label_height = self.object_image_label.winfo_height()
            
            if label_width <= 1:
                label_width = 400
            if label_height <= 1:
                label_height = 250
            
            img = Image.open(image_path)
            
            img.thumbnail((label_width - 20, label_height - 20), Image.Resampling.LANCZOS)
            
            self.object_image = ImageTk.PhotoImage(img)
            self.object_image_label.config(image=self.object_image, text='')
            
        except ImportError:
            self.object_image_label.config(text="Установите Pillow: pip install Pillow", fg='red')
        except Exception as e:
            self.object_image_label.config(text=f"Ошибка загрузки: {e}", fg='red')
    




    def setup_level1_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="2. Общий анализ")
        
        paned = ttk.PanedWindow(tab, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        left = ttk.Frame(paned)
        paned.add(left, weight=1)
        
        tk.Label(left, text="Выберите тип прогноза:", bg='#1e1e2e', fg='#ccccff').pack(pady=5)
        self.forecast_type_combo = ttk.Combobox(left, values=["μ", "μ+E", "μ-E", "α", "α+E", "α-E"], state="readonly")
        self.forecast_type_combo.pack(pady=5)
        self.forecast_type_combo.bind("<<ComboboxSelected>>", self.on_forecast_type_changed)
        
        tk.Label(left, text="Таблица прогнозных значений", bg='#1e1e2e', fg='#ccccff').pack(pady=(10,0))
        
        mu_frame = tk.Frame(left)
        mu_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        scroll_y_mu = ttk.Scrollbar(mu_frame, orient=tk.VERTICAL)
        scroll_x_mu = ttk.Scrollbar(mu_frame, orient=tk.HORIZONTAL)
        
        self.mu_alpha_tree = ttk.Treeview(mu_frame, yscrollcommand=scroll_y_mu.set, xscrollcommand=scroll_x_mu.set, height=8)
        scroll_y_mu.config(command=self.mu_alpha_tree.yview)
        scroll_x_mu.config(command=self.mu_alpha_tree.xview)
        
        scroll_y_mu.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x_mu.pack(side=tk.BOTTOM, fill=tk.X)
        self.mu_alpha_tree.pack(fill=tk.BOTH, expand=True)
        
        self.mu_alpha_tree["columns"] = ["Эпоха", "Реал. знач.", "α=0.1", "α=0.4", "α=0.7", "α=0.9"]
        self.mu_alpha_tree["show"] = "headings"
        
        col_widths = {"Эпоха": 80, "Реал. знач.": 120, "α=0.1": 100, "α=0.4": 100, "α=0.7": 100, "α=0.9": 100}
        for col, width in col_widths.items():
            self.mu_alpha_tree.heading(col, text=col)
            self.mu_alpha_tree.column(col, width=width)
        
        tk.Label(left, text="Таблица статуса", bg='#1e1e2e', fg='#ccccff').pack(pady=(10,0))
        
        status_frame = tk.Frame(left)
        status_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        scroll_y_st = ttk.Scrollbar(status_frame, orient=tk.VERTICAL)
        scroll_x_st = ttk.Scrollbar(status_frame, orient=tk.HORIZONTAL)
        
        self.status_tree = ttk.Treeview(status_frame, yscrollcommand=scroll_y_st.set, xscrollcommand=scroll_x_st.set, height=8)
        scroll_y_st.config(command=self.status_tree.yview)
        scroll_x_st.config(command=self.status_tree.xview)
        
        scroll_y_st.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x_st.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_tree.pack(fill=tk.BOTH, expand=True)
        
        right = ttk.Frame(paned)
        paned.add(right, weight=2)
        
        forecast_frame = ttk.Frame(right)
        forecast_frame.pack(fill=tk.BOTH, expand=True)
        
        self.fig_forecast = Figure(figsize=(6, 4), dpi=100, facecolor='#2a2a3e')
        self.ax_forecast = self.fig_forecast.add_subplot(111)
        self.ax_forecast.set_facecolor('#2a2a3e')
        self.ax_forecast.tick_params(colors='white')
        self.ax_forecast.set_xlabel("Эпоха", color='white')
        self.ax_forecast.set_ylabel("Значение", color='white')
        self.ax_forecast.set_title("Прогнозные значения", color='white')
        self.canvas_forecast = FigureCanvasTkAgg(self.fig_forecast, master=forecast_frame)
        self.canvas_forecast.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        response_frame = ttk.Frame(right)
        response_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.fig_response = Figure(figsize=(6, 4), dpi=100, facecolor='#2a2a3e')
        self.ax_response = self.fig_response.add_subplot(111)
        self.ax_response.set_facecolor('#2a2a3e')
        self.ax_response.tick_params(colors='white')
        self.ax_response.set_xlabel("μ", color='white')
        self.ax_response.set_ylabel("α", color='white')
        self.ax_response.set_title("Функция отклика S(t)", color='white')
        self.canvas_response = FigureCanvasTkAgg(self.fig_response, master=response_frame)
        self.canvas_response.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        response_params = tk.Frame(response_frame, bg='#2a2a3e', height=35)
        response_params.pack(side=tk.BOTTOM, fill=tk.X)
        response_params.pack_propagate(False)
        
        self.show_s = tk.BooleanVar(value=True)
        self.show_s_plus = tk.BooleanVar(value=False)
        self.show_s_minus = tk.BooleanVar(value=False)
        
        tk.Checkbutton(response_params, text="S(t)", variable=self.show_s, bg='#2a2a3e', fg='white',
                       command=self.plot_response_function).pack(side=tk.LEFT, padx=10)
        tk.Checkbutton(response_params, text="S+(t)", variable=self.show_s_plus, bg='#2a2a3e', fg='white',
                       command=self.plot_response_function).pack(side=tk.LEFT, padx=10)
        tk.Checkbutton(response_params, text="S-(t)", variable=self.show_s_minus, bg='#2a2a3e', fg='white',
                       command=self.plot_response_function).pack(side=tk.LEFT, padx=10)
    




    def setup_level2_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="3. Анализ блоков")
        
        paned = ttk.PanedWindow(tab, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        left = ttk.Frame(paned)
        paned.add(left, weight=1)
        
        tk.Label(left, text="Выберите блок:", bg='#1e1e2e', fg='#ccccff').pack(pady=5)
        self.block_combo_level2 = ttk.Combobox(left, values=["А", "Б"], state="readonly")
        self.block_combo_level2.pack(pady=5)
        self.block_combo_level2.bind("<<ComboboxSelected>>", self.on_block_selected_level2)
        
        points_frame = tk.Frame(left, bg='#1e1e2e')
        points_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        tk.Label(points_frame, text="Все точки", bg='#1e1e2e', fg='#ccccff').pack(side=tk.LEFT, padx=20)
        tk.Label(points_frame, text="Точки блока", bg='#1e1e2e', fg='#ccccff').pack(side=tk.RIGHT, padx=20)
        
        list_frame = tk.Frame(points_frame, bg='#1e1e2e')
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.all_points_list_level2 = tk.Listbox(list_frame, bg='#2a2a3e', fg='white', height=15)
        self.all_points_list_level2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        self.all_points_list_level2.bind("<Double-Button-1>", self.move_to_block_level2)
        
        self.block_points_list_level2 = tk.Listbox(list_frame, bg='#2a2a3e', fg='white', height=15)
        self.block_points_list_level2.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        self.block_points_list_level2.bind("<Double-Button-1>", self.move_from_block_level2)
        
        btn_frame = tk.Frame(left, bg='#1e1e2e')
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="Подтвердить и рассчитать", command=self.calculate_block_level2,
                  bg='#5a5a8a', fg='white', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)
        
        right = ttk.Frame(paned)
        paned.add(right, weight=2)
        
        select_frame = tk.Frame(right, bg='#2a2a3e')
        select_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(select_frame, text="Выберите таблицу:", bg='#2a2a3e', fg='#ccccff').pack(side=tk.LEFT, padx=10)
        self.combo_tables_level2 = ttk.Combobox(select_frame, state="readonly", width=20)
        self.combo_tables_level2.pack(side=tk.LEFT, padx=10)
        self.combo_tables_level2.bind("<<ComboboxSelected>>", self.on_table_selected_level2)
        
        graph_notebook = ttk.Notebook(right)
        graph_notebook.pack(fill=tk.BOTH, expand=True, pady=5)
        
        phase_frame = ttk.Frame(graph_notebook)
        graph_notebook.add(phase_frame, text="Фазовые траектории")
        
        phase_container = tk.Frame(phase_frame, bg='#2a2a3e')
        phase_container.pack(fill=tk.BOTH, expand=True)
        
        self.fig_phase_level2 = Figure(figsize=(5, 4), dpi=100, facecolor='#2a2a3e')
        self.ax_phase_level2 = self.fig_phase_level2.add_subplot(111)
        self.ax_phase_level2.set_facecolor('#2a2a3e')
        self.ax_phase_level2.tick_params(colors='white')
        self.ax_phase_level2.set_xlabel("Эпоха", color='white')
        self.ax_phase_level2.set_ylabel("Значение", color='white')
        self.canvas_phase_level2 = FigureCanvasTkAgg(self.fig_phase_level2, master=phase_container)
        self.canvas_phase_level2.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        response_frame2 = ttk.Frame(graph_notebook)
        graph_notebook.add(response_frame2, text="Функция S(t)")
        
        response_container = tk.Frame(response_frame2, bg='#2a2a3e')
        response_container.pack(fill=tk.BOTH, expand=True)
        
        self.fig_response_level2 = Figure(figsize=(5, 4), dpi=100, facecolor='#2a2a3e')
        self.ax_response_level2 = self.fig_response_level2.add_subplot(111)
        self.ax_response_level2.set_facecolor('#2a2a3e')
        self.ax_response_level2.tick_params(colors='white')
        self.ax_response_level2.set_xlabel("μ", color='white')
        self.ax_response_level2.set_ylabel("α", color='white')
        self.canvas_response_level2 = FigureCanvasTkAgg(self.fig_response_level2, master=response_container)
        self.canvas_response_level2.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        response_params = tk.Frame(response_container, bg='#2a2a3e', height=35)
        response_params.pack(side=tk.BOTTOM, fill=tk.X)
        response_params.pack_propagate(False)
        
        self.show_s_level2 = tk.BooleanVar(value=True)
        self.show_s_plus_level2 = tk.BooleanVar(value=False)
        self.show_s_minus_level2 = tk.BooleanVar(value=False)
        
        tk.Checkbutton(response_params, text="S(t)", variable=self.show_s_level2, bg='#2a2a3e', fg='white',
                       command=self.plot_response_function_level2).pack(side=tk.LEFT, padx=10)
        tk.Checkbutton(response_params, text="S+(t)", variable=self.show_s_plus_level2, bg='#2a2a3e', fg='white',
                       command=self.plot_response_function_level2).pack(side=tk.LEFT, padx=10)
        tk.Checkbutton(response_params, text="S-(t)", variable=self.show_s_minus_level2, bg='#2a2a3e', fg='white',
                       command=self.plot_response_function_level2).pack(side=tk.LEFT, padx=10)
        
        tk.Label(right, text="Таблица статуса блока", bg='#1e1e2e', fg='#ccccff').pack(pady=(5,0))
        
        status_block_frame = tk.Frame(right)
        status_block_frame.pack(fill=tk.X, pady=5)
        
        scroll_y_sb = ttk.Scrollbar(status_block_frame, orient=tk.VERTICAL)
        scroll_x_sb = ttk.Scrollbar(status_block_frame, orient=tk.HORIZONTAL)
        
        self.block_status_tree_level2 = ttk.Treeview(status_block_frame, yscrollcommand=scroll_y_sb.set, 
                                                      xscrollcommand=scroll_x_sb.set, height=6)
        scroll_y_sb.config(command=self.block_status_tree_level2.yview)
        scroll_x_sb.config(command=self.block_status_tree_level2.xview)
        
        scroll_y_sb.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x_sb.pack(side=tk.BOTTOM, fill=tk.X)
        self.block_status_tree_level2.pack(fill=tk.X, expand=True)
        
        tk.Label(right, text="Таблица μ и α блока", bg='#1e1e2e', fg='#ccccff').pack(pady=(10,0))
        
        mu_block_frame = tk.Frame(right)
        mu_block_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        scroll_y_mb = ttk.Scrollbar(mu_block_frame, orient=tk.VERTICAL)
        scroll_x_mb = ttk.Scrollbar(mu_block_frame, orient=tk.HORIZONTAL)
        
        self.block_mu_alpha_tree_level2 = ttk.Treeview(mu_block_frame, yscrollcommand=scroll_y_mb.set, 
                                                        xscrollcommand=scroll_x_mb.set, height=8)
        scroll_y_mb.config(command=self.block_mu_alpha_tree_level2.yview)
        scroll_x_mb.config(command=self.block_mu_alpha_tree_level2.xview)
        
        scroll_y_mb.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x_mb.pack(side=tk.BOTTOM, fill=tk.X)
        self.block_mu_alpha_tree_level2.pack(fill=tk.BOTH, expand=True)
        
        self.block_mu_alpha_tree_level2["columns"] = ["Эпоха", "Реал. знач.", "α=0.1", "α=0.4", "α=0.7", "α=0.9"]
        self.block_mu_alpha_tree_level2["show"] = "headings"
        
        col_widths = {"Эпоха": 80, "Реал. знач.": 120, "α=0.1": 100, "α=0.4": 100, "α=0.7": 100, "α=0.9": 100}
        for col, width in col_widths.items():
            self.block_mu_alpha_tree_level2.heading(col, text=col)
            self.block_mu_alpha_tree_level2.column(col, width=width)
        
        self.init_points_list_level2()
    




    def setup_level3_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="4. Выбор точки")
        
        paned = ttk.PanedWindow(tab, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        

        left = ttk.Frame(paned)
        paned.add(left, weight=1)
        
        tk.Label(left, text="Выберите одну точку для прогнозирования:", 
                 bg='#1e1e2e', fg='#ccccff', font=('Arial', 11)).pack(pady=10)
        
        list_frame = tk.Frame(left, bg='#1e1e2e')
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        scroll_y = ttk.Scrollbar(list_frame, orient=tk.VERTICAL)
        self.single_point_listbox = tk.Listbox(list_frame, bg='#2a2a3e', fg='white',
                                                selectmode=tk.SINGLE,
                                                yscrollcommand=scroll_y.set,
                                                font=('Courier', 10))
        scroll_y.config(command=self.single_point_listbox.yview)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.single_point_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        btn_frame = tk.Frame(left, bg='#1e1e2e')
        btn_frame.pack(pady=15)
        
        tk.Button(btn_frame, text="Построить прогноз для точки", 
                  command=self.build_single_point_forecast,
                  bg='#5a5a8a', fg='white', font=('Arial', 10, 'bold'),
                  padx=20, pady=5).pack(side=tk.LEFT, padx=10)
        
        tk.Button(btn_frame, text="Очистить", 
                  command=self.clear_single_point_forecast,
                  bg='#8a5a5a', fg='white', font=('Arial', 10, 'bold'),
                  padx=20, pady=5).pack(side=tk.LEFT, padx=10)
        
        right = ttk.Frame(paned)
        paned.add(right, weight=2)
        
        
        graph_notebook = ttk.Notebook(right)
        graph_notebook.pack(fill=tk.BOTH, expand=True, pady=5)
        
        
        forecast_tab = ttk.Frame(graph_notebook)
        graph_notebook.add(forecast_tab, text="Прогнозные значения")
        
        self.fig_single_point = Figure(figsize=(6, 3), dpi=100, facecolor='#2a2a3e')
        self.ax_single_point = self.fig_single_point.add_subplot(111)
        self.ax_single_point.set_facecolor('#2a2a3e')
        self.ax_single_point.tick_params(colors='white')
        self.ax_single_point.set_xlabel("Эпоха", color='white')
        self.ax_single_point.set_ylabel("Значение", color='white')
        self.ax_single_point.set_title("Прогнозные значения", color='white')
        self.canvas_single_point = FigureCanvasTkAgg(self.fig_single_point, master=forecast_tab)
        self.canvas_single_point.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        response_tab = ttk.Frame(graph_notebook)
        graph_notebook.add(response_tab, text="Функция отклика S(t)")
        
        self.fig_point_response = Figure(figsize=(6, 3), dpi=100, facecolor='#2a2a3e')
        self.ax_point_response = self.fig_point_response.add_subplot(111)
        self.ax_point_response.set_facecolor('#2a2a3e')
        self.ax_point_response.tick_params(colors='white')
        self.ax_point_response.set_xlabel("μ", color='white')
        self.ax_point_response.set_ylabel("α", color='white')
        self.ax_point_response.set_title("Функция отклика S(t) для точки", color='white')
        self.canvas_point_response = FigureCanvasTkAgg(self.fig_point_response, master=response_tab)
        self.canvas_point_response.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        response_params = tk.Frame(response_tab, bg='#2a2a3e', height=35)
        response_params.pack(side=tk.BOTTOM, fill=tk.X)
        response_params.pack_propagate(False)
        
        self.show_s_point = tk.BooleanVar(value=True)
        self.show_s_plus_point = tk.BooleanVar(value=False)
        self.show_s_minus_point = tk.BooleanVar(value=False)
        
        tk.Checkbutton(response_params, text="S(t)", variable=self.show_s_point, bg='#2a2a3e', fg='white',
                       command=self.plot_point_response_function).pack(side=tk.LEFT, padx=10)
        tk.Checkbutton(response_params, text="S+(t)", variable=self.show_s_plus_point, bg='#2a2a3e', fg='white',
                       command=self.plot_point_response_function).pack(side=tk.LEFT, padx=10)
        tk.Checkbutton(response_params, text="S-(t)", variable=self.show_s_minus_point, bg='#2a2a3e', fg='white',
                       command=self.plot_point_response_function).pack(side=tk.LEFT, padx=10)
        
        
        tk.Label(right, text="Прогнозные значения", 
                 bg='#1e1e2e', fg='#ccccff', font=('Arial', 10, 'bold')).pack(pady=(10,0))
        
        table_frame = tk.Frame(right)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        scroll_y_tab = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
        scroll_x_tab = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        
        self.single_point_table = ttk.Treeview(table_frame, yscrollcommand=scroll_y_tab.set,
                                                xscrollcommand=scroll_x_tab.set, height=15)
        scroll_y_tab.config(command=self.single_point_table.yview)
        scroll_x_tab.config(command=self.single_point_table.xview)
        
        scroll_y_tab.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x_tab.pack(side=tk.BOTTOM, fill=tk.X)
        self.single_point_table.pack(fill=tk.BOTH, expand=True)
        
        self.single_point_table["columns"] = ["Эпоха", "Реал. знач.", "α=0.1", "α=0.4", "α=0.7", "α=0.9"]
        self.single_point_table["show"] = "headings"
        
        col_widths = {"Эпоха": 80, "Реал. знач.": 120, "α=0.1": 100, "α=0.4": 100, "α=0.7": 100, "α=0.9": 100}
        for col, width in col_widths.items():
            self.single_point_table.heading(col, text=col)
            self.single_point_table.column(col, width=width, anchor="center")
        
        self.init_single_point_list()
    



    def init_points_list_level2(self):
        self.all_points_list_level2.delete(0, tk.END)
        self.block_points_list_level2.delete(0, tk.END)
        self.block_points_level2 = {"А": [], "Б": []}
        
        for i, col in enumerate(self.db.point_columns, 1):
            self.all_points_list_level2.insert(tk.END, str(i))
    



    def init_single_point_list(self):
        self.single_point_listbox.delete(0, tk.END)
        for i, col in enumerate(self.db.point_columns, 1):
            self.single_point_listbox.insert(tk.END, f"{i}. {col}")
    




    def load_database(self):
        file_path = filedialog.askopenfilename(filetypes=[("SQLite", "*.db *.sqlite")])
        if not file_path:
            return
        
        self.status_label.config(text="Загрузка...")
        self.root.update()
        
        if self.db.connect(file_path):
            self.update_data_tree()
            self.init_points_list_level2()
            self.init_single_point_list()
            
            mu_vals, alpha_vals = self.db.get_mu_alpha_from_db()
            if mu_vals and alpha_vals and len(mu_vals) > 0 and mu_vals[0] != 0:
                self.mu_values = mu_vals
                self.alpha_values = alpha_vals
                self.calculate_all_from_mu_alpha()
            else:
                self.calculate_mu_alpha()
            
            self.status_label.config(text=f"Загружено: {len(self.db.epochs)} эпох, {len(self.db.point_columns)} точек")
            messagebox.showinfo("Успех", f"БД загружена!\nЭпох: {len(self.db.epochs)}\nТочек: {len(self.db.point_columns)}")
    




    def update_data_tree(self):
        for item in self.data_tree.get_children():
            self.data_tree.delete(item)
        
        if not self.db.current_table:
            return
        
        cols = list(self.db.current_table[0].keys())
        self.data_tree["columns"] = cols
        self.data_tree["show"] = "headings"
        
        for col in cols:
            self.data_tree.heading(col, text=col)
            self.data_tree.column(col, width=100)
        
        for row in self.db.current_table:
            values = [str(row[col]) for col in cols]
            self.data_tree.insert("", tk.END, values=values)
    



    def apply_error(self):
        try:
            self.E = float(self.error_entry.get().replace(',', '.'))
            self.status_label.config(text=f"Погрешность установлена: {self.E}")
            if self.mu_values:
                self.calculate_all_from_mu_alpha()
        except:
            messagebox.showerror("Ошибка", "Введите корректное число!")
    




    def add_row(self):
        if not self.db.current_table:
            messagebox.showerror("Ошибка", "Сначала загрузите базу данных!")
            return
        
        position_window = tk.Toplevel(self.root)
        position_window.title("Выбор позиции")
        position_window.geometry("300x150")
        position_window.configure(bg='#1e1e2e')
        
        tk.Label(position_window, text="Введите номер эпохи,", bg='#1e1e2e', fg='white').pack(pady=5)
        tk.Label(position_window, text="после которой вставить новую строку:", bg='#1e1e2e', fg='white').pack(pady=0)
        tk.Label(position_window, text="(0 — вставить в начало)", bg='#1e1e2e', fg='#8888aa', font=('Arial', 8)).pack(pady=2)
        
        entry = tk.Entry(position_window, width=10)
        entry.pack(pady=10)
        
        result = {"position": None}
        




        def on_ok():
            try:
                pos = int(entry.get())
                if pos < 0:
                    raise ValueError
                if pos > len(self.db.epochs):
                    pos = len(self.db.epochs)
                result["position"] = pos
                position_window.destroy()
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректное число (0 или номер эпохи)!")
        
        tk.Button(position_window, text="OK", command=on_ok, bg='#5a5a8a', fg='white').pack(pady=5)
        
        self.root.wait_window(position_window)
        
        if result["position"] is None:
            return
        
        insert_after = result["position"]
        
        last_row = self.db.current_table[-1]
        
        new_values = []
        for col in self.db.column_names:
            if col == "Эпоха":
                new_values.append(0)
            elif col in self.db.point_columns:
                old_val = last_row[col] if isinstance(last_row[col], (int, float)) else float(last_row[col])
                delta = random.uniform(-0.0005, 0.0005)
                new_val = old_val + delta
                new_values.append(round(new_val, 6))
            else:
                new_values.append(last_row.get(col, ""))
        
        if insert_after == 0:
            position = 1
        else:
            position = insert_after + 1
        
        if self.db.insert_row_at_position(new_values, position):
            self.update_data_tree()
            self.init_points_list_level2()
            self.init_single_point_list()
            self.calculate_mu_alpha()
            self.status_label.config(text=f"Добавлена новая эпоха на позицию {position}. Всего эпох: {len(self.db.epochs)}")
            messagebox.showinfo("Успех", f"Добавлена новая эпоха!\nВсего эпох: {len(self.db.epochs)}")
    




    def delete_row(self):
        if not self.db.current_table or len(self.db.current_table) <= 1:
            messagebox.showerror("Ошибка", "Нельзя удалить последнюю строку!")
            return
        
        selected = self.data_tree.selection()
        if not selected:
            messagebox.showerror("Ошибка", "Выберите строку для удаления!")
            return
        
        item = selected[0]
        values = self.data_tree.item(item, "values")
        epoch = int(values[0])
        
        if messagebox.askyesno("Подтверждение", f"Удалить эпоху {epoch}?"):
            if self.db.delete_row(epoch):
                self.update_data_tree()
                self.init_points_list_level2()
                self.init_single_point_list()
                self.calculate_mu_alpha()
                self.status_label.config(text=f"Удалена эпоха {epoch}. Всего эпох: {len(self.db.epochs)}")
                messagebox.showinfo("Успех", f"Эпоха {epoch} удалена!\nВсего эпох: {len(self.db.epochs)}")
    




    def save_changes(self):
        messagebox.showinfo("Информация", "Изменения сохранены")
    


    
    def calculate_vector_length(self, values):
        return math.sqrt(sum(v**2 for v in values))
    



    def calculate_angle(self, current_values, ref_values, ref_length, current_length):
        dot_product = sum(r * c for r, c in zip(ref_values, current_values))
        if ref_length * current_length == 0:
            return math.pi / 2
        cos_theta = dot_product / (ref_length * current_length)
        cos_theta = max(-1, min(1, cos_theta))
        return math.acos(cos_theta)
    



    def calculate_mu_alpha(self):
        if not self.db.current_table:
            messagebox.showerror("Ошибка", "Сначала загрузите базу данных!")
            return
        
        self.status_label.config(text="Расчет μ и α...")
        self.root.update()
        
        try:
            epochs = self.db.epochs
            all_values = []
            for epoch in epochs:
                all_values.append(self.db.get_values_for_epoch(epoch))
            
            ref_values = all_values[0]
            ref_length = self.calculate_vector_length(ref_values)
            
            self.mu_values = []
            self.alpha_values = []
            
            for i, values in enumerate(all_values):
                mu = self.calculate_vector_length(values)
                if i == 0:
                    alpha = 0.0
                else:
                    alpha = self.calculate_angle(values, ref_values, ref_length, mu)
                
                self.mu_values.append(mu)
                self.alpha_values.append(alpha)
                self.db.update_mu_alpha_in_db(epochs[i], mu, alpha)
            
            self.calculate_all_from_mu_alpha()
            
            self.status_label.config(text="Расчет μ и α завершен")
            messagebox.showinfo("Успех", f"Расчет завершен!\nОбработано {len(epochs)} эпох")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка расчета: {e}")
            self.status_label.config(text="Ошибка расчета")
    




    def calculate_all_from_mu_alpha(self):
        if not self.mu_values:
            return
        
        self.create_offset_tables()
        self.calculate_R_L_status()
        self.calculate_forecasts()
        self.update_tables()
        self.plot_response_function()
        
        if self.mu_values:
            forecast_table = self.create_forecast_table(self.mu_values, "μ")
            self.forecast_tables["μ"] = forecast_table
            self.draw_forecast_chart(forecast_table, "μ")
            self.forecast_type_combo.set("μ")
    




    def create_offset_tables(self):
        if not self.mu_values:
            return
        
        all_values = []
        for epoch in self.db.epochs:
            all_values.append(self.db.get_values_for_epoch(epoch))
        
        ref_values = all_values[0]
        mu_ref = self.calculate_vector_length(ref_values)
        
        self.mu_plus_values = []
        self.mu_minus_values = []
        self.alpha_plus_values = []
        self.alpha_minus_values = []
        
        for i, values in enumerate(all_values):
            plus_values = [v + self.E for v in values]
            minus_values = [v - self.E for v in values]
            mu_plus = self.calculate_vector_length(plus_values)
            mu_minus = self.calculate_vector_length(minus_values)
            
            self.mu_plus_values.append(mu_plus)
            self.mu_minus_values.append(mu_minus)
            
            if i == 0:
                alpha_plus = 0.0
                alpha_minus = 0.0
            else:
                dot_plus = sum(r * (v + self.E) for r, v in zip(ref_values, values))
                cos_theta_plus = dot_plus / (mu_ref * mu_plus)
                cos_theta_plus = max(-1, min(1, cos_theta_plus))
                alpha_plus = math.acos(cos_theta_plus)
                
                dot_minus = sum(r * (v - self.E) for r, v in zip(ref_values, values))
                cos_theta_minus = dot_minus / (mu_ref * mu_minus)
                cos_theta_minus = max(-1, min(1, cos_theta_minus))
                alpha_minus = math.acos(cos_theta_minus)
            
            self.alpha_plus_values.append(alpha_plus)
            self.alpha_minus_values.append(alpha_minus)
    




    def calculate_R_L_status(self):
        if not self.mu_values:
            return
        
        first_mu = self.mu_values[0]
        n = len(self.mu_values)
        
        self.R_values = []
        self.L_values = []
        self.status_values = []
        
        for i in range(n):
            R = (self.mu_plus_values[i] - self.mu_minus_values[i]) / 2
            L = abs(self.mu_values[i] - first_mu) if i > 0 else 0
            
            self.R_values.append(R)
            self.L_values.append(L)
            
            if i == 0:
                status = "Эталон"
            elif L < R:
                status = "Не изменяемое"
            elif abs(L - R) < 0.0000001:
                status = "Предаварийное"
            else:
                status = "Аварийное"
            
            self.status_values.append(status)
    



    def calculate_forecasts(self):
        if not self.mu_values:
            return
        
        for a in self.ALPHA_VALUES:
            self.forecast_mu[a] = self.exponential_forecast(self.mu_values, a)
            self.forecast_alpha[a] = self.exponential_forecast(self.alpha_values, a)
            self.forecast_mu_plus[a] = self.exponential_forecast(self.mu_plus_values, a)
            self.forecast_mu_minus[a] = self.exponential_forecast(self.mu_minus_values, a)
            self.forecast_alpha_plus[a] = self.exponential_forecast(self.alpha_plus_values, a)
            self.forecast_alpha_minus[a] = self.exponential_forecast(self.alpha_minus_values, a)
        
        self.forecast_mu_value = self.forecast_mu[0.9]
        self.forecast_alpha_value = self.forecast_alpha[0.9]
        self.forecast_mu_plus_val = self.forecast_mu_plus[0.9]
        self.forecast_mu_minus_val = self.forecast_mu_minus[0.9]
        self.forecast_alpha_plus_val = self.forecast_alpha_plus[0.9]
        self.forecast_alpha_minus_val = self.forecast_alpha_minus[0.9]
        self.forecast_R = (self.forecast_mu_plus_val - self.forecast_mu_minus_val) / 2
        self.forecast_L = abs(self.forecast_mu_value - self.mu_values[0])
        
        if self.forecast_L < self.forecast_R:
            self.forecast_status = "Не изменяемое"
        elif abs(self.forecast_L - self.forecast_R) < 0.0000001:
            self.forecast_status = "Предаварийное"
        else:
            self.forecast_status = "Аварийное"
    




    def exponential_forecast(self, values, alpha):
        if not values or len(values) < 2:
            return values[-1] if values else 0
        avg = sum(values) / len(values)
        last = values[-1]
        return alpha * avg + (1 - alpha) * last 
    




    def create_forecast_table(self, values, name):
        n = len(values)
        if n == 0:
            return {}
        
        avg_val = sum(values) / n
        
        forecast_data = {
            'epochs': list(range(n)) + ['Прогноз'],
            'values': values.copy() + [None],
        }
        
        forecasts = {a: [] for a in self.ALPHA_VALUES}
        prev = {a: None for a in self.ALPHA_VALUES}
        
        for i, real_val in enumerate(values):
            for a in self.ALPHA_VALUES:
                if i == 0:
                    f = a * real_val + (1 - a) * avg_val
                else:
                    f = a * real_val + (1 - a) * prev[a]
                forecasts[a].append(f)
                prev[a] = f
        
        for a in self.ALPHA_VALUES:
            avg_f = sum(forecasts[a]) / n
            last_f = forecasts[a][-1]
            forecast_f = a * avg_f + (1 - a) * last_f
            forecasts[a].append(forecast_f)
        
        for a in self.ALPHA_VALUES:
            forecast_data[f'forecast_{a}'] = forecasts[a]
        
        return forecast_data
    



    
    def update_forecast_table_display(self, forecast_type):
        forecast_table = self.forecast_tables.get(forecast_type, {})
        
        for item in self.mu_alpha_tree.get_children():
            self.mu_alpha_tree.delete(item)
        
        if not forecast_table:
            return
        
        n = len(self.db.epochs)
        
        if forecast_type == "μ":
            real_values = self.mu_values        
        elif forecast_type == "μ+E":
            real_values = self.mu_plus_values
        elif forecast_type == "μ-E":
            real_values = self.mu_minus_values
        elif forecast_type == "α":
            real_values = self.alpha_values
        elif forecast_type == "α+E":
            real_values = self.alpha_plus_values
        elif forecast_type == "α-E":
            real_values = self.alpha_minus_values
        else:
            real_values = self.mu_values
        
        for i, ep in enumerate(self.db.epochs):
            row_values = [
                ep,
                round(real_values[i], 6) if i < len(real_values) else 0,
                round(forecast_table.get('forecast_0.1', [0])[i], 6) if i < len(forecast_table.get('forecast_0.1', [])) else 0,
                round(forecast_table.get('forecast_0.4', [0])[i], 6) if i < len(forecast_table.get('forecast_0.4', [])) else 0,
                round(forecast_table.get('forecast_0.7', [0])[i], 6) if i < len(forecast_table.get('forecast_0.7', [])) else 0,
                round(forecast_table.get('forecast_0.9', [0])[i], 6) if i < len(forecast_table.get('forecast_0.9', [])) else 0,
            ]
            self.mu_alpha_tree.insert("", tk.END, values=row_values)
        
        forecast_row = [
            "Прогноз", "",
            round(forecast_table.get('forecast_0.1', [0])[-1], 6) if forecast_table.get('forecast_0.1') else 0,
            round(forecast_table.get('forecast_0.4', [0])[-1], 6) if forecast_table.get('forecast_0.4') else 0,
            round(forecast_table.get('forecast_0.7', [0])[-1], 6) if forecast_table.get('forecast_0.7') else 0,
            round(forecast_table.get('forecast_0.9', [0])[-1], 6) if forecast_table.get('forecast_0.9') else 0,
        ]
        self.mu_alpha_tree.insert("", tk.END, values=forecast_row, tags=("forecast",))
        self.mu_alpha_tree.tag_configure("forecast", background="#3a3a5e")
    




    def draw_forecast_chart(self, forecast_data, title):
        if not forecast_data:
            return
        
        self.ax_forecast.clear()
        self.ax_forecast.set_facecolor('#2a2a3e')
        self.ax_forecast.tick_params(colors='white')
        self.ax_forecast.set_xlabel("Эпоха", color='white')
        self.ax_forecast.set_ylabel("Значение", color='white')
        self.ax_forecast.set_title("Прогнозные значения", color='white')
        
        n = len(forecast_data['epochs']) - 1
        colors = ['#1E90FF', '#FF4500', '#32CD32', '#FFA500']
        
        real_values = forecast_data['values'][:n]
        self.ax_forecast.plot(range(1, n+1), real_values, 'ko-', linewidth=2, markersize=6, label='Реальные значения')
        
        for j, a in enumerate(self.ALPHA_VALUES):
            key = f'forecast_{a}'
            if key in forecast_data:
                values = forecast_data[key]
                x_vals = list(range(1, len(values)+1))
                self.ax_forecast.plot(x_vals, values, '--', linewidth=1.5, 
                                      color=colors[j], label=f'α = {a}')
                self.ax_forecast.scatter(x_vals[-1], values[-1], 
                                    color=colors[j], s=120, marker='D',
                                    edgecolors='black', linewidth=1, zorder=5)
        

        self.ax_forecast.scatter([], [], color='gray', s=120, marker='D',
                                    edgecolors='black', linewidth=1, label='Прогноз')
        
        self.ax_forecast.legend(loc='best', facecolor='#2a2a3e', labelcolor='white')
        self.ax_forecast.grid(True, alpha=0.3, color='gray')
        self.canvas_forecast.draw()
    




    def on_forecast_type_changed(self, event):
        selected = self.forecast_type_combo.get()
        if not selected:
            return
        
        if selected in self.forecast_tables:
            self.draw_forecast_chart(self.forecast_tables[selected], selected)
            self.update_forecast_table_display(selected)
        else:
            if selected == "μ" and self.mu_values:
                table = self.create_forecast_table(self.mu_values, selected)
            elif selected == "μ+E" and self.mu_plus_values:
                table = self.create_forecast_table(self.mu_plus_values, selected)
            elif selected == "μ-E" and self.mu_minus_values:
                table = self.create_forecast_table(self.mu_minus_values, selected)
            elif selected == "α" and self.alpha_values:
                table = self.create_forecast_table(self.alpha_values, selected)
            elif selected == "α+E" and self.alpha_plus_values:
                table = self.create_forecast_table(self.alpha_plus_values, selected)
            elif selected == "α-E" and self.alpha_minus_values:
                table = self.create_forecast_table(self.alpha_minus_values, selected)
            else:
                return
            
            self.forecast_tables[selected] = table
            self.draw_forecast_chart(table, selected)
            self.update_forecast_table_display(selected)
    



    def plot_response_function(self):
        if not self.mu_values or not self.alpha_values:
            return
        
        self.ax_response.clear()
        self.ax_response.set_facecolor('#2a2a3e')
        self.ax_response.tick_params(colors='white')
        self.ax_response.set_xlabel("μ", color='white')
        self.ax_response.set_ylabel("α", color='white')
        self.ax_response.set_title("Функция отклика S(t)", color='white')
        
        n = len(self.mu_values)
        
        if self.show_s.get():
            self.ax_response.plot(self.mu_values[:n], self.alpha_values[:n], 
                                 'yo-', linewidth=2, markersize=6, label='S(t)', color='#FFD700')
            self.ax_response.scatter(self.forecast_mu[0.9], self.forecast_alpha[0.9],
                                    color='blue', s=120, marker='D',
                                    edgecolors='black', linewidth=1, zorder=5)
            for i, ep in enumerate(self.db.epochs):
                self.ax_response.annotate(str(ep), (self.mu_values[i], self.alpha_values[i]),
                                         color='white', fontsize=8, xytext=(5,5), textcoords='offset points')
        
        if self.show_s_plus.get() and self.mu_plus_values and self.alpha_plus_values:
            self.ax_response.plot(self.mu_plus_values[:n], self.alpha_plus_values[:n],
                                 'r--', linewidth=1.5, label='S+(t)', color='#FF4444')
            self.ax_response.scatter(self.forecast_mu_plus[0.9], self.forecast_alpha_plus[0.9],
                                    color='red', s=120, marker='D',
                                    edgecolors='black', linewidth=1, zorder=5)
        
        if self.show_s_minus.get() and self.mu_minus_values and self.alpha_minus_values:
            self.ax_response.plot(self.mu_minus_values[:n], self.alpha_minus_values[:n],
                                 'g--', linewidth=1.5, label='S-(t)', color='#44FF44')
            self.ax_response.scatter(self.forecast_mu_minus[0.9], self.forecast_alpha_minus[0.9],
                                    color='green', s=120, marker='D',
                                    edgecolors='black', linewidth=1, zorder=5)
        
        self.ax_response.legend(loc='best', facecolor='#2a2a3e', labelcolor='white')
        self.ax_response.grid(True, alpha=0.3, color='gray')
        self.canvas_response.draw()
    




    def update_tables(self):
        for item in self.status_tree.get_children():
            self.status_tree.delete(item)
        
        self.status_tree["columns"] = ["Эпоха", "μ+E", "μ", "μ-E", "α+E", "α", "α-E", "R", "L", "Статус"]
        self.status_tree["show"] = "headings"
        
        col_configs = [
            ("Эпоха", 80, "center"),
            ("μ+E", 100, "center"),
            ("μ", 100, "center"),
            ("μ-E", 100, "center"),
            ("α+E", 100, "center"),
            ("α", 100, "center"),
            ("α-E", 100, "center"),
            ("R", 80, "center"),
            ("L", 80, "center"),
            ("Статус", 120, "center")
        ]
        
        for col, width, anchor in col_configs:
            self.status_tree.heading(col, text=col)
            self.status_tree.column(col, width=width, anchor=anchor)
        
        if not self.mu_values:
            return
        
        first_mu = self.mu_values[0]
        n = len(self.db.epochs)
        color_map = {"Аварийное": "red", "Предаварийное": "orange", 
                     "Не изменяемое": "green", "Эталон": "blue"}
        
        for i, ep in enumerate(self.db.epochs):
            m_val = self.mu_values[i]
            a_val = self.alpha_values[i]
            m_plus_val = self.mu_plus_values[i] if i < len(self.mu_plus_values) else 0
            m_minus_val = self.mu_minus_values[i] if i < len(self.mu_minus_values) else 0
            a_plus_val = self.alpha_plus_values[i] if i < len(self.alpha_plus_values) else 0
            a_minus_val = self.alpha_minus_values[i] if i < len(self.alpha_minus_values) else 0
            
            r_val = abs(m_plus_val - m_minus_val) / 2
            l_val = abs(first_mu - m_val) if i > 0 else 0
            
            if i == 0:
                status = "Эталон"
            elif l_val < r_val:
                status = "Не изменяемое"
            elif abs(l_val - r_val) < 0.0000001:
                status = "Предаварийное"
            else:
                status = "Аварийное"
            
            row_id = self.status_tree.insert("", tk.END, values=[
                ep, round(m_plus_val, 6), round(m_val, 6), round(m_minus_val, 6),
                round(a_plus_val, 6), round(a_val, 6), round(a_minus_val, 6),
                round(r_val, 6), round(l_val, 6), status
            ])
            
            if status in color_map:
                self.status_tree.tag_configure(status, foreground=color_map[status])
                self.status_tree.item(row_id, tags=(status,))
        
        forecast_row_id = self.status_tree.insert("", tk.END, values=[
            "Прогноз",
            round(self.forecast_mu_plus_val, 6),
            round(self.forecast_mu_value, 6),
            round(self.forecast_mu_minus_val, 6),
            round(self.forecast_alpha_plus_val, 6),
            round(self.forecast_alpha_value, 6),
            round(self.forecast_alpha_minus_val, 6),
            round(self.forecast_R, 6),
            round(self.forecast_L, 6),
            self.forecast_status
        ], tags=("forecast",))
        
        self.status_tree.tag_configure("forecast", background="#3a3a5e")
        
        current_type = self.forecast_type_combo.get()
        if current_type and current_type in self.forecast_tables:
            self.update_forecast_table_display(current_type)
        elif self.mu_values:
            forecast_table = self.create_forecast_table(self.mu_values, "μ")
            self.forecast_tables["μ"] = forecast_table
            self.update_forecast_table_display("μ")
    



    
    def on_block_selected_level2(self, event):
        self.current_block_level2 = self.block_combo_level2.get()
        if not self.current_block_level2:
            return
        
        self.block_points_list_level2.delete(0, tk.END)
        
        self.all_points_list_level2.delete(0, tk.END)
        for i, col in enumerate(self.db.point_columns, 1):
            self.all_points_list_level2.insert(tk.END, str(i))
        
        block_key = self.current_block_level2
        if block_key in self.block_points_level2:
            for point in self.block_points_level2[block_key]:
                for idx in range(self.all_points_list_level2.size()):
                    if self.all_points_list_level2.get(idx) == str(point):
                        self.all_points_list_level2.delete(idx)
                        break
                self.block_points_list_level2.insert(tk.END, str(point))
    




    def move_to_block_level2(self, event):
        if not hasattr(self, 'current_block_level2') or not self.current_block_level2:
            messagebox.showwarning("Внимание", "Выберите блок!")
            return
        
        sel = self.all_points_list_level2.curselection()
        if not sel:
            return
        
        num = int(self.all_points_list_level2.get(sel[0]))
        block_key = self.current_block_level2
        
        if block_key not in self.block_points_level2:
            self.block_points_level2[block_key] = []
        
        if num in self.block_points_level2[block_key]:
            return
        
        self.block_points_level2[block_key].append(num)
        self.block_points_level2[block_key].sort()
        self.block_points_list_level2.insert(tk.END, str(num))
        self.all_points_list_level2.delete(sel[0])
    



    
    def move_from_block_level2(self, event):
        sel = self.block_points_list_level2.curselection()
        if not sel:
            return
        
        num = int(self.block_points_list_level2.get(sel[0]))
        block_key = self.current_block_level2
        
        if block_key in self.block_points_level2 and num in self.block_points_level2[block_key]:
            self.block_points_level2[block_key].remove(num)
            self.block_points_list_level2.delete(sel[0])
            
            all_nums = []
            for i in range(self.all_points_list_level2.size()):
                all_nums.append(int(self.all_points_list_level2.get(i)))
            all_nums.append(num)
            all_nums.sort()
            
            self.all_points_list_level2.delete(0, tk.END)
            for n in all_nums:
                self.all_points_list_level2.insert(tk.END, str(n))
    




    def calculate_block_level2(self):
        if not hasattr(self, 'current_block_level2') or not self.current_block_level2:
            messagebox.showerror("Ошибка", "Выберите блок!")
            return
        
        block_key = self.current_block_level2
        points = self.block_points_level2.get(block_key, [])
        
        if len(points) < 2:
            messagebox.showerror("Ошибка", f"В блоке {block_key} минимум 2 точки!")
            return
        
        self.status_label.config(text=f"Расчёт блока {block_key}...")
        self.root.update()
        
        try:
            block_cols = [self.db.point_columns[p-1] for p in points]
            
            block_data = []
            epochs = []
            for row in self.db.current_table:
                vals = []
                for col in block_cols:
                    v = row[col]
                    if isinstance(v, str):
                        v = float(v.replace(',', '.'))
                    vals.append(float(v))
                block_data.append(vals)
                epochs.append(row["Эпоха"])
            
            z_table = []
            z_plus_table = []
            z_minus_table = []
            
            for i, vals in enumerate(block_data):
                z_plus = [v + self.E for v in vals]
                z_minus = [v - self.E for v in vals]
                z_table.append(vals)
                z_plus_table.append(z_plus)
                z_minus_table.append(z_minus)
            
            m_values, a_values = self.calculate_m_a_for_block(z_table, epochs)
            m_plus_values, a_plus_values = self.calculate_m_a_for_block(z_plus_table, epochs)
            m_minus_values, a_minus_values = self.calculate_m_a_for_block(z_minus_table, epochs)
            
            self.block_m_values = m_values
            self.block_a_values = a_values
            self.block_m_plus_values = m_plus_values
            self.block_m_minus_values = m_minus_values
            self.block_a_plus_values = a_plus_values
            self.block_a_minus_values = a_minus_values
            self.block_epochs_level2 = epochs
            
            self.block_forecast_tables_level2[f"μ_{block_key}"] = self.create_forecast_table(m_values, f"μ_{block_key}")
            self.block_forecast_tables_level2[f"μ+E_{block_key}"] = self.create_forecast_table(m_plus_values, f"μ+E_{block_key}")
            self.block_forecast_tables_level2[f"μ-E_{block_key}"] = self.create_forecast_table(m_minus_values, f"μ-E_{block_key}")
            self.block_forecast_tables_level2[f"α_{block_key}"] = self.create_forecast_table(a_values, f"α_{block_key}")
            self.block_forecast_tables_level2[f"α+E_{block_key}"] = self.create_forecast_table(a_plus_values, f"α+E_{block_key}")
            self.block_forecast_tables_level2[f"α-E_{block_key}"] = self.create_forecast_table(a_minus_values, f"α-E_{block_key}")
            
            self.combo_tables_level2['values'] = [
                f"μ_{block_key}", f"μ+E_{block_key}", f"μ-E_{block_key}",
                f"α_{block_key}", f"α+E_{block_key}", f"α-E_{block_key}"
            ]
            if self.combo_tables_level2['values']:
                self.combo_tables_level2.set(f"μ_{block_key}")
            
            self.fill_status_table_level2(block_key)
            
            self.update_block_forecast_display(f"μ_{block_key}")
            
            self.draw_phase_trajectories_level2()
            self.plot_response_function_level2()
            
            self.status_label.config(text=f"Расчёт блока {block_key} завершён")
            messagebox.showinfo("Успех", f"Расчёт для блока {block_key} завершён!\n"
                                f"Точек в блоке: {len(points)}\nЭпох: {len(epochs)}")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка расчёта: {e}")
            self.status_label.config(text="Ошибка расчёта")
    




    def calculate_m_a_for_block(self, block_data, epochs):
        n = len(block_data)
        if n == 0:
            return [], []
        
        m_values = []
        a_values = []
        
        ref_values = block_data[0]
        m_ref = math.sqrt(sum(v**2 for v in ref_values))
        
        for i, vals in enumerate(block_data):
            m = math.sqrt(sum(v**2 for v in vals))
            m_values.append(m)
            
            if i == 0:
                a = 0.0
            else:
                dot = sum(r * c for r, c in zip(ref_values, vals))
                cos_theta = dot / (m_ref * m)
                cos_theta = max(-1, min(1, cos_theta))
                a = math.acos(cos_theta)
            a_values.append(a)
        
        return m_values, a_values
    




    def fill_status_table_level2(self, block_key):
        for item in self.block_status_tree_level2.get_children():
            self.block_status_tree_level2.delete(item)
        
        self.block_status_tree_level2["columns"] = ["Эпоха", "μ+E", "μ", "μ-E", "α+E", "α", "α-E", "R", "L", "Статус"]
        self.block_status_tree_level2["show"] = "headings"
        
        col_configs = [
            ("Эпоха", 80, "center"),
            ("μ+E", 100, "center"),
            ("μ", 100, "center"),
            ("μ-E", 100, "center"),
            ("α+E", 100, "center"),
            ("α", 100, "center"),
            ("α-E", 100, "center"),
            ("R", 80, "center"),
            ("L", 80, "center"),
            ("Статус", 120, "center")
        ]
        
        for col, width, anchor in col_configs:
            self.block_status_tree_level2.heading(col, text=col)
            self.block_status_tree_level2.column(col, width=width, anchor=anchor)
        
        if not self.block_m_values:
            return
        
        first_m = self.block_m_values[0]
        n = len(self.block_epochs_level2)
        
        color_map = {"Аварийное": "red", "Предаварийное": "orange", 
                     "Не изменяемое": "green", "Эталон": "blue"}
        
        for i, ep in enumerate(self.block_epochs_level2):
            m = self.block_m_values[i]
            m_plus = self.block_m_plus_values[i] if i < len(self.block_m_plus_values) else 0
            m_minus = self.block_m_minus_values[i] if i < len(self.block_m_minus_values) else 0
            a = self.block_a_values[i]
            a_plus = self.block_a_plus_values[i] if i < len(self.block_a_plus_values) else 0
            a_minus = self.block_a_minus_values[i] if i < len(self.block_a_minus_values) else 0
            
            r_val = abs(m_plus - m_minus) / 2
            l_val = abs(first_m - m) if i > 0 else 0
            
            if i == 0:
                status = "Эталон"
            elif l_val < r_val:
                status = "Не изменяемое"
            elif abs(l_val - r_val) < 0.0000001:
                status = "Предаварийное"
            else:
                status = "Аварийное"
            
            row_id = self.block_status_tree_level2.insert("", tk.END, values=[
                ep, round(m_plus, 6), round(m, 6), round(m_minus, 6),
                round(a_plus, 6), round(a, 6), round(a_minus, 6),
                round(r_val, 6), round(l_val, 6), status
            ])
            
            if status in color_map:
                self.block_status_tree_level2.tag_configure(status, foreground=color_map[status])
                self.block_status_tree_level2.item(row_id, tags=(status,))
        
        forecast_m = self.exponential_forecast(self.block_m_values, 0.9)
        forecast_m_plus = self.exponential_forecast(self.block_m_plus_values, 0.9)
        forecast_m_minus = self.exponential_forecast(self.block_m_minus_values, 0.9)
        forecast_a = self.exponential_forecast(self.block_a_values, 0.9)
        forecast_a_plus = self.exponential_forecast(self.block_a_plus_values, 0.9)
        forecast_a_minus = self.exponential_forecast(self.block_a_minus_values, 0.9)
        
        forecast_r = abs(forecast_m_plus - forecast_m_minus) / 2
        forecast_l = abs(forecast_m - first_m)
        
        if forecast_l < forecast_r:
            forecast_status = "Не изменяемое"
        elif abs(forecast_l - forecast_r) < 0.0000001:
            forecast_status = "Предаварийное"
        else:
            forecast_status = "Аварийное"
        
        forecast_row_id = self.block_status_tree_level2.insert("", tk.END, values=[
            "Прогноз", round(forecast_m_plus, 6), round(forecast_m, 6), round(forecast_m_minus, 6),
            round(forecast_a_plus, 6), round(forecast_a, 6), round(forecast_a_minus, 6),
            round(forecast_r, 6), round(forecast_l, 6), forecast_status
        ], tags=("forecast",))
        
        self.block_status_tree_level2.tag_configure("forecast", background="#3a3a5e")
        if forecast_status in color_map:
            self.block_status_tree_level2.tag_configure(f"forecast_{forecast_status}", foreground=color_map[forecast_status])
            self.block_status_tree_level2.item(forecast_row_id, tags=("forecast", f"forecast_{forecast_status}"))
    




    def update_block_forecast_display(self, table_name):
        if table_name not in self.block_forecast_tables_level2:
            return
        
        forecast_table = self.block_forecast_tables_level2[table_name]
        
        for item in self.block_mu_alpha_tree_level2.get_children():
            self.block_mu_alpha_tree_level2.delete(item)
        
        if not forecast_table:
            return
        
        n = len(self.block_epochs_level2)
        
        if table_name.startswith("μ"):
            if "+E" in table_name:
                real_values = self.block_m_plus_values
            elif "-E" in table_name:
                real_values = self.block_m_minus_values
            else:
                real_values = self.block_m_values
        else:
            if "+E" in table_name:
                real_values = self.block_a_plus_values
            elif "-E" in table_name:
                real_values = self.block_a_minus_values
            else:
                real_values = self.block_a_values
        
        for i, ep in enumerate(self.block_epochs_level2):
            row_values = [
                ep,
                round(real_values[i], 6) if i < len(real_values) else 0,
                round(forecast_table.get('forecast_0.1', [0])[i], 6) if i < len(forecast_table.get('forecast_0.1', [])) else 0,
                round(forecast_table.get('forecast_0.4', [0])[i], 6) if i < len(forecast_table.get('forecast_0.4', [])) else 0,
                round(forecast_table.get('forecast_0.7', [0])[i], 6) if i < len(forecast_table.get('forecast_0.7', [])) else 0,
                round(forecast_table.get('forecast_0.9', [0])[i], 6) if i < len(forecast_table.get('forecast_0.9', [])) else 0,
            ]
            self.block_mu_alpha_tree_level2.insert("", tk.END, values=row_values)
        
        forecast_row = [
            "Прогноз", "",
            round(forecast_table.get('forecast_0.1', [0])[-1], 6) if forecast_table.get('forecast_0.1') else 0,
            round(forecast_table.get('forecast_0.4', [0])[-1], 6) if forecast_table.get('forecast_0.4') else 0,
            round(forecast_table.get('forecast_0.7', [0])[-1], 6) if forecast_table.get('forecast_0.7') else 0,
            round(forecast_table.get('forecast_0.9', [0])[-1], 6) if forecast_table.get('forecast_0.9') else 0,
        ]
        self.block_mu_alpha_tree_level2.insert("", tk.END, values=forecast_row, tags=("forecast",))
        self.block_mu_alpha_tree_level2.tag_configure("forecast", background="#3a3a5e")
    




    def on_table_selected_level2(self, event):
        selected = self.combo_tables_level2.get()
        if not selected:
            return
        
        self.update_block_forecast_display(selected)
        self.draw_phase_trajectories_level2()
    



    def draw_phase_trajectories_level2(self):
        selected = self.combo_tables_level2.get()
        if not selected or selected not in self.block_forecast_tables_level2:
            return
        
        forecast_table = self.block_forecast_tables_level2[selected]
        if not forecast_table:
            return
        
        self.ax_phase_level2.clear()
        self.ax_phase_level2.set_facecolor('#2a2a3e')
        self.ax_phase_level2.tick_params(colors='white')
        self.ax_phase_level2.set_xlabel("Эпоха", color='white')
        self.ax_phase_level2.set_ylabel("Значение", color='white')
        self.ax_phase_level2.set_title(f"Прогнозные значения", color='white')
        
        n = len(self.block_epochs_level2)
        colors = ['#1E90FF', '#FF4500', '#32CD32', '#FFA500']
        
        if selected.startswith("μ"):
            if "+E" in selected:
                real_values = self.block_m_plus_values
            elif "-E" in selected:
                real_values = self.block_m_minus_values
            else:
                real_values = self.block_m_values
        else:
            if "+E" in selected:
                real_values = self.block_a_plus_values
            elif "-E" in selected:
                real_values = self.block_a_minus_values
            else:
                real_values = self.block_a_values
        
        self.ax_phase_level2.plot(range(1, n+1), real_values, 'ko-', linewidth=2, markersize=6, label='Реальные значения')
        
        for j, a in enumerate(self.ALPHA_VALUES):
            key = f'forecast_{a}'
            if key in forecast_table:
                values = forecast_table[key]
                x_vals = list(range(1, len(values)+1))
                self.ax_phase_level2.plot(x_vals, values, '--', linewidth=1.5, 
                                          color=colors[j], label=f'α = {a}')
                self.ax_phase_level2.scatter(x_vals[-1], values[-1], 
                                            color=colors[j], s=120, marker='D',
                                            edgecolors='black', linewidth=1, zorder=5)
        
        
        self.ax_phase_level2.scatter([], [], color='gray', s=120, marker='D',
                                    edgecolors='black', linewidth=1, label='Прогноз')
        
        self.ax_phase_level2.legend(loc='best', facecolor='#2a2a3e', labelcolor='white')
        self.ax_phase_level2.grid(True, alpha=0.3, color='gray')
        self.canvas_phase_level2.draw()
    




    def plot_response_function_level2(self):
        if not hasattr(self, 'block_m_values') or not self.block_m_values:
            return
        
        self.ax_response_level2.clear()
        self.ax_response_level2.set_facecolor('#2a2a3e')
        self.ax_response_level2.tick_params(colors='white')
        self.ax_response_level2.set_xlabel("μ", color='white')
        self.ax_response_level2.set_ylabel("α", color='white')
        self.ax_response_level2.set_title(f"Функция отклика S(t)", color='white')
        
        n = len(self.block_epochs_level2)
        
        if self.show_s_level2.get():
            self.ax_response_level2.plot(self.block_m_values[:n], self.block_a_values[:n], 
                                         'yo-', linewidth=2, markersize=6, label='S(t)', color='#FFD700')
            forecast_m = self.exponential_forecast(self.block_m_values, 0.9)
            forecast_a = self.exponential_forecast(self.block_a_values, 0.9)
            self.ax_response_level2.scatter(forecast_m, forecast_a, color='blue', s=120, marker='D',
                                            edgecolors='black', linewidth=1, zorder=5)
            for i, ep in enumerate(self.block_epochs_level2):
                self.ax_response_level2.annotate(str(ep), (self.block_m_values[i], self.block_a_values[i]),
                                                color='white', fontsize=8, xytext=(5,5), textcoords='offset points')
        
        if self.show_s_plus_level2.get() and hasattr(self, 'block_m_plus_values'):
            self.ax_response_level2.plot(self.block_m_plus_values[:n], self.block_a_plus_values[:n],
                                         'r--', linewidth=1.5, label='S+(t)', color='#FF4444')
            forecast_m_plus = self.exponential_forecast(self.block_m_plus_values, 0.9)
            forecast_a_plus = self.exponential_forecast(self.block_a_plus_values, 0.9)
            self.ax_response_level2.scatter(forecast_m_plus, forecast_a_plus, color='red', s=120, marker='D',
                                            edgecolors='black', linewidth=1, zorder=5)
        
        if self.show_s_minus_level2.get() and hasattr(self, 'block_m_minus_values'):
            self.ax_response_level2.plot(self.block_m_minus_values[:n], self.block_a_minus_values[:n],
                                         'g--', linewidth=1.5, label='S-(t)', color='#44FF44')
            forecast_m_minus = self.exponential_forecast(self.block_m_minus_values, 0.9)
            forecast_a_minus = self.exponential_forecast(self.block_a_minus_values, 0.9)
            self.ax_response_level2.scatter(forecast_m_minus, forecast_a_minus, color='green', s=120, marker='D',
                                            edgecolors='black', linewidth=1, zorder=5)
        

        self.ax_response_level2.scatter([], [], color='gray', s=120, marker='D',
                                        edgecolors='black', linewidth=1, label='Прогноз')
        
        self.ax_response_level2.legend(loc='best', facecolor='#2a2a3e', labelcolor='white')
        self.ax_response_level2.grid(True, alpha=0.3, color='gray')
        self.canvas_response_level2.draw()
    



    
    def build_single_point_forecast(self):
        sel = self.single_point_listbox.curselection()
        if not sel:
            messagebox.showwarning("Внимание", "Выберите точку!")
            return
        
        selected = self.single_point_listbox.get(sel[0])
        point_idx = int(selected.split('.')[0]) - 1
        point_name = self.db.point_columns[point_idx]
        
        self.status_label.config(text=f"Построение прогноза для точки {point_name}...")
        self.root.update()
        
        try:
            real_values = []
            for row in self.db.current_table:
                val = row[point_name]
                if isinstance(val, str):
                    val = float(val.replace(',', '.'))
                real_values.append(float(val))
            
            forecast_table = self.create_forecast_table(real_values, point_name)
            
            
            for item in self.single_point_table.get_children():
                self.single_point_table.delete(item)
            
            n = len(forecast_table['values']) - 1
            for i in range(n):
                self.single_point_table.insert("", tk.END, values=[
                    i+1,
                    round(forecast_table['values'][i], 6),
                    round(forecast_table['forecast_0.1'][i], 6),
                    round(forecast_table['forecast_0.4'][i], 6),
                    round(forecast_table['forecast_0.7'][i], 6),
                    round(forecast_table['forecast_0.9'][i], 6)
                ])
            
            self.single_point_table.insert("", tk.END, values=[
                "Прогноз", "",
                round(forecast_table['forecast_0.1'][-1], 6),
                round(forecast_table['forecast_0.4'][-1], 6),
                round(forecast_table['forecast_0.7'][-1], 6),
                round(forecast_table['forecast_0.9'][-1], 6)
            ], tags=("forecast",))
            self.single_point_table.tag_configure("forecast", background="#3a3a5e")
            self.ax_single_point.clear()
            self.ax_single_point.set_facecolor('#2a2a3e')
            self.ax_single_point.tick_params(colors='white')
            self.ax_single_point.set_xlabel("Эпоха", color='white')
            self.ax_single_point.set_ylabel("Значение", color='white')
            self.ax_single_point.set_title(f"Прогноз для точки {point_name}", color='white')
            
            colors = ['#1E90FF', '#FF4500', '#32CD32', '#FFA500']
            for j, a in enumerate(self.ALPHA_VALUES):
                key = f'forecast_{a}'
                if key in forecast_table:
                    values = forecast_table[key]
                    x_vals = list(range(1, len(values)+1))
                    self.ax_single_point.plot(x_vals, values, '--', color=colors[j], label=f'α = {a}')
                    self.ax_single_point.scatter(x_vals[-1], values[-1], color=colors[j], s=120, marker='D',
                                                edgecolors='black', linewidth=1, zorder=5)
            
            x_real = list(range(1, n+1))
            self.ax_single_point.plot(x_real, forecast_table['values'][:n], 'ko-', label='Реальные')
            
            # Серый ромб в легенде (один раз)
            self.ax_single_point.scatter([], [], color='gray', s=120, marker='D',
                                        edgecolors='black', linewidth=1, label='Прогноз')
            
            self.ax_single_point.legend(loc='best', facecolor='#2a2a3e', labelcolor='white')
            self.ax_single_point.grid(True, alpha=0.3, color='gray')
            self.canvas_single_point.draw()
            self.current_point_values = real_values
            self.current_point_name = point_name
            self.plot_point_response_function()
            
            self.status_label.config(text=f"Прогноз для точки {point_name} построен")
            messagebox.showinfo("Успех", f"Прогноз для точки '{point_name}' успешно построен!")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка построения прогноза: {e}")
            self.status_label.config(text="Ошибка")
    
    def plot_point_response_function(self):
        if not hasattr(self, 'current_point_values') or not self.current_point_values:
            return
        
        n = len(self.current_point_values)
        
        mu_values = [abs(v) for v in self.current_point_values]
        first_mu = mu_values[0] if mu_values else 0
        
        alpha_values = [0.0]
        for i in range(1, n):
            if mu_values[i-1] != 0:
                delta = abs(mu_values[i] - mu_values[i-1]) / max(abs(mu_values[i-1]), 0.0001)
                alpha = math.atan(delta)
            else:
                alpha = 0.0
            alpha_values.append(alpha)
        
        mu_plus_values = [abs(v + self.E) for v in self.current_point_values]
        mu_minus_values = [abs(v - self.E) for v in self.current_point_values]
        
        alpha_plus_values = [0.0]
        alpha_minus_values = [0.0]
        for i in range(1, n):
            if mu_plus_values[i-1] != 0:
                delta_plus = abs(mu_plus_values[i] - mu_plus_values[i-1]) / max(abs(mu_plus_values[i-1]), 0.0001)
                alpha_plus = math.atan(delta_plus)
            else:
                alpha_plus = 0.0
            alpha_plus_values.append(alpha_plus)
            
            if mu_minus_values[i-1] != 0:
                delta_minus = abs(mu_minus_values[i] - mu_minus_values[i-1]) / max(abs(mu_minus_values[i-1]), 0.0001)
                alpha_minus = math.atan(delta_minus)
            else:
                alpha_minus = 0.0
            alpha_minus_values.append(alpha_minus)
        
        forecast_mu = self.exponential_forecast(mu_values, 0.9)
        forecast_alpha = self.exponential_forecast(alpha_values, 0.9)
        forecast_mu_plus = self.exponential_forecast(mu_plus_values, 0.9)
        forecast_alpha_plus = self.exponential_forecast(alpha_plus_values, 0.9)
        forecast_mu_minus = self.exponential_forecast(mu_minus_values, 0.9)
        forecast_alpha_minus = self.exponential_forecast(alpha_minus_values, 0.9)
        
        self.ax_point_response.clear()
        self.ax_point_response.set_facecolor('#2a2a3e')
        self.ax_point_response.tick_params(colors='white')
        self.ax_point_response.set_xlabel("μ", color='white')
        self.ax_point_response.set_ylabel("α", color='white')
        self.ax_point_response.set_title(f"Функция отклика S(t) для точки {self.current_point_name}", color='white')
        
        if self.show_s_point.get():
            self.ax_point_response.plot(mu_values, alpha_values, 
                                        'yo-', linewidth=2, markersize=6, label='S(t)', color='#FFD700')
            self.ax_point_response.scatter(forecast_mu, forecast_alpha,
                                           color='blue', s=120, marker='D',
                                           edgecolors='black', linewidth=1, zorder=5)
            for i, ep in enumerate(self.db.epochs):
                self.ax_point_response.annotate(str(ep), (mu_values[i], alpha_values[i]),
                                                color='white', fontsize=8, xytext=(5,5), textcoords='offset points')
        
        if self.show_s_plus_point.get():
            self.ax_point_response.plot(mu_plus_values, alpha_plus_values,
                                        'r--', linewidth=1.5, label='S+(t)', color='#FF4444')
            self.ax_point_response.scatter(forecast_mu_plus, forecast_alpha_plus,
                                           color='red', s=120, marker='D',
                                           edgecolors='black', linewidth=1, zorder=5)
        
        if self.show_s_minus_point.get():
            self.ax_point_response.plot(mu_minus_values, alpha_minus_values,
                                        'g--', linewidth=1.5, label='S-(t)', color='#44FF44')
            self.ax_point_response.scatter(forecast_mu_minus, forecast_alpha_minus,
                                           color='green', s=120, marker='D',
                                           edgecolors='black', linewidth=1, zorder=5)
        

        self.ax_point_response.scatter([], [], color='gray', s=120, marker='D',
                                        edgecolors='black', linewidth=1, label='Прогноз')
        
        self.ax_point_response.legend(loc='best', facecolor='#2a2a3e', labelcolor='white')
        self.ax_point_response.grid(True, alpha=0.3, color='gray')
        self.canvas_point_response.draw()
    



    def clear_single_point_forecast(self):
        for item in self.single_point_table.get_children():
            self.single_point_table.delete(item)
        
        self.ax_single_point.clear()
        self.ax_single_point.set_facecolor('#2a2a3e')
        self.ax_single_point.tick_params(colors='white')
        self.ax_single_point.set_xlabel("Эпоха", color='white')
        self.ax_single_point.set_ylabel("Значение", color='white')
        self.ax_single_point.set_title("Прогнозные значения", color='white')
        self.canvas_single_point.draw()
        
        self.ax_point_response.clear()
        self.ax_point_response.set_facecolor('#2a2a3e')
        self.ax_point_response.tick_params(colors='white')
        self.ax_point_response.set_xlabel("μ", color='white')
        self.ax_point_response.set_ylabel("α", color='white')
        self.ax_point_response.set_title("Функция отклика S(t)", color='white')
        self.canvas_point_response.draw()
        
        self.single_point_listbox.selection_clear(0, tk.END)
        self.status_label.config(text="Выбор сброшен")
        
        if hasattr(self, 'current_point_values'):
            delattr(self, 'current_point_values')
        if hasattr(self, 'current_point_name'):
            delattr(self, 'current_point_name')


if __name__ == "__main__":
    root = tk.Tk()
    app = MonitoringApp(root)
    root.mainloop()