# Based on code from 'nbro': https://stackoverflow.com/questions/30410421/run-process-with-realtime-output-to-a-tkinter-gui
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import threading
import time
import os
import io
import re
from subprocess import Popen, PIPE
from threading import Thread
from queue import Queue

class Console(tk.Frame):
    def __init__(self, master, main, evq):
        tk.Frame.__init__(self, master)

        # master.protocol("WM_DELETE_WINDOW", self.on_close)
        # master.bind("<Destroy>", self.on_destroy)

        self.main = main
        self.evq = evq
        self.stopped = False
        self.terminated = False

        self.text_options = {"state": "disabled",
                             "bg": "black",
                             "fg": "#08c614",
                             "insertbackground": "#08c614",
                             "selectbackground": "#f01c1c"}

        self.text = ScrolledText(self, **self.text_options)
        self.text.tag_config("stdin", foreground="yellow")
        self.text.tag_config("stdout", foreground="#000fff000")
        self.text.tag_config("stderr", foreground="red")

        # It seems not to work when Text is disabled...
        # self.text.bind("<<Modified>>", lambda: self.text.frame.see(tk.END))

        self.text.grid(row=0, column=0)

        input = tk.Frame(self)
        tk.Label(input, text="Input:").grid(row=0, column=0, sticky=tk.W)
        self.entry = tk.Entry(input)
        self.entry.bind('<Return>', self.entryEnter)
        self.entry.grid(row=0, column=1, sticky=tk.E+tk.W)
        self.entry.focus_set()
        input.grid_columnconfigure(1, weight=1)
        input.grid(row=1, column=0, sticky=tk.E+tk.W)

        self.popen = None     # will hold a reference to a Popen object

        self.bottom = tk.Frame(self)

        self.status = tk.StringVar()
        self.status.set("Executing")
        self.executer = tk.Label(self.bottom, textvariable=self.status)
        self.executer.grid(row=0, column=0, sticky=tk.W)
        self.stopper = tk.Button(self.bottom, text="Stop", command=self.stop)
        self.stopper.grid(row=0, column=1, sticky=tk.W)

        self.bottom.grid(row=2, column=0, sticky=tk.W)

        self.queue = Queue(1024)
        self.open = { "stdout": True, "stderr": True }
        self.errStr = ""

    def on_close(self):
        print("CLOSING")

    def on_destroy(self, ev):
        print("DESTROYED")

    def processQueue(self):
        while not self.queue.empty():
            (tag, c) = self.queue.get()
            if c == None:
                print("CLOSE", tag)
                self.open[tag] = False
            else:
                self.show(c.decode("utf-8"), tag)
                if tag == "stderr":
                    self.errStr += c.decode("utf-8")
        if self.open["stdout"] or self.open["stderr"]:
            self.master.after(100, self.processQueue)
        else:
            errFile = None
            errLine = None
            errCol = None
            errDescr = None
            with io.StringIO(self.errStr) as fd:
                for line in fd:
                    mo = re.match(r' *File "([^"]+)", line (\d+).*', line, re.S|re.I)
                    if mo:
                        errFile = mo.group(1)
                        errLine = int(mo.group(2))
                        errCol = None
                    elif errFile != None:
                        mo = re.match(r'^( *)\^.*$', line)
                        if mo:
                            errCol = len(mo.group(1))
                        else:
                            mo = re.match(r'^\w+Error.*$', line)
                            if mo:
                                errDescr = line
            if errDescr != None:
                self.evq.put((errLine, errCol, errDescr))
                self.main.event_generate("<<RunErr>>", when="tail")

    def entryEnter(self, ev):
        m = self.entry.get() + '\n'
        self.entry.delete(0, tk.END)
        self.show(m, "stdin")
        try:
            self.popen.stdin.write(m.encode())
            self.popen.stdin.flush()
        except:
            pass

    def show(self, message, tag):
        """Inserts message into the Text wiget"""
        try:
            self.text.config(state="normal")
            self.text.insert(tk.END, message, (tag))
            self.text.see("end")
            self.text.config(state="disabled")
        except:
            print("console show had a problem")

    def start_proc(self, command):
        """Starts a new thread and calls process"""
        self.command = command
        threading.Thread(target=self.execute).start()
        self.processQueue()

    def stop(self):
        """Stops an eventual running process"""
        if self.popen:
            try:
                self.popen.kill()
            except ProcessLookupError:
                pass 
        if self.terminated:
            self.master.destroy()
        else:
            self.status.set("Terminating")
            self.stopped = True

    def reader(self, pipe, tag):
        try:
            while not self.stopped:
                c = pipe.read(1)
                if c == b'' or c == '':
                    break
                self.queue.put((tag, c))
                if self.queue.qsize() > 256:
                    print("reader: wait for queue to clear a bit")
                    time.sleep(0.1)
        finally:
            self.queue.put((tag, None))

    def execute(self):
        """Keeps inserting line by line into self.text
        the output of the execution of self.command"""
        try:
            print("start process")
            self.popen = Popen(['python', '-u', self.command], stdin=PIPE, stdout=PIPE, stderr=PIPE, bufsize=0)

            Thread(target=self.reader, args=[self.popen.stdout, "stdout"]).start()
            Thread(target=self.reader, args=[self.popen.stderr, "stderr"]).start()
            while self.popen.poll() is None:
                # print("process still running")
                time.sleep(0.1)
            self.status.set("Terminated")
            print("terminated process")
        except FileNotFoundError:
            self.show("Can't find python\n\n", "stderr")
        finally:
            os.remove(self.command)
            self.terminated = True
            if self.stopped:
                self.master.destroy()
