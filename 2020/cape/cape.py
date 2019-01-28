import os
import tempfile
import subprocess
import sys
import io
import tkinter as tk
import tkinter.messagebox
import tkinter.filedialog
import tokenize

import pparse
import pmod
import shared
from form import *
from node import *
from block import *

class Scrollable(tk.Frame):
    """
       Make a frame scrollable with a scrollbar
       After adding or removing widgets to the scrollable frame,
       call the update() method to refresh the scrollable area.
    """

    def __init__(self, frame, shared, width=16):
        super().__init__(None)
        self.canvas = tk.Canvas(frame, width=725, height=475)
        self.canvas.isWithinDef = False     # ???
        self.canvas.isWithinLoop = False    # ???
        ysb = tk.Scrollbar(frame, width=width, orient=tk.VERTICAL)
        xsb = tk.Scrollbar(frame, width=width, orient=tk.HORIZONTAL)
        # self.canvas.configure(bd=2, highlightbackground="red", highlightcolor="red", highlightthickness=2)

        self.stuff = Block(self.canvas, shared)
        self.stuff.configure(bd=2, highlightbackground="green", highlightcolor="green", highlightthickness=2)

        ysb.grid(row=0, column=0, sticky=tk.N+tk.S)
        self.canvas.grid(row=0, column=1)
        xsb.grid(row=1, column=1, sticky=tk.W+tk.E)

        ysb.config(command=self.canvas.yview)
        xsb.config(command=self.canvas.xview)
        self.canvas.configure(xscrollcommand=xsb.set)
        self.canvas.configure(yscrollcommand=ysb.set)

        self.canvas.bind('<Configure>', self.__fill_canvas)
        # self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # base class initialization
        tk.Frame.__init__(self, frame)

        # assign this obj (the inner frame) to the windows item of the canvas
        self.windows_item = self.canvas.create_window(0, 0, window=self.stuff, anchor=tk.NW)

    """
    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(-1*(event.delta/120), "units")
    """

    def __fill_canvas(self, event):
        "Enlarge the windows item to the canvas width"

        canvas_width = event.width
        canvas_height = event.height
        # self.canvas.itemconfig(self.windows_item, width = canvas_width)
        # self.canvas.itemconfig(self.windows_item, height = canvas_height)

    def scrollUpdate(self):
        "Update the canvas and the scrollregion"

        self.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox(self.windows_item))
        # self.canvas.config(scrollregion=self.canvas.bbox("all"))

