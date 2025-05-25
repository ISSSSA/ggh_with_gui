import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

ERROR_VECTOR = np.array([1, -1, 1])


class GGHModernGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("GGH Cryptography Tool")
        self.style = ttk.Style("darkly")

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        self.encrypt_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.encrypt_frame, text="Шифрование")
        self.setup_encryption_tab()

        self.about_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.about_frame, text="О программе")
        self.setup_about_tab()

    def setup_encryption_tab(self):
        matrix_frame = ttk.LabelFrame(self.encrypt_frame, text="Приватный базис (матрица)", padding=10)
        matrix_frame.pack(fill='x', padx=5, pady=5)

        self.matrix_text = tk.Text(matrix_frame, height=8, width=30, font=('Consolas', 10))
        self.matrix_text.pack(fill='both', expand=True)
        ttk.Button(matrix_frame, text="Пример матрицы", command=self.insert_sample_matrix,
                   bootstyle=(OUTLINE, INFO)).pack(pady=5)

        vector_frame = ttk.LabelFrame(self.encrypt_frame, text="Вектор сообщения", padding=10)
        vector_frame.pack(fill='x', padx=5, pady=5)

        self.vector_entry = ttk.Entry(vector_frame, font=('TkDefaultFont', 10))
        self.vector_entry.pack(fill='x', pady=5)
        ttk.Button(vector_frame, text="Пример вектора", command=self.insert_sample_vector,
                   bootstyle=(OUTLINE, INFO)).pack(pady=5)

        button_frame = ttk.Frame(self.encrypt_frame)
        button_frame.pack(fill='x', pady=10)

        ttk.Button(button_frame, text="Зашифровать", command=self.encrypt_message,
                   bootstyle=SUCCESS).pack(side=LEFT, padx=5)
        ttk.Button(button_frame, text="Очистить", command=self.clear_fields,
                   bootstyle=WARNING).pack(side=LEFT, padx=5)

        result_frame = ttk.LabelFrame(self.encrypt_frame, text="Результаты", padding=10)
        result_frame.pack(fill='both', expand=True, padx=5, pady=5)

        ttk.Label(result_frame, text="Зашифрованный вектор:").pack(anchor='w')
        self.encrypted_result = ttk.Label(result_frame, text="", font=('Consolas', 10),
                                          relief='solid', padding=5)
        self.encrypted_result.pack(fill='x', pady=5)

        ttk.Label(result_frame, text="Расшифрованный вектор:").pack(anchor='w')
        self.decrypted_result = ttk.Label(result_frame, text="", font=('Consolas', 10),
                                          relief='solid', padding=5)
        self.decrypted_result.pack(fill='x', pady=5)

    def setup_about_tab(self):
        about_text = """GGH Cryptography Tool

Версия 1.0
Использует алгоритм GGH (Goldreich-Goldwasser-Halevi) 
для шифрования на основе решёток.

Инструкция:
1. Введите приватный базис (матрицу)
2. Введите вектор сообщения
3. Нажмите 'Зашифровать'

Пример матрицы:
7 0 0
0 5 0
0 0 3

Пример вектора:
3 -2 1
"""
        text = tk.Text(self.about_frame, wrap='word', height=15, padx=10, pady=10,
                       font=('TkDefaultFont', 10), relief='flat')
        text.insert('1.0', about_text)
        text.config(state='disabled')
        text.pack(fill='both', expand=True)

    def insert_sample_matrix(self):
        sample = """7 0 0
0 5 0
0 0 3"""
        self.matrix_text.delete('1.0', END)
        self.matrix_text.insert('1.0', sample)

    def insert_sample_vector(self):
        self.vector_entry.delete(0, END)
        self.vector_entry.insert(0, "3 -2 1")

    def clear_fields(self):
        self.matrix_text.delete('1.0', END)
        self.vector_entry.delete(0, END)
        self.encrypted_result.config(text="")
        self.decrypted_result.config(text="")

    def parse_matrix(self):
        try:
            text = self.matrix_text.get('1.0', END).strip()
            lines = [line for line in text.split('\n') if line.strip()]
            matrix = []
            for line in lines:
                row = [int(x) for x in line.split()]
                matrix.append(row)
            return np.array(matrix)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Некорректный формат матрицы:\n{e}")
            return None

    def parse_vector(self):
        try:
            text = self.vector_entry.get().strip()
            if not text:
                raise ValueError("Вектор не может быть пустым")
            return np.array([int(x) for x in text.split()])
        except Exception as e:
            messagebox.showerror("Ошибка", f"Некорректный формат вектора:\n{e}")
            return None

    def generate_public_key(self, n, pri_key):
        k = 0
        matrix = np.identity(n)
        while k < 5:
            A = np.random.randint(-5, 5, size=(n, n))
            if np.linalg.det(A) == 1:
                matrix = np.matmul(matrix, A)
                k += 1
        return np.matmul(matrix, pri_key)

    def encrypt_message(self):
        private_key = self.parse_matrix()
        if private_key is None:
            return

        message = self.parse_vector()
        if message is None:
            return

        if len(message) != private_key.shape[0]:
            messagebox.showerror("Ошибка",
                                 f"Размер вектора ({len(message)}) не соответствует размеру матрицы ({private_key.shape[0]})")
            return

        try:
            public_key = self.generate_public_key(private_key.shape[0], private_key)
            encrypted = np.matmul(message, public_key) + ERROR_VECTOR
            u = np.matmul(encrypted, np.linalg.inv(private_key))
            u = np.matmul(np.rint(u), private_key)
            decrypted = np.matmul(u, np.linalg.inv(public_key))
            self.encrypted_result.config(text=str(encrypted))
            self.decrypted_result.config(text=str(decrypted))

        except Exception as e:
            messagebox.showerror("Ошибка вычислений", str(e))


if __name__ == "__main__":
    root = ttk.Window(themename="darkly")
    app = GGHModernGUI(root)
    root.geometry("600x750")
    root.minsize(500, 400)
    root.mainloop()
