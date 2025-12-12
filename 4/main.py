import itertools
import tkinter as tk
from tkinter import ttk, messagebox


class LogicTableApp:
    def __init__(self, root):
        self.replacements = {
            ' И ': ' and ',
            ' ИЛИ ': ' or ',
            ' НЕ ': ' not ',
            '¬': 'not ',
            '∧': ' and ',
            '∨': ' or ',
            '→': ' <= ',
            '↔': ' == ',
            '⊕': ' != ',
        }
        self.root = root
        self.root.title("Таблиц истинности")
        self.root.geometry("800x600")

        input_frame = ttk.Frame(root, padding="10")
        input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        ttk.Label(input_frame, text="Логическое выражение:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.expression_entry = ttk.Entry(input_frame, width=50)
        self.expression_entry.grid(row=0, column=1, pady=5, padx=5)
        self.expression_entry.insert(0, "(A and B) or (not C)")

        ttk.Label(input_frame, text="Переменные (через запятую):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.vars_entry = ttk.Entry(input_frame, width=50)
        self.vars_entry.grid(row=1, column=1, pady=5, padx=5)
        self.vars_entry.insert(0, "A, B, C")

        ttk.Button(input_frame, text="Построить таблицу истинности",
                   command=self.build_table).grid(row=2, column=0, columnspan=2, pady=10)

        table_frame = ttk.Frame(root, padding="10")
        table_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.tree = ttk.Treeview(table_frame, height=15)
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        vsb.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.tree.configure(yscrollcommand=vsb.set)

        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        hsb.grid(row=1, column=0, sticky=(tk.W, tk.E))
        self.tree.configure(xscrollcommand=hsb.set)

        result_frame = ttk.Frame(root, padding="10")
        result_frame.grid(row=2, column=0, sticky=(tk.W, tk.E))

        self.result_label = ttk.Label(result_frame, text="", font=("Arial", 10))
        self.result_label.grid(row=0, column=0)

        root.columnconfigure(0, weight=1)
        root.rowconfigure(1, weight=1)
        table_frame.columnconfigure(0, weight=1)
        table_frame.rowconfigure(0, weight=1)

    def build_table(self):
        try:
            expression = self.expression_entry.get().strip()
            vars_str = self.vars_entry.get().strip()

            if not expression or not vars_str:
                messagebox.showerror("Ошибка", "Заполните все поля")
                return

            variables = [v.strip() for v in vars_str.split(',')]
            py_expression = self.convert_to_python(expression)
            self.tree.delete(*self.tree.get_children())

            columns = variables + ['Результат']
            self.tree['columns'] = columns
            self.tree.heading('#0', text='№')
            self.tree.column('#0', width=40)

            for col in columns:
                self.tree.heading(col, text=col)
                self.tree.column(col, width=80, anchor='center')

            row_num = 1

            for values in itertools.product([0, 1], repeat=len(variables)):
                var_dict = dict(zip(variables, values))
                py_expression_new = py_expression
                for key, value in var_dict.items():
                    py_expression_new = py_expression_new.replace(key, str(value))
                try:
                    result = int(bool(eval(py_expression_new)))
                except Exception as e:
                    messagebox.showerror("Ошибка", "Ошибка в логическом выражении")
                    return

                row_values = list(values) + [result]
                self.tree.insert('', 'end', text=str(row_num), values=row_values)
                row_num += 1

        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")

    def convert_to_python(self, expression):

        result = expression
        for old, new in self.replacements.items():
            result = expression.replace(old, new)

        if '<=' in expression and 'not' not in result:
            parts = result.split('<=')
            if len(parts) == 2:
                result = f"(not ({parts[0].strip()}) or ({parts[1].strip()}))"

        return result


def main():
    root = tk.Tk()
    app = LogicTableApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
