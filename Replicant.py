import sys
from tkinter import Tk, Entry, END, BOTH
from tkinter.scrolledtext import ScrolledText
from os import listdir
from os.path import splitext
from importlib.util import find_spec, module_from_spec


class StandardStream:
    """Context manager for redirection of output and error streams."""
    
    def __init__(self, newOutput):
        self.newOutput = newOutput
        
    def __enter__(self):
        self.oldOutput = sys.stdout
        self.oldErr = sys.stderr

        sys.stdout = self.newOutput
        sys.stderr = self.newOutput

    def __exit__(self, excType, excVal, excTb):
        sys.stdout = self.oldOutput
        sys.stderr = self.oldErr

def moduleEntry(event):
    """Cache the specs of a chosen module."""
    userInput = event.widget.get()
    event.widget.delete(0, END)
    log.write(userInput, 'green')
        
    if userInput in pipelines:
        cache['handlers'] = (
            spec 
            for spec in inspect(
                'pipelines', 
                userInput
                )
            )
    else:
        log.write(msgs['invalid'], 'green')
        
def inspect(package, module):
    """Pull out and print module source code, ask for user approval and change the entry callback.
    
    Returns the arguments for executeFrom.
    """
    spec = find_spec(f'.{module}', package=package)    
    sourceCode = spec.loader.get_source(
        f'{package}.{module}'
        )
    
    entry.bind('<Return>', executionEntry)
    
    log.write(f"{module} {msgs['inspect']}\n", 'green')
    log.write(sourceCode, 'blue')
    log.write(f"\n{msgs['proceed']}", 'green')

    return spec, sourceCode
        
def executionEntry(event):
    """Control module execution upon user input."""
    userInput = event.widget.get()
    event.widget.delete(0, END)
    log.write(userInput, 'green')
    
    if userInput == 'yes':
        executeFrom(*cache['handlers'])
    else:
        entry.bind('<Return>', moduleEntry)
        for message in (msgs['abort'], msgs['nextop'], *pipelines):
            log.write(message, 'green')
        
def executeFrom(spec, sourceCode):
    """Execute the source code of a module."""
    print()
    module = module_from_spec(spec)
    spec.loader.exec_module(module)

    entry.bind('<Return>', moduleEntry)
    for message in (f"\n{msgs['complete']}", msgs['nextop'], *pipelines):
        log.write(message, 'green')

def setup():
    """Initialize the GUI window and divide it into two parts: the output and input boxes."""
    
    root = Tk()
    root.geometry("500x500")
    root.title("Replicant")
    
    log = ScrolledText(root)
    log.configure(
        font='TkFixedFont', 
        bg='#000000', 
        fg='#00FFFF'
        )
    log.pack(fill=BOTH, expand=1)
    log.tag_config('green', foreground="#00FF00")
    log.tag_config('blue', foreground="#0000FF")
    
    def write(self, string, color=None):
        if color is not None:
            string += '\n'
        log.insert(END, string, color)
        log.see(END)
    
    log.write = write.__get__(log)
    for text in (msgs['welcome'], *pipelines):
        log.write(text, 'green')
    
    entry = Entry(root)
    entry.bind('<Return>', moduleEntry)
    entry.configure(
        font='TkFixedFont', 
        bg='#000000', 
        fg='#00FF00',
        insertbackground='#00FF00'
        )
    entry.icursor(END)
    entry.pack(fill=BOTH, expand=1)

    return root, log, entry

if __name__ == '__main__':  
    
    path = './pipelines'
    pipelines = [
        splitext(file)[0]
        for file in listdir(path)
        if splitext(file)[1].startswith('.py')
        ]
    
    cache = {'handlers': ()}

    msgs = {
        'welcome': 'Welcome to Replicant! What do you want to do? Available operations are',
        'nextop': 'If you want to continue, available operations are',
        'abort': 'No module was executed.',
        'inspect': 'will execute the following source code:',
        'proceed': 'Proceed?',
        'complete': 'Module execution complete, returning to default view.',
        'invalid': 'Invalid entry.'
        }

    root, log, entry = setup()
        
    with StandardStream(log):
        root.mainloop()

