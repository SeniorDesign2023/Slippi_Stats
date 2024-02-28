### MAIN WINDOW ###Helvetica

# Using tkinter version 8.6
# Visit https://docs.python.org/3/library/tkinter.html for documentation

import tkinter as tk
import tkinter.ttk as ttk
from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageTk
import pathlib
from pathlib import Path

def main():
    root = tk.Tk()
    root.geometry('1280x760')
    root.title("Slippi Stats")
    title = Label(root, text = "Slippi Stats", font = ('Helvetica 20 bold')).pack(pady = 20)
    
    # Create a File Explorer label
    global label_file_explorer
    label_file_explorer = Label(root, 
                                text = "File Explorer using Tkinter",
                                width = 100, height = 4, 
                                fg = "blue")
    
    # Select Character
    characters = ["Mario", "Bowser", "Peach", "Yoshi", "Donkey Kong",
                  "Captain Falcon", "Fox", "Ness", "Ice Climbers",
                  "Kirby", "Samus", "Zelda", "Link", "Pikachu",
                  "Jigglypuff", "Dr. Mario", "Luigi", "Ganondorf",
                  "Falco", "Young Link", "Pichu", "Mewtwo",
                  "Mr. Game & Watch", "Marth", "Roy"]
    selectedCharacter = tk.StringVar()
    characterLabel = tk.Label(root, text="Select a character to train against")
    characterLabel.pack(pady=10)
    dropdown = tk.OptionMenu(root, selectedCharacter, *characters, command=characterImage(selectedCharacter))
    dropdown.pack()

    button_explore = Button(root, 
                            text = "Browse Files",
                            command = browseFiles)
    label_file_explorer.pack(pady=10)
    button_explore.pack(pady=10)
    quitButton = tk.Button(text="Quit", command=root.destroy)
    quitButton.pack(pady = 100)
    root.mainloop()

def characterImage(character):
    if character is not None:
        path = pathlib.Path(__file__).parent.resolve()
        path = path._str.replace("window", "") + "CharacterImages\\Mario.jpg"
        path = Path(path)
        characterImage = Image.open(path)
        test = ImageTk.PhotoImage(characterImage)
        label1 = tk.Label(image=test)
        label1.image = test
        # Position image
        label1.place(0, 0)
    else:
        path = pathlib.Path(__file__).parent.resolve()
        path = path._str.replace("window", "") + "CharacterImages\\" + character.get() + ".jpg"
        path = Path(path)
        characterImage = Image.open(path)
        test = ImageTk.PhotoImage(characterImage)
        label1 = tk.Label(image=test)
        label1.image = test
        # Position image
        label1.place(0, 0)

def browseFiles():
    filename = filedialog.askopenfilename(initialdir = "/",
                                          title = "Select a File",
                                          filetypes = (("Slippi Files",
                                                        "*.slp*"),
                                                       ("All files",
                                                        "*.*")))
    label_file_explorer.configure(text="File Opened: "+filename)
main()