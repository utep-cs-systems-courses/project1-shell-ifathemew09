import os, sys, re

rc = os.fork()

if rc < 0:
    os.write(2, ("Fork failed, returning &d\n" %rc).encode())
    sys.exit(1)

elif rc == 0:
    os.write(1, ("Child\n").encode())

    for dir in re.split(":" , os.enviorn['PATH']):
        program = "%s/%s" % (dir, args[0])
        os.write(1, ("Child is trying to exec %s\n" % program).encode())
        try:
            os.execve(program, args, os.enviorn)
        except FileNotFoundError:
            pass
        break
    os.write(2, ("Child was not able to exec%s\n" % args[0]).encode())
    sys.exit(1)

else:
    os.write(1, ("Parent\n").encode())
    waiting = os.wait()
    os.write(1, ("Parent: Child %d terminated with exit code%d\n" % waiting).encode())
            
