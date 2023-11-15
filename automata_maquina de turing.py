import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from googletrans import Translator  # Importa el traductor de Google
import threading
import time

class TuringMachine:
    def __init__(self):
        self.states = {'q0', 'q1', 'q2'}
        self.transitions = {
            ('q0', 'a'): ('q0', 'a', 'R'),
            ('q0', 'b'): ('q0', 'a', 'R'),
            ('q0', '_'): ('q1', '_', 'L'),
            ('q1', 'a'): ('q1', 'a', 'L'),
            ('q1', '_'): ('q2', '_', 'R'),
        }
        self.accept_state = 'q2'
        self.current_state = 'q0'
        self.tape = ['_']
        self.head_position = 0

    def initialize_with_input(self, input_string):
        self.tape = ['_'] + list(input_string) + ['_']
        self.current_state = 'q0'
        self.head_position = 1

    def step(self):
        current_symbol = self.tape[self.head_position]
        if (self.current_state, current_symbol) not in self.transitions:
            self.current_state = self.reject_state
            return

        new_state, write_symbol, move_direction = self.transitions[(self.current_state, current_symbol)]
        self.tape[self.head_position] = write_symbol

        if move_direction == 'R':
            self.head_position += 1
        elif move_direction == 'L':
            self.head_position -= 1

        self.current_state = new_state

