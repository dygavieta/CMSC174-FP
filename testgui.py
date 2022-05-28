import PySimpleGUI as sg
import os.path
import fpdraft2
from PIL import Image 

score = 0
filename = ""

answer_keys = open('answer_keys/answer_keys.txt','r')
with answer_keys as f_in:
    answers = (answer.rstrip() for answer in f_in) 
    answers = list(answer for answer in answers if answer)
answer_keys.close()

file_list_column = [
    [sg.Button("Scan", size =(40,2))],
    [sg.FolderBrowse("Open", size =(40,2),enable_events=True, key="-FOLDER-")],
    [sg.Text("Answers:")],
]
for i in range(len(answers)):
    file_list_column += [[sg.Text(f"{i+1}.", pad=(0,0)), sg.Text(answers[i].upper(),pad=(0,0))]]

file_list_column +=  [
        sg.Listbox(
            values=[], enable_events=True, size=(40,10),
            key = "-FILE LIST-"
        )
    ],
file_list_column +=[[sg.Text("Score: ", font=("Any 16")), sg.Text(f"{score}", font=("Any 16"), key="-SCORE-")]]

image_viewer_column = [
    [sg.Text("Choose an image from the list")],
    [sg.Text(size=(40,1), key="-TOUT-")],
    [sg.Image(key="-IMAGE-")],
]

layout = [
    [
        sg.Column(file_list_column),
        sg.VSeperator(),
        sg.Column(image_viewer_column),
    ]
]

window = sg.Window("Image Viewer", layout)

while True: 
    event, values = window.read()
    if event == "Exit" or event == sg.WIN_CLOSED:
        break
    if event == "-FOLDER-":
        folder = values["-FOLDER-"]
        try:
            file_list = os.listdir(folder)
        except:
            file_list = []

        fnames = [
            file
            for file in file_list
            if os.path.isfile(os.path.join(folder, file))
            and file.lower().endswith((".png",".gif"))
        ]
        window["-FILE LIST-"].update(fnames) 
    elif event == "-FILE LIST-":
        try:
            filename = os.path.join(
                values["-FOLDER-"], values["-FILE LIST-"][0]
            )
            window["-TOUT-"].update(filename)
            window["-IMAGE-"].update(filename=filename)
        except:
            pass
    if event == "Scan":
        print("Scanning...")
        correctScore,output_dir = fpdraft2.scan(filename, values["-FILE LIST-"][0])
        print(correctScore)
        window["-TOUT-"].update(output_dir)
        window["-IMAGE-"].update(filename=(output_dir))
        window["-SCORE-"].update(f"{correctScore}/15")

window.close()