class TopLevel(tk.Frame):
    def __init__(self, parent, shared):
        super().__init__(parent, borderwidth=1, relief=tk.SUNKEN)
        self.parent = parent
        self.shared = shared
        self.curfile = None
        self.program = None

        menu = tk.Menu(parent)
        parent.config(menu=menu)

        file = tk.Menu(menu)
        file.add_command(label="New", command=self.new)
        file.add_command(label="Open", command=self.load)
        file.add_command(label="Save", command=self.save)
        file.add_command(label="Save As", command=self.saveAs)
        file.add_separator()
        file.add_command(label="Exit", command=self.quit)
        menu.add_cascade(label="File", menu=file)

        edit = tk.Menu(menu)
        edit.add_command(label="TO BE IMPLEMENTED")
        menu.add_cascade(label="Edit", menu=edit)

        actions = tk.Menu(menu)
        actions.add_command(label="Show code", command=self.text)
        actions.add_command(label="Run", command=self.run)
        menu.add_cascade(label="Actions", menu=actions)

        help = tk.Menu(menu)
        help.add_command(label="Getting Started", command=self.help)
        menu.add_cascade(label=" Help", menu=help)

        parent.config(menu=menu)

        self.configure(bd=2, highlightbackground="blue", highlightcolor="blue", highlightthickness=2)

        """
        # menubar = tk.Frame(self, borderwidth=1, relief=tk.SUNKEN, style="Custom.TFrame")
        menubar = tk.Frame(self)
        tk.Button(menubar, text="Import", command=self.load).grid(row=0, column=0, sticky=tk.W)
        tk.Button(menubar, text="Export", command=self.save).grid(row=0, column=1, sticky=tk.W)
        tk.Button(menubar, text="Code", command=self.text).grid(row=0, column=2, sticky=tk.W)
        tk.Button(menubar, text="Run", command=self.run).grid(row=0, column=3, sticky=tk.W)
        tk.Button(menubar, text="Help", command=self.help).grid(row=0, column=4, sticky=tk.W)
        tk.Button(menubar, text="Quit", command=self.quit).grid(row=0, column=5, sticky=tk.W)
        menubar.configure(bd=2, highlightbackground="green", highlightcolor="green", highlightthickness=2)
        menubar.grid(row=0, column=0, sticky=tk.W, columnspan=2)
        """

        frame = tk.Frame(self, width=1200, height=500)
        frame.grid(row=1, column=0, sticky=tk.W)
        frame.grid_propagate(0)
        # frame.configure(bd=2, highlightbackground="purple", highlightcolor="purple", highlightthickness=2)

        # self.shared.confarea = tk.Frame(frame, width=400, height=475, bd=10, highlightbackground="green", highlightcolor="green", highlightthickness=3)
        self.shared.confarea = tk.Frame(frame, width=400, height=475)
        # self.shared.confarea.configure(bd=2, highlightbackground="green", highlightcolor="green", highlightthickness=2)
        self.shared.confarea.grid_propagate(0)

        # self.progarea = tk.Frame(frame, width=750, height=500, highlightbackground="green", highlightcolor="green", highlightthickness=3)
        self.progarea = tk.Frame(frame, width=750, height=500)
        # self.progarea = Block(frame, shared)
        # progarea.configure(bd=2, highlightbackground="green", highlightcolor="green", highlightthickness=2)
        self.progarea.grid_propagate(0)

        self.shared.scrollable = Scrollable(self.progarea, shared, width=16)
        self.program = SeqBlock(self.shared.scrollable.stuff, shared, None)
        self.program.grid(sticky=tk.W)
        self.shared.scrollable.scrollUpdate()

        # self.shared.confarea.place(x=0, y=0)
        # self.progarea.place(x=400, y=0)
        # self.shared.confarea.pack(side=tk.LEFT, anchor=tk.NW, fill=tk.BOTH, expand=tk.YES)
        # self.progarea.pack(side=tk.LEFT, anchor=tk.NW, fill=tk.BOTH, expand=tk.YES)
        self.shared.confarea.grid(row=0, column=0, sticky=tk.N)
        self.progarea.grid(row=0, column=1, sticky=tk.NW)

        self.help()

    def xxx(self):
        self.shared.cvtError = False
        n = self.program.toNode()
        if not self.shared.cvtError:
            print("'=== START OF PROGRAM ==='")
            n.print(sys.stdout, 0)
            print("'=== END OF PROGRAM ==='")

    def extractComments(self, code):
        comments = {}
        fd = io.StringIO(code)
        for toktype, tokval, begin, end, line in tokenize.generate_tokens(fd.readline):
            if toktype == tokenize.COMMENT:
                (row, col) = begin
                comments[row] = tokenize.untokenize([(toktype, tokval)])
        return comments

    def new(self):
        if not self.shared.saved:
            tk.messagebox.showinfo("Warning", "You must save the program first")
            self.shared.saved = True
            return

        if self.program != None:
            self.program.grid_forget()
        self.program = SeqBlock(self.shared.scrollable.stuff, self.shared, None)
        self.program.grid(sticky=tk.W)
        self.shared.scrollable.scrollUpdate()

        self.shared.saved = True

    def load(self):
        if not self.shared.saved:
            tk.messagebox.showinfo("Warning", "You must save the program first")
            self.shared.saved = True
            return

        filename = tk.filedialog.askopenfilename(defaultextension='.py',
                                     filetypes=(('Python source files', '*.py'),
                                                ('All files', '*.*')))
        if filename:
            self.curfile = filename
            with open(filename, "r") as fd:
                code = fd.read()
                tree = pparse.pparse(code)
                n = pmod.nodeEval(tree)
                comments = self.extractComments(code)
                for lineno, text in comments.items():
                    (sb, i) = n.findRow(lineno)
                    row = sb.rows[i]
                    if lineno < row.lineno:
                        row = RowNode(EmptyNode(), lineno)
                        sb.rows.insert(i, row)
                    row.comment = text[1:]

                if self.program != None:
                    self.program.grid_forget()
                self.program = SeqBlock(self.shared.scrollable.stuff, self.shared, n)
                self.program.grid(sticky=tk.W)
                self.shared.scrollable.scrollUpdate()

                self.shared.saved = True

    def save(self):
        if self.curfile == None:
            saveAs()
        else:
            self.shared.cvtError = False
            n = self.program.toNode()
            if self.shared.cvtError:
                print("===== Fix program first =====")
            else:
                with open(self.curfile, "w") as fd:
                    n.print(fd, 0)
                    print("saved")
                    self.shared.saved = True

    def saveAs(self):
        self.shared.cvtError = False
        n = self.program.toNode()
        if self.shared.cvtError:
            print("===== Fix program first =====")
        else:
            if self.curfile == None:
                filename = tk.filedialog.asksaveasfilename(defaultextension='.py',
                                         filetypes=(('Python source files', '*.py'),
                                                    ('All files', '*.*')))
            else:
                curName = os.path.basename(self.curfile)
                curDir = os.path.dirname(self.curfile)
                filename = tk.filedialog.asksaveasfilename(initialdir=curDir, initialfile=curFile, defaultextension='.py',
                         filetypes=(('Python source files', '*.py'),
                                            ('All files', '*.*')))
            if filename:
                self.curfile = filename
                with open(filename, "w") as fd:
                    n.print(fd, 0)
                    print("saved")
                    self.shared.saved = True

    def run(self):
        self.shared.cvtError = False
        n = self.program.toNode()
        if self.shared.cvtError:
            print("===== Fix program first =====")
        else:
            fd, path = tempfile.mkstemp()
            try:
                with os.fdopen(fd, 'w') as tmp:
                    n.print(tmp, 0)
                    tmp.close()
                    print("===== Start running =====")
                    # subprocess.Popen(['python3', path])
                    subprocess.call(['python3', path])
                    print("===== Done =====")
            finally:
                os.remove(path)

    def help(self):
        if self.shared.curForm != None:
            self.shared.curForm.grid_forget()
        self.shared.curForm = HelpForm(self.shared.confarea, self)
        self.shared.curForm.grid(row=0, column=0, sticky=tk.E)
        self.shared.curForm.update()

    def text(self):
        if self.shared.curForm != None:
            self.shared.curForm.grid_forget()
        self.shared.curForm = TextForm(self.shared.confarea, self)

        self.shared.cvtError = False
        n = self.program.toNode()
        if not self.shared.cvtError:
            f = io.StringIO("")
            n.print(f, 0)
            self.shared.curForm.settext(f.getvalue())
            self.shared.curForm.grid(row=0, column=0, sticky=tk.E+tk.S+tk.W+tk.N)
            self.shared.curForm.update()

    def quit(self):
        if self.shared.saved:
            sys.exit(0)
        else:
            tk.messagebox.showinfo("Warning", "You must save the program first")
            self.shared.saved = True

if __name__ == '__main__':
    root = tk.Tk()
    root.title("Code Afrique Python Editor")
    root.geometry("1250x550")
    shared = shared.Shared()
    tl = TopLevel(root, shared)
    tl.grid()
    tl.grid_propagate(0)
    root.mainloop()
