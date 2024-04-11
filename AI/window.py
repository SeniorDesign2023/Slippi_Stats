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
import customtkinter



customtkinter.set_appearance_mode("dark")  # Modes: system (default), light, dark
customtkinter.set_default_color_theme("green")  # Themes: blue (default), dark-blue, green

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
        fullpath = os.path.join(os.path.dirname(__file__),c["JSON_PATH"])# This path always is relative, we don't need
        return fullpath                                                  # to store the whole path. Just Slippi.
    except:
        return None

def main():
    # Initialize Window
    root = customtkinter.CTk()
    
   
    root.geometry('1280x500')
    root.title("Slippi Stats")
    title = customtkinter.CTkLabel(root, text = "Build a Slippi Bot",font= ("Helvetica bold", 48)).grid(row=0, column=0,padx=20,pady=20,sticky="ew", columnspan=2)
    #title = Label(root, text = "Build a Slippi Bot", font = ('Helvetica 48 bold')).pack(pady = 20)
    
    # Column weights
    # Keeps each of the columns from automatically collapsing,
    # can do the same thing for rows if needed
    root.grid_columnconfigure((0,1,2), weight=1)

    # Frames for the individual columns
    root.slippiFrame = customtkinter.CTkFrame(root)
    root.slippiFrame.grid(row=1,column=0,padx=10,pady=(10,0),sticky="nsw")

    root.characterFrame = customtkinter.CTkFrame(root)
    root.characterFrame.grid(row=1,column=1,padx=10,pady=(10,0),sticky="nsw")

    # Create a File Explorer label
    global label_file_explorer
    label_file_explorer = customtkinter.CTkLabel(root, 
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
    label1 = Label(root.slippiFrame, image = "")
    global imageAppear
    imageAppear = True
    selectedCharacter = customtkinter.StringVar(master=root) #Always pass the 'master' keyword argument
    selectedCharacter.set("Select a character")
    selectedCharacter.trace_add('write', characterImage)
    # dropdown = tk.OptionMenu(root, selectedCharacter, *characters)
    # dropdown.pack()
    dropdown2 = customtkinter.CTkOptionMenu(root.slippiFrame,
                                            variable=selectedCharacter,
                                            values= characters)
    dropdown2.grid(row=1,column=0,padx=20,pady=0,sticky="ew")
    # File Explorer
    button_explore = customtkinter.CTkButton(root.slippiFrame, 
                            text = "Browse Files",
                            command = browseFiles)
    label_file_explorer.grid(row=2,column=0,padx=20,pady=(0,20),sticky="ew")
    button_explore.grid(row=3,column=0,padx=20,pady=20,sticky="ew")

    # Launch Slippi
    launchButton = customtkinter.CTkButton(root.slippiFrame,
                          text = "Launch Slippi",
                          command=runSlippi)
    launchButton.grid(row=4,column=0,padx=20,pady=20,sticky="ew")

    # Quit Button
    quitButton = customtkinter.CTkButton(root.slippiFrame,text="Quit", command=root.destroy)
    quitButton.grid(row=5,column=0,padx=20,pady=20,sticky="ew")
    
    # START OF COLUMN 2

    # Column 2 Label
    columnTwoLabel = customtkinter.CTkLabel(root.characterFrame,
                                            text="Character Options",
                                            corner_radius=10)
    columnTwoLabel.grid(row=1,column=1,padx=20,pady=(0,10),sticky="ew")

    # Attack Style Dropdown
    attackLabel = customtkinter.CTkLabel(root.characterFrame,
                                         text="Attack Style",
                                         width=100,
                                         height=4)
    attackLabel.grid(row=2,column=1,padx=20,pady=(0,10),sticky="ew")
    attackStyle = customtkinter.StringVar(master=root)
    attackStyle.set("Select bots attack style")
    attackStyleDropdown = customtkinter.CTkOptionMenu(root.characterFrame,
                                            variable=attackStyle,
                                            values= ["Aerial", "Mixed", "Ground"])
    attackStyleDropdown.grid(row=3,column=1,padx=0,pady=(0,10),sticky="ew")
    
    # Playstyle Dropdown
    playstyleLabel = customtkinter.CTkLabel(root.characterFrame,
                                         text="Playstyle",
                                         width=100,
                                         height=4)
    playstyleLabel.grid(row=4,column=1,padx=20,pady=(0,10),sticky="ew")
    playstyleStyle = customtkinter.StringVar(master=root)
    playstyleStyle.set("Select bots playstyle")
    playstyleStyleDropdown = customtkinter.CTkOptionMenu(root.characterFrame,
                                            variable=playstyleStyle,
                                            values= ["Aggressive", "Neutral", "Passive"])
    playstyleStyleDropdown.grid(row=5,column=1,padx=0,pady=(0,10),sticky="ew")

    # Edgeguard Dropdown
    edgeguardLabel = customtkinter.CTkLabel(root.characterFrame,
                                         text="Edgeguard",
                                         width=100,
                                         height=4)
    edgeguardLabel.grid(row=6,column=1,padx=20,pady=(0,10),sticky="ew")
    edgeguardStyle = customtkinter.StringVar(master=root)
    edgeguardStyle.set("Select bots edgeguard style")
    edgeguardStyleDropdown = customtkinter.CTkOptionMenu(root.characterFrame,
                                            variable=edgeguardStyle,
                                            values= ["High", "Medium", "Low"])
    edgeguardStyleDropdown.grid(row=7,column=1,padx=0,pady=(0,10),sticky="ew")

    # Frame Delay Slider
    frameDelayLabel = customtkinter.CTkLabel(root.characterFrame,
                                         text="Frame Delay",
                                         width=100,
                                         height=4)
    frameDelayLabel.grid(row=8,column=1,padx=20,pady=(0,10),sticky="ew")
    frameDelaySlider = customtkinter.CTkSlider(root.characterFrame, from_=0, to=30, number_of_steps=30)
    frameDelaySlider.grid(row=9,column=1)

    # L Cancel Slider
    LCancelLabel = customtkinter.CTkLabel(root.characterFrame,
                                         text="L Cancel Rate",
                                         width=100,
                                         height=4)
    LCancelLabel.grid(row=10,column=1,padx=20,pady=(0,10),sticky="ew")
    LCancelSlider = customtkinter.CTkSlider(root.characterFrame, from_=0, to=1, number_of_steps=10)
    LCancelSlider.grid(row=11,column=1)

    # Tech Rate Slider
    techRateLabel = customtkinter.CTkLabel(root.characterFrame,
                                         text="Tech Rate",
                                         width=100,
                                         height=4)
    techRateLabel.grid(row=12,column=1,padx=20,pady=(0,10),sticky="ew")
    techRateSlider = customtkinter.CTkSlider(root.characterFrame, from_=0, to=1, number_of_steps=10)
    techRateSlider.grid(row=13,column=1)

    # Dictionary to store values of slippi bot
    global characterSettings
    characterSettings = {
        "attackStyle" : "Aerial",
        "playStyle" : "Aggressive",
        "edgeguard" : "High",
        "frameDelay" : 0,
        "LCancelRate" : .8,
        "techRate" : .8
    }

    root.mainloop()

def applyChange(key, value):
    global characterSettings
    characterSettings[key] = value

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
    label1.grid(row=1,column=2,padx=20,pady=20)
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


