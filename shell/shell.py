#! /usr/bin/env python3

import sys, os, re

def main():

    while True:
        if 'PS1' in os.environ:
            os.write(1, (os.environ['PS1']).encode())
        else:
            os.write(1, ("$ ").encode())

        try:
            userInput = input()
        except EOFError:
            sys.exit(1)
        except ValueError:
            sys.exit(1)

        inputHandler(userInput) # handle input method

def inputHandler(userInput):
    args = userInput.split() # tokenize user input arguments

    if 'exit' in userInput.lower(): # exit command - Exit and exit both work
        sys.exit(0)

    elif userInput == "":   # empty input, just reprompt the user
        pass

    elif 'cd' in args[0]: # change directory
        try: 
            if len(args) <= 1: # if just cd is specified, move down to parent directory of current directory
                os.chdir("..")
            else: 
                os.chdir(args[1])
            print(os.getcwd())
        except FileNotFoundError:
            os.write(1, ("cd %s: No such file or directory" % args[1]).encode())
            pass

    elif "<" in userInput:
        redirectIn(args)

    elif ">" in userInput: 
        redirectOut(args)

    elif '|' in userInput: # pipe: used to read the output from one command and use it for the input of another command (i.e. dir | sort)
        pipe(args)

    else:
        executeCommand(args)

def redirectIn(args):
    pid = os.getpid()
    rc = os.fork()

    if rc < 0:
        os.write(2, ("fork failed, returning %d\n" % rc).encode())
        sys.exit(1)

    elif rc == 0:
        del args[1]
        # set file descriptor out
        fd = sys.stdout.fileno() 

        try:
            os.execve(args[0], args, os.environ)
        except FileNotFoundError:
            pass
        
        for dir in re.split(":", os.environ['PATH']): # try each directory in the path
                program = "%s/%s" % (dir, args[0])
                try:
                    os.execve(program, args, os.environ) # try to exec program
                except FileNotFoundError:
                    pass
            
            os.write(2, ("%s: command not found\n" % args[0]).encode()) # command not found, print error message
            sys.exit(1)
        
    else:
        childpid = os.wait()


def pipe(args):
    pid = os.getpid()
    pipe = args.index("|") # check for pipe symbol in command

    pr, pw = os.pipe() # tuple
    for f in (pr, pw):
        os.set_inheritable(f,True)
    
    rc = os.fork()

    if rc < 0:
        os.write(2, ("fork failed, returning %d\n" % rc).encode())
        sys.exit(1)

    elif rc == 0: # write to pipe from child
        args = args[:pipe]

        os.close(1)

        fd = os.dup(pw) # dup() duplicates file descriptor 
        os.set_inheritable(fd, True)
        for fd in (pr, pw):
            os.close(fd)
        if os.path.isfile(args[0]):
            try:
                os.execve(args[0], args, os.environ)
            except FileNotFoundError:
                pass
        else:
            for dir in re.split(":", os.environ['PATH']): # try each directory in the path
                program = "%s/%s" % (dir, args[0])
                try:
                    os.execve(program, args, os.environ) # try to exec program
                except FileNotFoundError:
                    pass
            
            os.write(2, ("%s: command not found\n" % args[0]).encode()) # command not found, print error message
            sys.exit(1)
    
    else:
        args = args[pipe+1:]
        
        os.close(0)

        fd = os.dup(pr)
        os.set_inheritable(fd, True)
        for fd in (pw, pr):
            os.close(fd)
        
        if os.path.isfile(args[0]):
            try:
                os.execve(args[0], args, os.environ)
            except FileNotFoundError:
                pass
        else:
            for dir in re.split(":", os.environ['PATH']): # try each directory in the path
                program = "%s/%s" % (dir, args[0])
                try:
                    os.execve(program, args, os.environ) # try to exec program
                except FileNotFoundError:
                    pass
            
            os.write(2, ("%s: command not found\n" % args[0]).encode()) # command not found, print error message
            sys.exit(1)

def executeCommand(args):
    pid = os.getpid()
    rc = os.fork()

    # based off of p3-exec demo

    if rc < 0: # capture error during fork
        os.write(2, ("fork failed, returning %d\n" % rc).encode())
        sys.exit(1)

    elif rc == 0:
        for dir in re.split(":", os.environ['PATH']): # try each directory in the path
            program = "%s/%s" % (dir, args[0])
            try:
                os.execve(program, args, os.environ) # try to exec program
            except FileNotFoundError:
                pass
                
        os.write(2, ("%s: command not found\n" % args[0]).encode()) # command not found, print error message
        sys.exit(1)
    
    else:
        childpid = os.wait()

if __name__ == "__main__":
    main()