## DO NOT USE THIS WINDOW, USE ONE IN AI FOLDER















### MAIN WINDOW ###

# Using tkinter version 8.6
# Visit https://docs.python.org/3/library/tkinter.html for documentation
# Using pack as the LayoutManager

import tkinter as tk
import tkinter.ttk as ttk
from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageTk
import pathlib
from pathlib import Path
import os
from GeneralBot.BotManager import BotManager

def main():
    # Initialize Window
    root = tk.Tk()
    root.geometry('1280x760')
    root.title("Slippi Stats")
    title = Label(root, text = "Build a Slippi Bot", font = ('Helvetica 20 bold')).pack(pady = 20)
    
    # Create a File Explorer label
    global label_file_explorer
    label_file_explorer = Label(root, 
                                text = "",
                                width = 100, height = 4)
    
    # Select Character
    characters = ["Mario", "Bowser", "Peach", "Yoshi", "Donkey Kong",
                  "Captain Falcon", "Fox", "Ness", "Ice Climbers",
                  "Kirby", "Samus", "Zelda", "Link", "Pikachu",
                  "Jigglypuff", "Dr. Mario", "Luigi", "Ganondorf",
                  "Falco", "Young Link", "Pichu", "Mewtwo",
                  "Mr. Game & Watch", "Marth", "Roy"]
    global selectedCharacter
    global label1
    label1 = Label(root, image = "")
    global imageAppear
    imageAppear = True
    selectedCharacter = tk.StringVar(master=root) #Always pass the 'master' keyword argument
    selectedCharacter.set("Select a character")
    selectedCharacter.trace_add('write', characterImage)
    characterLabel = tk.Label(root, text="Select a character to train against")
    characterLabel.pack(pady=5)
    dropdown = tk.OptionMenu(root, selectedCharacter, *characters)
    dropdown.pack()
    
    # File Explorer
    button_explore = Button(root, 
                            text = "Browse Files",
                            command = browseFiles)
    label_file_explorer.pack(pady=5)
    button_explore.pack(pady=5)

    # Launch Slippi
    launchButton = Button(root,
                          text = "Launch Slippi",
                          command=runSlippi)
    launchButton.pack(pady=5)

    # Quit Button
    quitButton = tk.Button(text="Quit", command=root.destroy)
    quitButton.pack(pady = 100)
    root.mainloop()

#Character Options
    #character
    #aggresion = 1-9
    #playstyle = aerial grounded mixed
    #waveshine = boolean
    #multishine = boolean

def characterImage(*args):
    global imageAppear
    global label1
    if imageAppear == True:
        clearImage()
    path = pathlib.Path(__file__).parent.resolve()
    path = path._str + "\\CharacterImages\\{}.jpg".format(selectedCharacter.get())
    # path = path.replace("\\\\","\\")
    path = Path(path)
    characterImage = Image.open(path)
    test = ImageTk.PhotoImage(characterImage)
    label1 = tk.Label(image=test)
    label1.image = test
    # Position image
    label1.pack(side=RIGHT)
    imageAppear = True

def clearImage():
    label1.config(image = "")

def runSlippi():
    os.system("./.venv/Scripts/Activate.bat")
    os.system("python3 example.py -e \"C:\\Users\\zcrim\\AppData\\Roaming\\Slippi Launcher\\netplay\"")

def browseFiles():
    filename = filedialog.askopenfilename(initialdir = "/",
                                          title = "Select a File",
                                          filetypes = (("Slippi Files",
                                                        "*.slp*"),
                                                       ("All files",
                                                        "*.*")))
    label_file_explorer.configure(text="File Opened: "+filename)

main()