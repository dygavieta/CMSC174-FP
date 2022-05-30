import PySimpleGUI as sg
import os.path
import test_checker
from PIL import Image

score = 0
filename = ""

answers = []
with open(f'answer_keys/answer_keys.txt', 'r') as f:
    for line in f.readlines():
        answers.append(line.strip())


def getAnswers(name):
    answers = []
    with open(f'answer_keys/{name}.txt', 'r') as f:
        for line in f.readlines():
            answers.append(line.strip().upper())
    return answers


file_list_column = [
    [sg.Button("Scan", size=(40, 2))],
    [sg.FolderBrowse("Open", size=(40, 2),
                     enable_events=True, key="-FOLDER-")],
    [sg.Text("Correct Answers:")],
]

answers_layout = []
for i in range(len(answers)):
    answers_layout.append([sg.Text(
        f"{i+1}.", pad=(0, 0)), sg.Text(answers[i].upper(), pad=(0, 0),  key=f"-ANSWER{i}-")])

file_list_column += answers_layout

file_list_column += [
    sg.Listbox(
        values=[], enable_events=True, size=(40, 10),
        key="-FILE LIST-"
    )
],
file_list_column += [[sg.Text("Score: ", font=("Any 16")),
                      sg.Text(f"{score}", font=("Any 16"), key="-SCORE-")]]

image_viewer_column = [
    [sg.Text("Choose an image from the list")],
    [sg.Text(size=(40, 1), key="-TOUT-")],
    [sg.Image(size=(600, 900), key="-IMAGE-")],
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
            and file.lower().endswith((".png", ".gif"))
        ]
        window["-FILE LIST-"].update(fnames)
    elif event == "-FILE LIST-":
        try:
            filename = os.path.join(
                values["-FOLDER-"], values["-FILE LIST-"][0]
            )
            window["-TOUT-"].update(filename)
            image = Image.open(filename)
            image = image.resize((600, 900), Image.ANTIALIAS)
            fp = "testcase/currentImage.png"
            image.save(fp="testcase/currentImage.png")
            window["-IMAGE-"].update(size=(600, 900), filename=fp)
        except:
            pass
    if event == "Scan":
        print("Scanning...")
        totalScore, output_dir = test_checker.scan(
            values["-FILE LIST-"][0], values["-FILE LIST-"][0])
        window["-TOUT-"].update(output_dir)
        window["-IMAGE-"].update(filename=(output_dir))
        window["-SCORE-"].update(f"{totalScore}/15")
        for index, value in enumerate(getAnswers(values["-FILE LIST-"][0][::-1][4:][::-1])):
            window[f"-ANSWER{index}-"].update(value)

window.close()