class TuringMachineGUI(tk.Tk):
    def __init__(self, turing_machine):
        super().__init__()

        self.title("Máquina de Turing")
        self.geometry("800x600")

        self.turing_machine = turing_machine

        # Cuadro de lista (Combobox) para el idioma
        self.language_label_text = tk.StringVar()
        self.language_label_text.set("Seleccione el idioma de la expresión:")
        self.language_label = tk.Label(self, textvariable=self.language_label_text)
        self.language_label.pack()

        self.language_combobox = ttk.Combobox(self, values=['es', 'en', 'fr', 'de', 'ja', 'ko'])
        self.language_combobox.set('es')  # Establecer el valor predeterminado a español
        self.language_combobox.pack()

        # Etiqueta e entrada para la expresión
        self.input_label_text = tk.StringVar()
        self.input_label_text.set("Ingrese una expresión compuesta por 'a' y 'b' para convertir todos los símbolos en 'a'")
        self.input_label = tk.Label(self, textvariable=self.input_label_text)
        self.input_label.pack()

        self.input_entry = tk.Entry(self)
        self.input_entry.pack()

        # Etiqueta para el resultado
        self.result_label_text = tk.StringVar()
        self.result_label_text.set("")
        self.result_label = tk.Label(self, textvariable=self.result_label_text)
        self.result_label.pack()

        # Botones organizados horizontalmente
        self.button_frame = tk.Frame(self)
        self.button_frame.pack()

        self.enter_button = tk.Button(self.button_frame, text="Ingresar", command=self.enter_word)
        self.enter_button.pack(side=tk.LEFT)

        self.step_button = tk.Button(self.button_frame, text="Paso", command=self.step_tape)
        self.step_button.pack(side=tk.LEFT)

        self.run_button = tk.Button(self.button_frame, text="Ejecutar", command=self.run)
        self.run_button.pack(side=tk.LEFT)

        self.pause_button = tk.Button(self.button_frame, text="Pausar", command=self.pause)
        self.pause_button.pack(side=tk.LEFT)

        # Escala para la velocidad
        self.speed_scale = tk.Scale(self, label="Velocidad", from_=1, to=10, orient=tk.HORIZONTAL)
        self.speed_scale.set(5)
        self.speed_scale.pack()

        # Etiqueta para el símbolo evaluado
        self.evaluated_symbol = tk.Label(self, text="")

        # Crear el scrollbar horizontal
        self.horizontal_scrollbar = ttk.Scrollbar(self, orient=tk.HORIZONTAL, command=self.scroll_canvas)
        self.horizontal_scrollbar.pack(fill=tk.X, side=tk.BOTTOM)

        # Marco para el lienzo
        self.canvas_frame = tk.Frame(self)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)

        # Lienzo
        self.canvas = tk.Canvas(self.canvas_frame, width=800, height=600, xscrollcommand=self.horizontal_scrollbar.set)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Configuración de eventos del lienzo
        self.canvas.bind("<Configure>", self.configure_canvas)
        self.visualize_turing_machine()
        self.running = False
        self.turing_thread = None
        self.paused = False  # Variable de control para pausar el hilo
        
        self.translator = Translator()

        # Actualizar idioma al inicio
        self.update_language()

    def configure_canvas(self, event):
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def scroll_canvas(self, *args):
        self.canvas.xview(*args)

    def translate_text(self, text, source='auto', target='en'):
        translation = self.translator.translate(text, src=source, dest=target)
        return translation.text

    def update_language(self):
        language = self.language_combobox.get()
        self.language_label_text.set(self.translate_text("Seleccione el idioma de la expresión:", source='en', target=language))
        self.input_label_text.set(self.translate_text("Ingrese una expresión compuesta por 'a' y 'b' para convertir todos los símbolos en 'a'", source='en', target=language))
        self.result_label_text.set("")

    def enter_word(self):
        language = self.language_combobox.get()
        input_word = self.input_entry.get()
        translated_word = self.translate_text(input_word, source=language, target='en')
        self.turing_machine.initialize_with_input(translated_word)
        self.visualize_turing_machine()
        self.result_label_text.set(self.translate_text("Se ha ingresado una nueva palabra.", source='en', target=language))

    def step_tape(self):
        if self.turing_machine.current_state != self.turing_machine.accept_state:
            self.move_tape(10, 3)  # Mover la cinta en 3 pasos de 10 unidades
            self.turing_machine.step()
            self.move_tape(-10, 3)  # Restaurar la posición original en 3 pasos de 10 unidades
            self.visualize_turing_machine()
            self.result_label_text.set(self.translate_text("Se ha saltado un símbolo", source='en', target=language))

    def move_tape(self, delta, steps):
        for _ in range(steps):
            self.turing_machine.head_position += delta
            self.visualize_turing_machine()
            self.update()
            time.sleep(5 / self.speed_scale.get())

    def run(self):
        self.paused = False
        if self.turing_machine.current_state != self.turing_machine.accept_state:
            self.turing_thread = threading.Thread(target=self.turing_thread_function)
            self.turing_thread.start()
            self.result_label_text.set("")

    def pause(self):
        self.paused = True
        self.result_label_text.set(self.translate_text("Pausado", source='en', target=language))

    def resume(self):
        self.paused = False

    def turing_thread_function(self):
        while not self.paused and self.turing_machine.current_state != self.turing_machine.accept_state:
            self.turing_machine.step()
            self.after(10, self.update_visualization)
            time.sleep(5 / self.speed_scale.get())

            if self.turing_machine.current_state == self.turing_machine.accept_state:
                self.result_label_text.set(self.translate_text("Se ha cambiado toda la palabra.", source='en', target=language))

    def update_visualization(self):
        self.visualize_turing_machine()

    def visualize_turing_machine(self):
        self.clear_canvas()
        self.draw_states()
        self.draw_transitions()
        self.draw_tape()

    def clear_canvas(self):
        self.canvas.delete("all")

    def draw_states(self):
        for state in self.turing_machine.states:
            x, y = self.get_node_coordinates(state)
            fill_color = "lightgreen" if state == self.turing_machine.current_state else "lightblue"
            border_width = 3 if state == self.turing_machine.accept_state else 1
            self.draw_node(x, y, fill_color, state, border_width)

    def draw_node(self, x, y, fill_color, state, border_width):
        self.canvas.create_oval(x - 20, y - 20, x + 20, y + 20, fill=fill_color, width=border_width)
        self.canvas.create_text(x, y, text=state)

    def draw_transitions(self):
        for transition, destination in self.turing_machine.transitions.items():
            current_state, read_symbol = transition
            new_state, write_symbol, move_direction = destination
            current_symbol = self.turing_machine.tape[self.turing_machine.head_position]
            color = "red" if current_state == self.turing_machine.current_state and read_symbol == current_symbol else "black"
            transition_label = f"{read_symbol}, {write_symbol}, {move_direction}"

            self.draw_transition(current_state, new_state, transition_label, color)

    def draw_tape(self):
        tape_text = "".join(self.turing_machine.tape)
        tape_length = len(tape_text)
        square_size = 40
        empty_squares = 20

        head_position = self.turing_machine.head_position
        start_x = 400 - head_position * square_size

        for i in range(empty_squares):
            x = start_x - (empty_squares - i) * square_size
            y = 100
            self.draw_square(x, y, square_size, '')

        for i, char in enumerate(tape_text):
            x = start_x + i * square_size
            y = 100
            self.draw_square(x, y, square_size, char)

        for i in range(empty_squares):
            x = start_x + (tape_length + i) * square_size
            y = 100
            self.draw_square(x, y, square_size, '')

        self.draw_head_fixed_position()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))
        self.horizontal_scrollbar.configure(command=self.scroll_canvas)

    def draw_square(self, x, y, size, char):
        self.canvas.create_rectangle(x, y, x + size, y + size, outline='black')
        self.canvas.create_text(x + size // 2, y + size // 2, text=char, font=('Helvetica', 12), anchor=tk.CENTER)

    def draw_head_fixed_position(self):
        x = 420
        y = 100
        self.canvas.create_polygon(x, y, x - 10, y - 20, x + 10, y - 20, fill='red')

    def draw_transition(self, current_state, new_state, label, color):
        x1, y1 = self.get_node_coordinates(current_state)
        x2, y2 = self.get_node_coordinates(new_state)

        if current_state == new_state:
            self.canvas.create_arc(x1 - 30, y1 - 30, x1 + 30, y1 + 30, start=180, extent=-180, style=tk.ARC)
            self.canvas.create_line(x1 - 40, y1, x1 - 20, y1, arrow=tk.LAST)
        else:
            self.canvas.create_line(x1 + 20, y1, x2 - 20, y2, arrow=tk.LAST)

        label_x, label_y = self.calculate_label_position(x1, y1, x2, y2)
        self.canvas.create_text(label_x, label_y, text=label, fill=color)

    def calculate_label_position(self, x1, y1, x2, y2):
        label_x = (x1 + x2) / 2
        label_y = y1 - 30

        overlapping_labels = self.canvas.find_overlapping(label_x - 10, label_y - 10, label_x + 10, label_y + 10)

        while overlapping_labels:
            label_y -= 10
            overlapping_labels = self.canvas.find_overlapping(label_x - 10, label_y - 10, label_x + 10, label_y + 10)

        return label_x, label_y

    def get_node_coordinates(self, state):
        state_number = int(state[1:])
        x = 100 + state_number * 150
        y = 300
        return x, y

if __name__ == "__main__":
    turing_machine = TuringMachine()
    app = TuringMachineGUI(turing_machine)
    app.mainloop()
