import PySimpleGUI as sg
import json



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
    [sg.Text(size=(40, 40), text='hello\nmy name is meric', background_color='white', text_color='black', key='-CHAT BOX-')], 
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

# Run the Event Loop
while True:
    event, values = window.read()
    print('Event: ', event, 'Values: ', values)

    # Check active users and update gui accordingly
    active_user_file = open('active_users.json')
    active_users = json.loads(active_user_file.read())
    window['-PERSON-'].update(active_users)
    active_user_file.close()

    # Check the conversation of the selected person
    if values['-PERSON-']:
        filename = 'conv_' + values['-PERSON-'][0] + '.json'
        f = open(filename)
        convArr = json.loads(f.read())
        f.close()
        convString = convParser(convArr)
        print(convString)
        window['-CHAT BOX-'].update(convString)

    
        
    # Handle events

    if event == "Exit" or event == sg.WIN_CLOSED:
        break
    
    if event == '-SEND BUTTON-':
        newMessage = values['-MESSAGE INPUT-']
        newText = window['-CHAT BOX-'].get() + '\n' + newMessage
        window['-CHAT BOX-'].update(newText)

    # elif event == '-PERSON-':


    

window.close()