# Based on code from 'nbro': https://stackoverflow.com/questions/30410421/run-process-with-realtime-output-to-a-tkinter-gui
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import threading
import time
from subprocess import Popen, PIPE

class Console(tk.Frame):

    """Simple console that can execute bash commands"""

    def __init__(self, master, *args, **kwargs):
        tk.Frame.__init__(self, master, *args, **kwargs)

        self.text_options = {"state": "disabled",
                             "bg": "black",
                             "fg": "#08c614",
                             "insertbackground": "#08c614",
                             "selectbackground": "#f01c1c"}

        self.text = ScrolledText(self, **self.text_options)

        # It seems not to work when Text is disabled...
        # self.text.bind("<<Modified>>", lambda: self.text.frame.see(tk.END))

        self.text.pack(expand=True, fill="both")

        # bash command, for example 'ping localhost' or 'pwd'
        # that will be executed when "Execute" is pressed
        self.command = ""  
        self.popen = None     # will hold a reference to a Popen object
        self.running = False  # True if the process is running

        self.bottom = tk.Frame(self)

        self.status = tk.StringVar()
        self.status.set("Executing")
        self.executer = tk.Label(self.bottom, textvariable=self.status)
        self.executer.pack(side="left", padx=5, pady=2)
        self.stopper = tk.Button(self.bottom, text="Stop", command=self.stop)
        self.stopper.pack(side="left", padx=5, pady=2)

        self.bottom.pack(side="bottom", fill="both")

    def show(self, message):
        """Inserts message into the Text wiget"""
        self.text.config(state="normal")
        self.text.insert("end", message)
        self.text.see("end")
        self.text.config(state="disabled")

    def start_proc(self, command):
        """Starts a new thread and calls process"""
        self.stop()
        self.running = True
        self.command = command
        # self.process is called by the Thread's run method
        threading.Thread(target=self.process).start()

    def process(self):
        """Runs in an infinite loop until self.running is False""" 
        while self.running:
            self.execute()

    def stop(self):
        """Stops an eventual running process"""
        if self.popen:
            try:
                self.popen.kill()
            except ProcessLookupError:
                pass 
        self.running = False

    def execute(self):
        """Keeps inserting line by line into self.text
        the output of the execution of self.command"""
        try:
            # self.popen is a Popen object
            self.popen = Popen(self.command.split(), stdout=PIPE, bufsize=1)
            lines_iterator = iter(self.popen.stdout.readline, b"")

            # poll() return None if the process has not terminated
            # otherwise poll() returns the process's exit code
            while self.popen.poll() is None:
                for line in lines_iterator:
                    self.show(line.decode("utf-8"))
                else:
                    time.sleep(0.1)
            # self.show("Process " + self.command  + " terminated.\n\n")
            self.status.set("Terminated")

        except FileNotFoundError:
            self.show("Unknown command: " + self.command + "\n\n")                               
        except IndexError:
            self.show("No command entered\n\n")

        self.stop()
