import os
import tempfile
import subprocess
import sys
import io
import keyword
import tkinter as tk
import tkinter.messagebox
import tkinter.filedialog
import tkinter.scrolledtext
import tokenize
import queue
import ast
import argparse
import pmod
import shared
from form import HelpForm, TextForm
from block import Block, ModuleBlock
import console

class Scrollable(tk.Frame):
    "\n       Make a frame scrollable with a scrollbar\n       After adding or removing widgets to the scrollable frame,\n       call the update() method to refresh the scrollable area.\n    "

    def __init__(self, frame, shared, width=16):
        super().__init__(None)
        self.canvas = tk.Canvas(frame, width=725, height=445)
        self.canvas.isWithinDef = False    # ???
        self.canvas.isWithinLoop = False    # ???
        self.canvas.isWithinStore = False    # ???
        ysb = tk.Scrollbar(frame, width=width, orient=tk.VERTICAL)
        xsb = tk.Scrollbar(frame, width=width, orient=tk.HORIZONTAL)
        # self.canvas.configure(bd=2, highlightbackground="red", highlightcolor="red", highlightthickness=2)
        self.stuff = shared.canvas = Block(self.canvas, shared)
        self.stuff.isTop = True
        # self.stuff.configure(bd=2, highlightbackground="green", highlightcolor="green", highlightthickness=2)
        ysb.grid(row=0, column=0, sticky=(tk.N + tk.S))
        self.canvas.grid(row=0, column=1)
        xsb.grid(row=1, column=1, sticky=(tk.W + tk.E))
        ysb.config(command=self.canvas.yview)
        xsb.config(command=self.canvas.xview)
        self.canvas.configure(xscrollcommand=xsb.set)
        self.canvas.configure(yscrollcommand=ysb.set)
        self.canvas.bind("<Configure>", self.__fill_canvas)
        # self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        # base class initialization
        tk.Frame.__init__(self, frame)
        # assign this obj (the inner frame) to the windows item of the canvas
        self.windows_item = self.canvas.create_window(0, 0, window=self.stuff, anchor=tk.NW)
    "\n    def _on_mousewheel(self, event):\n        self.canvas.yview_scroll(-1*(event.delta/120), \"units\")\n    "

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

