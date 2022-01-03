import sys
import tkinter as tk

from os import getcwd, listdir
from os.path import isfile, join
from importlib.util import module_from_spec, find_spec


class StandardOutput:
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
    event.widget.delete(0, tk.END)
    print(userInput)
        
    if isStrat(userInput, stratNames):
        cache['handlers'] = (
            spec 
            for spec in inspect(
                'strats', 
                userInput
                )
            )
    else:
        print(msgs['invalid'])

def isStrat(userInput, strats):
    """Check if user input exists in strategies."""
    if userInput in strats:
        return True
    return False
        
def inspect(package, module):
    """Pull out and print module source code, ask for user approval and change the entry callback.
    
    Returns the arguments for executeFrom.
    """
    spec = find_spec(
        f'.{module}', 
        package=package
        )    
    sourceCode = spec.loader.get_source(
        f'{package}.{module}'
        )
    entry.bind('<Return>', executionEntry)
    print(
        f"{module} {msgs['inspect']}\n", 
        sourceCode + '\n', 
        f"{msgs['proceed']}", 
        sep='\n'
        )
    
    return spec, sourceCode
        
def executionEntry(event):
    """Control module execution upon user input."""
    userInput = event.widget.get()
    event.widget.delete(0, tk.END)
    print(userInput)
    
    if userInput == 'yes':
        executeFrom(*cache['handlers'])
    else:
        entry.bind('<Return>', moduleEntry)
        print(
            msgs['abort'],
            msgs['nextop'],
            *stratNames,
            sep='\n'
            )
        
def executeFrom(spec, sourceCode):
    """Execute the source code of a module."""
    print()
    
    module = module_from_spec(spec)
    codeObject = compile(
        sourceCode, 
        module.__spec__.origin, 
        'exec'
        )
    exec(codeObject, module.__dict__)
    
    entry.bind('<Return>', moduleEntry)
    print(
        f"\n{msgs['complete']}",
        msgs['nextop'],
        *stratNames,
        sep='\n'
        )

def setup():
    """Initialize the GUI window and divide it into two parts: the output and input boxes."""
    root = tk.Tk()
    root.geometry("500x500")
    root.title("Replicant")
    
    def write(self, string):
        self.insert(tk.END, string)
        self.see(tk.END)
    
    log = tk.Text(root)
    log.insert(tk.END, msgs['welcome'] + '\n')
    for strat in stratNames:
        log.insert(tk.END, strat + '\n')
    log.configure(
        font='TkFixedFont', 
        bg='#000000', 
        fg='#00FF00'
        )
    log.write = write.__get__(log)
    log.pack(fill=tk.BOTH, expand=1)

    entry = tk.Entry(root)
    entry.bind('<Return>', moduleEntry)
    entry.configure(
        font='TkFixedFont', 
        bg='#000000', 
        fg='#00FF00',
        insertbackground='#00FF00'
        )
    entry.icursor(tk.END)
    entry.pack(fill=tk.BOTH, expand=1)

    return root, log, entry

if __name__ == '__main__':  
    
    path = f'./strats'
    strats = [
        f 
        for f in listdir(path) 
        if isfile(join(path, f))
        ]
    stratNames = [s.split('.')[0] for s in strats]
    
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
        
    with StandardOutput(log):
        root.mainloop()
