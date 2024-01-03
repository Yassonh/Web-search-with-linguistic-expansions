from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import PySimpleGUI as sg
from SearchAPI import *
from nltk.corpus import wordnet as wn

nltk.download('wordnet')
nltk.download('omw-1.4')

global fig_agg
global values


# Draws the histogram onto the Canvas
def drawFigureOnCanvas(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg


# Deletes the histogram to replace it with a new one
def deleteFigAgg(fig_agg):
    fig_agg.get_tk_widget().forget()
    plt.close('all')


# Updates the textbox with the WordNet such as definitions and synonyms
def updateWordnet(window, num, top):
    string = ""
    string += "Word: " + top[num] + "\n"

    try:
        term = wn.synsets(top[num])[0]
        window["Query"].update(f"{values['Query']} {top[num]}")
        list = [lemma.name() for lemma in wn.synset(term.name()).lemmas()]

        string += "Definition: " + term.definition() + "\n" + "Other Words: " + "\n"
        for x in range(len(list)):
            w = list[x].replace("_", " ")
            string += w + " - "
        window["WordNet"].update(string)
    except:
        window["WordNet"].update("word not found in WordNet")



# Refine your query through WordNet
def refine(query, window):
    global fig_agg

    list = query.split(" ")
    wordnet_list = []
    for x in list:
        term = wn.synsets(x)[0]
        wordnet_list += [lemma.name() for lemma in wn.synset(term.name()).lemmas()]

    string = " ".join(wordnet_list)
    string = string.replace("_", " ")
    window["Textbox"].update(search(string))

    if fig_agg is not None:
        deleteFigAgg(fig_agg)
    fig_agg = drawFigureOnCanvas(window["Canvas"].TKCanvas, plot())



# Remove the last term in the query
def removeLastTerm(window):
    query = values['Query'].split(" ")  # Turn query into a list
    query.pop()    # Pop last element in list
    string = ' '.join([str(words) for words in query])  # Turn list into string
    window['Query'].update(string) # Update query box with new string


# Handles all the GUI and events
def GUI():
    left_column = [  # Left side of the GUI
        [sg.Text('Web Search')],
        [sg.Text('Enter Query: '), sg.InputText(key='Query'), sg.Button('Search', bind_return_key=True),
         sg.Button('Remove'), sg.Button('Reset'), sg.Button('Refine', visible=False)],
        [sg.Multiline(key='Textbox', size=(90, 40), disabled=True, visible=False)]
    ]

    middle_column = [  # Middle containing the buttons for the histogram
        [sg.Button(' 1st ', visible=False, key='b0', size=(10, 1))],
        [sg.Button(' 2nd ', visible=False, key='b1', size=(10, 1))],
        [sg.Button(' 3rd ', visible=False, key='b2', size=(10, 1))],
        [sg.Button(' 4th ', visible=False, key='b3', size=(10, 1))],
        [sg.Button(' 5th ', visible=False, key='b4', size=(10, 1))],
        [sg.Button(' 6th ', visible=False, key='b5', size=(10, 1))],
        [sg.Button(' 7th ', visible=False, key='b6', size=(10, 1))],
        [sg.Button(' 8th ', visible=False, key='b7', size=(10, 1))],
        [sg.Button(' 9th ', visible=False, key='b8', size=(10, 1))],
        [sg.Button('10th ', visible=False, key='b9', size=(10, 1))],
        [sg.Text('')],
        [sg.Text('')],
        [sg.Text('')],
        [sg.Text('')],
    ]

    right_column = [  # Right side of GUI containing the histogram and text box
        [sg.Text('Term Frequency Histogram', visible=False, key='Histogram_Text')],
        [sg.Canvas(size=(80, 40), key='Canvas')],
        [sg.Text('WordNet', visible=False, key='WordNet_Text')],
        [sg.Multiline(key='WordNet', size=(80, 5), disabled=True, visible=False)],
    ]

    layout = [  # The whole layout of the GUI
        [sg.Column(left_column),
         sg.VSeperator(pad=(0, 0)),
         sg.Column(middle_column),
         sg.VSeperator(pad=(0, 0)),
         sg.Column(right_column), ]
    ]

    # Create the Window
    window = sg.Window('Project', layout)
    # Event Loop to process "events" and get the "values" of the inputs
    global fig_agg
    fig_agg = None
    while True:
        global top_results
        global values
        event, values = window.read()
        if event == sg.WIN_CLOSED:  # If user closes window or clicks cancel
            break
        if event == 'Reset':  # If user clicks the reset query button
            window['Query'].update('')
        if event == 'Search' and values['Query'] != "" and not values[
            'Query'].isspace():  # If user tries to click search with an empty query
            window['Textbox'].update(search(values['Query']), visible=True)
            window['Histogram_Text'].update(visible=True)
            window['Refine'].update(visible=True)
            if fig_agg is not None:
                deleteFigAgg(fig_agg)
            fig_agg = drawFigureOnCanvas(window['Canvas'].TKCanvas, plot())  # Draws the histogram to the canvas
            top = returnTopResult()

            for x in range(0, 10, 1):  # Creates and updates the buttons for adding terms to the query
                button_name = 'b' + str(x)
                window[button_name].update(top[x], visible=True)
            window['WordNet_Text'].update(visible=True)
            window['WordNet'].update(visible=True)
            window['Histogram_Text'].update('Term Frequency Histogram\t\t\tRating: ' + str(
                round(returnScore(), 3)))  # Display the rating for the query
        if event == 'Refine':  # Calls the refine function
            refine(values['Query'], window)
            top = returnTopResult()

            for x in range(0, 10, 1):
                button_name = 'b' + str(x)
                window[button_name].update(top[x], visible=True)
            window['Histogram_Text'].update('Term Frequency Histogram\t\t\tRating: ' + str(round(returnScore(), 3)))
        if event == 'Remove' and values['Query'] != "" and not values['Query'].isspace():
            removeLastTerm(window)
        if event == 'b0':  # First term button
            updateWordnet(window, 0, top)
        if event == 'b1':  # Second button
            updateWordnet(window, 1, top)
        if event == 'b2':  # Third button
            updateWordnet(window, 2, top)
        if event == 'b3':  # Fourth term button
            updateWordnet(window, 3, top)
        if event == 'b4':  # Fifth term button
            updateWordnet(window, 4, top)
        if event == 'b5':  # Sixth term button
            updateWordnet(window, 5, top)
        if event == 'b6':  # Seventh term button
            updateWordnet(window, 6, top)
        if event == 'b7':  # Eight term button
            updateWordnet(window, 7, top)
        if event == 'b8':  # Ninth term button
            updateWordnet(window, 8, top)
        if event == 'b9':  # Tenth term button
            updateWordnet(window, 9, top)

    window.close()
