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
import json
import os
from GeneralBot.BotManager import BotManager

WINDOW_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "window.json")

# TODO 1: Select JSON files and pass to BotManager
# TODO 2: Make buttons/fields/menus that visualize the JSON paramaterse (see GeneralBot/configs)
# TODO 2.5: Edit the JSON "CHARACTER" field based on the selected character
# TODO 3: Make visualized JSON fields (or a subset) editable, and save to existing or new JSON in GeneralBot/configs
# TODO 4: Pretty up the UI
# TODO 5: Pretty up the code



def getSlippiPath():
    try:
        f = open(WINDOW_CONFIG_PATH, "r")
        c: dict = json.load(f)
        f.close()
        return c["SLP_PATH"]
    except:
        return None

def getJSONPath():
    try:
        f = open(WINDOW_CONFIG_PATH, "r")
        c: dict = json.load(f)
        f.close()
        return c["JSON_PATH"]
    except:
        return None

def main():
    # Initialize Window
    root = tk.Tk()
    root.geometry('1280x760')
    root.title("Slippi Stats")
    title = Label(root, text = "Build a Slippi Bot", font = ('Helvetica 48 bold')).pack(pady = 20)
    
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
    # TODO 1: Pass filePath of JSON to BotMan.run
    BotMan = BotManager()

    res = BotMan.run(getSlippiPath(),getJSONPath()) # <--- pass the SLIPPI path here and JSON path
    print("Game end!")
    print(res[0])
    print(res[1])
    

def browseFiles():
    filename = filedialog.askopenfilename(initialdir = "/",
                                          title = "Select a File",
                                          filetypes = (("Slippi Files",
                                                        "*.slp*"),
                                                       ("All files",
                                                        "*.*")))
    label_file_explorer.configure(text="File Opened: "+filename)

main()


