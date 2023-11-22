import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from googletrans import Translator
import ply.yacc as yacc
import pyttsx3
from lexer import lexer

class SimpleInterpreterGUI:
    def __init__(self, master):
        self.master = master
        master.title("Simple Interpreter GUI")

        self.translator = Translator()
        self.current_language = "en"
        self.languages = {"en": "English", "es": "Spanish", "fr": "French"}

        self.language_var = tk.StringVar()
        self.language_var.set("en")

        self.language_label = ttk.Label(master, text=self.translate_text("Select a language:"))
        self.language_label.pack()

        self.language_selector = ttk.Combobox(master, values=list(self.languages.values()), state="readonly",
                                              textvariable=self.language_var)
        self.language_selector.current(0)
        self.language_selector.pack()
        self.language_selector.bind("<<ComboboxSelected>>", self.change_language)

        self.editor_label = tk.Label(master, text=self.translate_text("Enter your code to validate with the interpreter:"))
        self.editor_label.pack(pady=5)

        self.editor = scrolledtext.ScrolledText(master, width=40, height=10)
        self.editor.pack(pady=5)

        self.run_button = tk.Button(master, text=self.translate_text("Run"), command=self.run_code)
        self.run_button.pack(side=tk.LEFT, padx=5)

        self.validate_button = tk.Button(master, text=self.translate_text("Validate"), command=self.validate_code)
        self.validate_button.pack(side=tk.RIGHT, padx=5)

        self.help_button = tk.Button(master, text=self.translate_text("Help"), command=self.show_help)
        self.help_button.pack(side=tk.RIGHT, padx=5)

        self.example_button = tk.Button(master, text=self.translate_text("Show Examples"), command=self.show_examples)
        self.example_button.pack(side=tk.LEFT, padx=5)

        self.result_text = tk.Text(master, height=2, width=40)
        self.result_text.pack(pady=5)

        self.example_labels = []
        self.example_buttons = []
        self.examples_frame = tk.Frame(master)
        self.examples_frame.pack(pady=5)

        # Show the initial instruction
        self.show_result(self.translate_text("Enter your code to validate with the interpreter."))

        # Inicializar el motor de texto a voz
        self.engine = pyttsx3.init()

    def run_code(self):
        code = self.editor.get("1.0", tk.END)
        translated_code = self.translate_code(code)
        try:
            parser_result = parser.parse(translated_code, lexer=lexer)
            result_str = self.translate_text(f"Parser result: {parser_result}")
            self.show_result(result_str)
            self.speak(result_str)
        except Exception as e:
            error_str = self.translate_text(f"Error during parsing/execution: {e}")
            self.show_result(error_str)
            self.speak(error_str)

    def validate_code(self):
        code = self.editor.get("1.0", tk.END)
        translated_code = self.translate_code(code)
        try:
            parser.parse(translated_code, lexer=lexer)
            result_str = self.translate_text("The code is valid.")
            self.show_result(result_str)
            self.speak(result_str)
        except Exception as e:
            error_str = self.translate_text(f"Syntax error: {e}")
            self.show_result(error_str)
            self.speak(error_str)

    def translate_code(self, code):
        target_language = self.language_var.get()
        translation = self.translator.translate(code, dest=target_language)
        return translation.text

    def show_result(self, result):
        # Clear previous content before showing the new result
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, result)

    def show_help(self):
        help_window = tk.Toplevel(self.master)
        help_window.title(self.translate_text("Help"))

        help_text = """
        This is a simple interpreter GUI that allows you to enter and validate code snippets.
        
        Features:
        - Enter code in the editor and click "Run" or "Validate."
        - The result will be displayed in the result area.
        - Click "Help" to view examples and usage instructions.
        
        Examples:
        - Basic arithmetic: x = 10 + y * 5
        - Conditionals: if x > 0: positive = True else: positive = False
        - Loops: for i in range(5): print(i)
        - Functions: def multiply(a, b): return a * b
        
        Enjoy coding!
        """

        help_label = tk.Label(help_window, text=self.translate_text(help_text), justify=tk.LEFT)
        help_label.pack(padx=10, pady=10)

    def show_examples(self):
        examples = [
            "x = 10 + y * 5",
            "result = 2 * (3 + 4)",
            "a = 5 * (10 - b)",
            "c = 8 / (2 * d)",
            "x = 10 * y + z",
            "invalid = 3 + * 5",
            "",
            "# Conditional Example",
            "if x > 0:",
            "    positive = True",
            "else:",
            "    positive = False",
            "",
            "# Loop Example",
            "for i in range(5):",
            "    print(i)",
            "",
            "# Function Example",
            "def multiply(a, b):",
            "    return a * b",
            "",
            "result = multiply(3, 4)",
        ]

        # Clear the frame of previous labels and buttons
        for label, button in zip(self.example_labels, self.example_buttons):
            label.destroy()
            button.destroy()
        self.example_labels = []
        self.example_buttons = []

        # Show examples in the frame and create buttons
        for i, example in enumerate(examples):
            label = tk.Label(self.examples_frame, text=f"Example {i + 1}: {example}")
            label.grid(row=i, column=0, sticky=tk.W, padx=5)
            self.example_labels.append(label)
            button = tk.Button(self.examples_frame, text=f"Use Example {i + 1}", command=lambda ex=example: self.use_example(ex))
            button.grid(row=i, column=1, padx=5)
            self.example_buttons.append(button)

    def use_example(self, example):
        # Clear the editor before adding the example
        self.editor.delete("1.0", tk.END)
        # Add the example to the editor
        self.editor.insert(tk.END, example)
        # Clear the previous result
        self.show_result("")

    def change_language(self, event):
        new_language = next(key for key, value in self.languages.items() if value == self.language_selector.get())
        print("Language changed to:", new_language)
        
        # Cambia el idioma de la instrucción inicial
        initial_instruction = self.translate_text("Enter your code to validate with the interpreter.")
        self.show_result(initial_instruction)

        # Cambia el idioma de todos los elementos de la interfaz
        self.master.title(f"Simple Interpreter GUI - {self.languages[new_language]}")
        self.language_label.config(text=self.translate_text("Select a language:"))
        self.editor_label.config(text=self.translate_text("Enter your code to validate with the interpreter:"))
        self.run_button.config(text=self.translate_text("Run"))
        self.validate_button.config(text=self.translate_text("Validate"))
        self.help_button.config(text=self.translate_text("Help"))
        self.example_button.config(text=self.translate_text("Show Examples"))

    def translate_text(self, text):
        target_language = self.language_var.get()
        translation = self.translator.translate(text, dest=target_language)
        return translation.text

    def speak(self, text):
        self.engine.say(text)
        self.master.after(10, self.engine.runAndWait)

def main():
    root = tk.Tk()
    app = SimpleInterpreterGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
