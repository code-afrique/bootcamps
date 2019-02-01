# Based on code from 'nbro': https://stackoverflow.com/questions/30410421/run-process-with-realtime-output-to-a-tkinter-gui
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import threading
import time
import os
from subprocess import Popen, PIPE

class Console(tk.Frame):
    def __init__(self, master, *args, **kwargs):
        tk.Frame.__init__(self, master, *args, **kwargs)

        self.text_options = {"state": "disabled",
                             "bg": "black",
                             "fg": "#08c614",
                             "insertbackground": "#08c614",
                             "selectbackground": "#f01c1c"}

        self.text = ScrolledText(self, **self.text_options)
        self.text.tag_config("stdin", foreground="green")
        self.text.tag_config("stdout", foreground="white")
        self.text.tag_config("stderr", foreground="red")

        # It seems not to work when Text is disabled...
        # self.text.bind("<<Modified>>", lambda: self.text.frame.see(tk.END))

        self.text.pack(expand=True, fill="both")

        input = tk.Frame(self)
        tk.Label(input, text="Input:").pack(side=tk.LEFT)
        self.entry = tk.Entry(input)
        self.entry.bind('<Return>', self.entryEnter)
        self.entry.pack(expand=True, fill="both")
        self.entry.focus_set()
        input.pack(expand=True, fill=tk.BOTH)

        self.popen = None     # will hold a reference to a Popen object

        self.bottom = tk.Frame(self)

        self.status = tk.StringVar()
        self.status.set("Executing")
        self.executer = tk.Label(self.bottom, textvariable=self.status)
        self.executer.pack(side="left", padx=5, pady=2)
        self.stopper = tk.Button(self.bottom, text="Stop", command=self.stop)
        self.stopper.pack(side="left", padx=5, pady=2)

        self.bottom.pack(side="bottom", fill="both")

    def entryEnter(self, ev):
        m = self.entry.get() + '\n'
        self.entry.delete(0, tk.END)
        try:
            self.popen.stdin.write(m.encode())
            self.popen.stdin.flush()
            self.show(m, "stdin")
        except:
            pass

    def show(self, message, tag):
        """Inserts message into the Text wiget"""
        self.text.config(state="normal")
        self.text.insert("end", message)
        n = len(message)
        self.text.tag_add(tag, "end-{}c".format(n+1), "end-2c")
        self.text.see("end")
        self.text.config(state="disabled")

    def start_proc(self, command):
        """Starts a new thread and calls process"""
        self.command = command
        # self.process is called by the Thread's run method
        threading.Thread(target=self.process).start()

    def process(self):
        self.execute()

    def stop(self):
        """Stops an eventual running process"""
        if self.popen:
            try:
                self.popen.kill()
            except ProcessLookupError:
                pass 
        self.master.destroy()

    def execute(self):
        """Keeps inserting line by line into self.text
        the output of the execution of self.command"""
        try:
            self.popen = Popen(['python'] + self.command.split(), stdin=PIPE, stdout=PIPE, stderr=PIPE, bufsize=1)
            stdout_iterator = iter(self.popen.stdout.readline, b"")
            stderr_iterator = iter(self.popen.stderr.readline, b"")
            # poll() returns None if the process has not terminated
            # otherwise poll() returns the process's exit code
            while self.popen.poll() is None:
                for line in stdout_iterator:
                    self.show(line.decode("utf-8"), "stdout")
                for line in stderr_iterator:
                    self.show(line.decode("utf-8"), "stderr")
                # else:
                #     time.sleep(0.1)
            self.status.set("Terminated")
        except FileNotFoundError:
            self.show("Can't find python\n\n", "stderr")
        except IndexError:
            self.show("No command entered\n\n", "stderr")
        finally:
            os.remove(self.command)
