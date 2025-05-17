import sqlite3
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from ttkbootstrap import Style
from PIL import Image, ImageTk
from tkinter import PhotoImage
import random 
from PIL import Image, ImageTk 



def create_tables(conn):
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS flashcard_sets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS flashcards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            set_id INTEGER NOT NULL,
            word TEXT NOT NULL,
            definition TEXT NOT NULL,
            FOREIGN KEY (set_id) REFERENCES flashcard_sets(id)
        )
    ''')

# Add flashcard 
def add_set(conn, name):
    cursor = conn.cursor()

    
    cursor.execute('''
        INSERT INTO flashcard_sets (name)
        VALUES (?)
    ''', (name,))

    set_id = cursor.lastrowid
    conn.commit()

    return set_id


def add_card(conn, set_id, word, definition):
    cursor = conn.cursor()

    
    cursor.execute('''
        INSERT INTO flashcards (set_id, word, definition)
        VALUES (?, ?, ?)
    ''', (set_id, word, definition))

    
    card_id = cursor.lastrowid
    conn.commit()

    return card_id

# Retrieve flashcards from database
def get_sets(conn):
    cursor = conn.cursor()

    
    cursor.execute('''
        SELECT id, name FROM flashcard_sets
    ''')

    rows = cursor.fetchall()
    sets = {row[1]: row[0] for row in rows} 

    return sets


def get_cards(conn, set_id):
    cursor = conn.cursor()

    cursor.execute('''
        SELECT word, definition FROM flashcards
        WHERE set_id = ?
    ''', (set_id,))

    rows = cursor.fetchall()
    cards = [(row[0], row[1]) for row in rows] 

    return cards

# Delete a flashcard set
def delete_set(conn, set_id):
    cursor = conn.cursor()

   
    cursor.execute('''
        DELETE FROM flashcard_sets
        WHERE id = ?
    ''', (set_id,))

    conn.commit()
    sets_combobox.set('')
    clear_flashcard_display()
    populate_sets_combobox()

    
    global current_cards, card_index
    current_cards = []
    card_index = 0

# Create flashcards
def create_set():
    set_name = set_name_var.get()
    if set_name:
        if set_name not in get_sets(conn):
            set_id = add_set(conn, set_name)
            populate_sets_combobox()
            set_name_var.set('')

            # Clear the input fields
            set_name_var.set('')
            word_var.set('')
            definition_var.set('')

def add_word():
    set_name = set_name_var.get()
    word = word_var.get()
    definition = definition_var.get()

    if set_name and word and definition:
        if set_name not in get_sets(conn):
            set_id = add_set(conn, set_name)
        else:
            set_id = get_sets(conn)[set_name]

        add_card(conn, set_id, word, definition)

        word_var.set('')
        definition_var.set('')

        populate_sets_combobox()

def populate_sets_combobox():
    sets_combobox['values'] = tuple(get_sets(conn).keys())

# Delete flashcards
def delete_selected_set():
    set_name = sets_combobox.get()

    if set_name:
        result = messagebox.askyesno(
            'Confirmation', f'Are you sure you want to delete the "{set_name}" set?'
        )

        if result == tk.YES:
            set_id = get_sets(conn)[set_name]
            delete_set(conn, set_id)
            populate_sets_combobox()
            clear_flashcard_display()

def select_set():
    set_name = sets_combobox.get()

    if set_name:
        set_id = get_sets(conn)[set_name]
        cards = get_cards(conn, set_id)

        if cards:
            display_flashcards(cards)
            
            
        else:
            word_label.config(text="No cards in this set")
            definition_label.config(text='')
    else:
        
        global current_cards, card_index
        current_cards = []
        card_index = 0
        clear_flashcard_display()

def display_flashcards(cards):
    global card_index
    global current_cards

    card_index = 0
    current_cards = cards

   
    if not cards:
        clear_flashcard_display()
    else:
        show_card()

    show_card()

def clear_flashcard_display():
    word_label.config(text='')
    definition_label.config(text='')

#  Display the current flashcards word
def show_card():
    global card_index
    global current_cards

    if current_cards:
        if 0 <= card_index < len(current_cards):
            word, _ = current_cards[card_index]
            word_label.config(text=word)
            definition_label.config(text='') # Hide definition when showing word
        else:
            clear_flashcard_display()
    else:
        clear_flashcard_display()

# 'Flip' the card
def flip_card():
    global card_index
    global current_cards

    if current_cards:
        if 0 <= card_index < len(current_cards):
            _, definition = current_cards[card_index]
            definition_label.config(text=definition)
        else:
            definition_label.config(text='')


# Move to the next card
def next_card():
    global card_index
    global current_cards

    if current_cards:
        card_index = min(card_index + 1, len(current_cards) -1)
        show_card()

# Move to the previous card
def prev_card():
    global card_index
    global current_cards

    if current_cards:
        card_index = max(card_index - 1, 0)
        show_card()

# Shuffle flashcards
def shuffle_cards():
    global current_cards, card_index
    if current_cards:
        random.shuffle(current_cards)
        card_index = 0 # Reset to the first card after shuffling
        show_card()
        messagebox.showinfo("Shuffle", "Cards have been shuffled!")
    else:
        messagebox.showinfo("Shuffle", "No cards to shuffle in the current set.")


if __name__ == '__main__':
    # Connect to the SQLite database and create tables
    conn = sqlite3.connect('flashcards.db')
    create_tables(conn)

    # Create the main GUI window
    root = tk.Tk()
    
    try:
        icon = PhotoImage(file='D:\Downloads\CC15Flashcards\FlashMe.png')
        root.iconphoto(True, icon)
    except tk.TclError:
        print("Warning: Icon file not found at D:\Downloads\CC15Flashcards\FlashMe.png")

    root.title('FlashMe!')
    window_width = 500
    window_height = 550

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    x = int((screen_width / 2) - (window_width / 2))
    y = int((screen_height / 2) - (window_height / 2))

    root.geometry(f'{window_width}x{window_height}+{x}+{y}')

    root.resizable(False, False)

    style = Style(theme='darkly')
    style.configure('TLabel', font=('TkHeadingFont', 18))
    style.configure('TButton', font=('TkDefaultFont', 16))

    set_name_var = tk.StringVar()
    word_var = tk.StringVar()
    definition_var = tk.StringVar()

    notebook = ttk.Notebook(root)
    notebook.pack(fill='both', expand=True, padx=10, pady=10) 

    create_set_frame = ttk.Frame(notebook, padding="10") 
    notebook.add(create_set_frame, text='Create Set')

    ttk.Label(create_set_frame, text='Set Name').pack(padx=5, pady=5)
    ttk.Entry(create_set_frame, textvariable=set_name_var, width=30).pack(padx=5, pady=5)

    ttk.Label(create_set_frame, text='Question').pack(padx=5, pady=5)
    ttk.Entry(create_set_frame, textvariable=word_var, width=30).pack(padx=5, pady=5)

    ttk.Label(create_set_frame, text='Definition').pack(padx=5, pady=5)
    ttk.Entry(create_set_frame, textvariable=definition_var, width=30).pack(padx=5, pady=5)

    ttk.Button(create_set_frame, text='Add Question', command=add_word, bootstyle='light-outline').pack(padx=5, pady=10)

    ttk.Button(create_set_frame, text='Save Set', command=create_set, bootstyle='light-outline').pack(padx=5, pady=10)

    select_set_frame = ttk.Frame(notebook, padding="10") 
    notebook.add(select_set_frame, text="Select Set")

    sets_combobox = ttk.Combobox(select_set_frame, state='readonly', width=27, bootstyle='light') 
    sets_combobox.pack(padx=5, pady=20) 

    ttk.Button(select_set_frame, text='Select Set', command=select_set, bootstyle='light-outline').pack(padx=5, pady=5)

    ttk.Button(select_set_frame, text='Delete Set', command=delete_selected_set, bootstyle='light-outline').pack(padx=5, pady=5)

    flashcards_frame = ttk.Frame(notebook, padding="10") 
    notebook.add(flashcards_frame, text='Study Mode')

    card_index = 0
    current_cards = [] 

    card_box_frame = ttk.Frame(flashcards_frame, relief='raised', borderwidth=3, padding="40") 
    card_box_frame.pack(pady=20, fill='both', expand=True) 

    word_label = ttk.Label(card_box_frame, text='', font=('TkHeadingFont', 24), wraplength=400, anchor='center', justify='center') 
    word_label.pack(padx=10, pady=10)

    definition_label = ttk.Label(card_box_frame, text='', wraplength=400, anchor='center', justify='center') 
    definition_label.pack(padx=10, pady=10)

    control_frame = ttk.Frame(flashcards_frame)
    control_frame.pack(pady=10)

    ttk.Button(control_frame, text='Flip', command=flip_card, bootstyle='light-outline').pack(side='left', padx=5)

    ttk.Button(control_frame, text='Previous', command=prev_card, bootstyle='light-outline').pack(side='left', padx=5)

    ttk.Button(control_frame, text='Next', command=next_card, bootstyle='light-outline').pack(side='left', padx=5)

    ttk.Button(control_frame, text='Shuffle', command=shuffle_cards, bootstyle='light-outline').pack(side='left', padx=5)

    populate_sets_combobox()

    


    # Error handling for the footer image loading
    try:
        
        original_image = Image.open('D:\Downloads\CC15Flashcards\FlashMe2.png')
        resized_image = original_image.resize((74, 75))  
        footer_image = ImageTk.PhotoImage(resized_image)

        footer_label = ttk.Label(root, image=footer_image)
        footer_label.image = footer_image  
        footer_label.pack(side='bottom', pady=10)
        
    except FileNotFoundError:
        print("Warning: Footer image file not found at D:\Downloads\CC15Flashcards\FlashMe2.png")
    except ImportError:
        print("Warning: Pillow library not found. Install it with 'pip install Pillow' to display the footer image.")

    root.mainloop()
