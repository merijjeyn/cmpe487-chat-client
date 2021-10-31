import PySimpleGUI as sg
import json
from network import Network


def convParser(convArr):
    result = ''
    for s in convArr:
        textArr = s.split('::')
        sender = textArr[0]
        text = textArr[1]
        result += sender + ': ' + text + '\n\n'
    return result


# First the window layout in 2 columns

left_column = [
    [
        sg.Text("People")
    ],
    [
        sg.Listbox(
            values=[], enable_events=True, size=(20, 20), key="-PERSON-"
        )
    ],
]

# For now will only show the name of the file that was chosen
right_column = [
    [sg.Text(size=(40, 40), text='', background_color='white', text_color='black', key='-CHAT BOX-')], 
    [
        sg.Input(enable_events=True, key='-MESSAGE INPUT-'),
        sg.Button(button_text='SEND',enable_events=True, key='-SEND BUTTON-')
    ]
]

# ----- Full layout -----
layout = [
    [
        sg.Column(left_column),
        sg.VSeperator(),
        sg.Column(right_column),
    ]
]

window = sg.Window("MeChat", layout)

# Initialize network element
network = Network()

lastChosen = ''
# Run the Event Loop
while True:
    event, values = window.read()

    # Update last chosen
    if values['-PERSON-']:
        lastChosen = values['-PERSON-'][0]

    # Handle events
    if event == "Exit" or event == sg.WIN_CLOSED:
        break
    
    if event == '-SEND BUTTON-':
        body = values['-MESSAGE INPUT-']
        receiver = lastChosen
        receiverIp = network.getIpFromName(receiver)
        network.sendMessage(receiverIp, body)


    # Check active users and update gui accordingly
    try:
        with open('active_users.json', 'r') as f:
            active_users = json.loads(f.read())
    except:
        active_users = {}
    
    window['-PERSON-'].update(active_users.keys())


    # Check the conversation of the selected person
    if lastChosen:
        with open('conversations.json', 'r') as f:
            try:
                conversations = json.loads(f.read())
            except:
                conversations = {}
            if lastChosen in conversations:
                convArr = conversations[lastChosen]
                convString = convParser(convArr)
                window['-CHAT BOX-'].update(convString)
    
        

window.close()