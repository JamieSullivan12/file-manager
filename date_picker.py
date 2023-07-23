import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar

def dateselectioncomplete(cal, window, complete_function):
    # close the calendar window
    window.destroy()
    # retrieve the selected date and pass it back into the complete_function (defined in the parameter)
    date = cal.selection_get()
    complete_function(date)

def dateselect(text, complete_function):
    """
    Create a date window popup
    - text: any information that needs to be shared with the user
    - complete_function: the function that needs to be run upon completion of the date selection
    """
    #new window popup
    calendar_window = tk.Tk() 
    #naming the window
    calendar_window.title('Date Selection') 
    # create an information text label (passed as parameter)
    info_text = tk.Label(calendar_window, text=text, fg='black')
    info_text.pack()
    # create the calendar
    cal = Calendar(calendar_window, font='Helvlevtica 14', selectmode="day", CalendarSelected="date_selected")
    cal.pack(fill="both",expand=True) #adding it to the new window
    # add a complete/ok button. this links to the dateselectioncomplete function above
    ok_button = ttk.Button(calendar_window,text='continue',style="Accent.TButton",width=20,command=lambda:dateselectioncomplete(cal, calendar_window, complete_function))
    ok_button.pack()