class CAPE(tk.Frame):

    def __init__(self, parent, shared, filename):
        super().__init__(parent, borderwidth=1, relief=tk.SUNKEN)
        self.parent = parent
        self.shared = shared
        self.curfile = None
        self.program = None
        menu = tk.Menu(parent)
        parent.config(menu=menu)
        file = tk.Menu(menu)
        file.add_command(label="New", command=self.new)
        file.add_command(label="Open", command=self.open)
        file.add_command(label="Save", command=self.save)
        file.add_command(label="Save As", command=self.saveAs)
        file.add_separator()
        file.add_command(label="Exit", command=self.quit)
        menu.add_cascade(label="File", menu=file)
        edit = tk.Menu(menu)
        edit.add_command(label="Cut", command=self.cut)
        edit.add_command(label="Copy", command=self.copy)
        edit.add_command(label="Paste", command=self.paste)
        menu.add_cascade(label="Edit", menu=edit)
        actions = tk.Menu(menu)
        actions.add_command(label="Show code", command=self.text)
        actions.add_command(label="Run", command=self.run)
        menu.add_cascade(label="Actions", menu=actions)
        help = tk.Menu(menu)
        help.add_command(label="Getting Started", command=self.help)
        menu.add_cascade(label=" Help", menu=help)
        parent.config(menu=menu)
        # self.configure(bd=2, highlightbackground="blue", highlightcolor="blue", highlightthickness=2)

        self.shared.confarea = tk.Frame(self, width=400, height=475)

        self.shared.confarea.configure(bd=2, highlightbackground="green", highlightcolor="green", highlightthickness=2)
        self.shared.confarea.grid_propagate(0)

        self.progarea = tk.Frame(self, width=750, height=475)
        self.progarea.configure(bd=2, highlightbackground="green", highlightcolor="green", highlightthickness=2)
        self.shared.scrollable = Scrollable(self.progarea, shared, width=16)

        if filename:
            self.load(filename)
        else:
            self.program = ModuleBlock(self.shared.scrollable.stuff, shared, None)
            self.program.grid(sticky=tk.W)
            self.program.setBlock(self.program.clauses[0].body.rows[0].what)
            self.shared.scrollable.scrollUpdate()
            self.shared.saved = True

        self.errormsgs = tk.scrolledtext.ScrolledText(self, wrap=tk.WORD, width=100, height=3, bd=2, highlightbackground="red", highlightcolor="red", highlightthickness=2)
        self.errormsgs.insert(tk.INSERT, "...error output from running programs will appear here...")

        self.shared.confarea.grid(row=0, column=0, sticky=tk.N)
        self.progarea.grid(row=0, column=1, sticky=tk.NW)
        self.errormsgs.grid(row=1, columnspan=2, sticky=tk.SW + tk.NE)
        self.help()

        self.evq = queue.Queue()
        self.bind("<<RunErr>>", self.runerr)
        # self.master.after(100, self.checkQueue)

    def checkQueue(self):
        self.runerr(None)
        self.master.after(100, self.checkQueue)

    def runerr(self, ev):
        while not self.evq.empty():
            (line, col, err) = self.evq.get()
            print("ERROR", line, col, err)
            # if 0 <= line < len(self.shared.linebuf):
            #   self.program.setBlock(self.shared.linebuf[line])
            # tk.messagebox.showinfo("Run Error", err)
            self.displayErr(line, err)

    def displayErr(self, lineno, err):
        self.errormsgs.delete('1.0', tk.END)
        self.errormsgs.insert(tk.INSERT, err)

        (type, b, i) = self.node.findLine(lineno)
        if type == "row":
            # print("ROW", lineno, i)
            row = b.rows[i]
        else:
            # print("CLAUSE", lineno, i)
            assert type == "clause"
            row = b
        blk = self.shared.linebuf[int(row.commentR)]
        self.program.setBlock(blk)

    def printx(self):
        self.shared.cvtError = False
        n = self.program.toNode()
        if (not self.shared.cvtError):
            print("'=== START OF PROGRAM ==='")
            n.print(sys.stdout, 0)
            print("'=== END OF PROGRAM ==='")

    def extract(self, code):
        keywords = queue.Queue()
        keywords.put(("module", 0, 0))
        comments = {}
        fd = io.StringIO(code)
        for (toktype, tokval, begin, end, line) in tokenize.generate_tokens(fd.readline):
            if (toktype == tokenize.COMMENT):
                (row, col) = begin
                comments[row] = tokenize.untokenize([(toktype, tokval)])
            elif (toktype == tokenize.NAME):
                (row, col) = begin
                if keyword.iskeyword(tokval):
                    keywords.put((tokval, row, col))
        return (keywords, comments)

    def new(self):
        if (not self.shared.saved):
            tk.messagebox.showinfo("Warning", "You must save the program first")
            self.shared.saved = True
            return
        if (self.program != None):
            self.program.grid_forget()
        self.program = ModuleBlock(self.shared.scrollable.stuff, self.shared, None)
        self.program.grid(sticky=tk.W)
        self.program.setBlock(self.program.clauses[0].body.rows[0].what)
        self.shared.scrollable.scrollUpdate()
        self.shared.saved = True

    def open(self):
        if (not self.shared.saved):
            tk.messagebox.showinfo("Warning", "You must save the program first")
            self.shared.saved = True
            return
        filename = tk.filedialog.askopenfilename(defaultextension=".py", filetypes=(("Python source files", "*.py"), ("All files", "*.*")))
        if filename:
            self.load(filename)

    def load(self, filename):
        self.curfile = filename
        with open(filename, "r") as fd:
            # read and parse the program
            code = fd.read()
            self.parse(code)
            self.shared.saved = True

    def getComment(self, text):
        assert (text[0] == "#")
        if len(text) > 1 and text[1] == " ":
            return text[2:]
        return text[1:]

    def parse(self, code):
        n = self.shared.parse(code);
        if self.program != None:
            self.program.grid_forget()
        self.program = n.toBlock(self.shared.scrollable.stuff, self.shared.scrollable.stuff)
        self.program.grid(sticky=tk.W)
        self.shared.scrollable.scrollUpdate()
        self.program.setBlock(self.program.clauses[0].body)

        # verify that conversion has been done right
        # print("verify")
        # tree2 = pparse.pparse(code, show_offsets=False)
        mod2 = ast.parse(code)
        tree2 = ast.dump(mod2, include_attributes=False)
        with open("tree2", "w") as fd:
            fd.write(tree2)
        n3 = self.program.toNode()
        f3 = io.StringIO("")
        n3.print(f3, 0)
        code3 = f3.getvalue()
        with open("code3", "w") as fd:
            fd.write(code3)
        # tree3 = pparse.pparse(code3, show_offsets=False)
        mod3 = ast.parse(code3)
        tree3 = ast.dump(mod3, include_attributes=False)
        with open("tree3", "w") as fd:
            fd.write(tree3)
        if (tree2 != tree3):
            print("Parse verification failed; edit at own risk")

    def save(self):
        if (self.curfile == None):
            self.saveAs()
        else:
            self.shared.cvtError = True
            n = self.program.toNode()
            with open(self.curfile, "w") as fd:
                n.print(fd, 0)
                print("saved")
                self.shared.saved = True

    def saveAs(self):
        self.shared.cvtError = True
        n = self.program.toNode()
        if (self.curfile == None):
            filename = tk.filedialog.asksaveasfilename(defaultextension=".py", filetypes=(("Python source files", "*.py"), ("All files", "*.*")))
        else:
            curName = os.path.basename(self.curfile)
            curDir = os.path.dirname(self.curfile)
            filename = tk.filedialog.asksaveasfilename(initialdir=curDir, initialfile=curName, defaultextension=".py", filetypes=(("Python source files", "*.py"), ("All files", "*.*")))
        if filename:
            self.curfile = filename
            with open(filename, "w") as fd:
                n.print(fd, 0)
                print("saved")
                self.shared.saved = True

    def run(self):
        self.errormsgs.delete('1.0', tk.END)
        self.shared.cvtError = False

        # convert blocks to nodes, while keeping track of RowBlocks and ClauseBlocks
        # as those are the places where comments can be inserted.  Also, use
        # indexes into the list of RowBlocks and ClauseBlocks as inline comments
        # so we can find them back later
        self.shared.startKeeping()
        n = self.program.toNode()
        self.shared.stopKeeping()

        if self.shared.cvtError:
            print("===== Fix program first =====")
        else:
            # convert nodes to code, and parse the code again, this time to get the
            # right line numbers for all the statements, as well as their indices
            # in the comments.  Keep the node tree in self.node, so that if errors
            # occur, we can find the statements.
            f = io.StringIO("")
            n.print(f, 0)
            code = f.getvalue()
            self.node = self.shared.parse(code)

            # Finally, write the (original) code to a file, and start a "console"
            # to run the code and capture its output (including error output
            (fd, path) = tempfile.mkstemp(dir=".", suffix=".py")
            with os.fdopen(fd, "w") as tmp:
                n.print(tmp, 0)
                tmp.close()
                t = tk.Toplevel(self.master)
                c = console.Console(t, self, self.evq)
                c.grid()
                c.start_proc(path)

    # This is an old version of running code that actually runs the code straight
    # within the same Python interpreter.  The advantage is that you don't need
    # another interpreter.  The disadvantage is that Python is no good at sandboxing.
    def runx(self):
        self.shared.cvtError = False
        n = self.program.toNode()
        if self.shared.cvtError:
            print("===== Fix program first =====")
        else:
            f = io.StringIO("")
            n.print(f, 0)
            code = f.getvalue()
            exec(code)

    def help(self):
        if (self.shared.curForm != None):
            self.shared.curForm.grid_forget()
        self.shared.curForm = HelpForm(self.shared.confarea, self.program)
        self.shared.curForm.grid(row=0, column=0, sticky=tk.E)
        self.shared.curForm.update()

    def text(self):
        if (self.shared.curForm != None):
            self.shared.curForm.grid_forget()
        self.shared.curForm = TextForm(self.shared.confarea, self)
        self.shared.cvtError = True
        n = self.program.toNode()
        f = io.StringIO("")
        n.print(f, 0)
        self.shared.curForm.settext(f.getvalue())
        self.shared.curForm.grid(row=0, column=0, sticky=(((tk.E + tk.S) + tk.W) + tk.N))
        self.shared.curForm.update()

    def cut(self):
        if (self.shared.curBlock == None):
            print("nothing to cut")
        else:
            self.shared.curBlock.cut(True)
        pass

    def copy(self):
        if (self.shared.curBlock == None):
            print("nothing to copy")
        else:
            self.shared.curBlock.copy()

    def paste(self):
        if (self.shared.curBlock == None):
            print("nothing to paste into")
        else:
            self.shared.curBlock.paste()

    def quit(self):
        if self.shared.saved:
            sys.exit(0)
        else:
            tk.messagebox.showinfo("Warning", "You must save the program first")
            self.shared.saved = True

def top(root, file):
    s = shared.Shared()
    tl = CAPE(root, s, file)
    tl.grid()
    # tl.grid_propagate(0)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", type=str, help="Python source file")
    args = parser.parse_args()

    root = tk.Tk()
    root.title("Code Afrique Python Editor")
    root.geometry("1175x600")
    top(root, args.file)
    root.mainloop()

if (__name__ == "__main__"):
    main()
