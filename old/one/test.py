#!/usr/bin/env python

import os, sys

from doctest import testmod, NORMALIZE_WHITESPACE, ELLIPSIS

# port that all modules assume the suprocess server is running on 
SUBPROCESS_PORT = 4999

def doctest_modules(modules, verbose=False):
    """
    INPUT:

    - ``modules`` -- a list of modules
    - ``verbose`` -- bool (default: False)
    
    EXAMPLES::

    Stupid test -- do nothing::
    
        >>> doctest_modules([])
    """
    cwd = os.path.abspath(os.curdir)
    for module in modules:
        print "doctest.testmod(%s)"%module.__name__
        os.chdir(cwd)
        testmod(module, optionflags=NORMALIZE_WHITESPACE | ELLIPSIS, verbose=verbose)

if __name__ == '__main__':
    #TODO proper option parsing

    import misc
    try:
        misc.get("http://localhost:%s"%SUBPROCESS_PORT)
    except misc.ConnectionError:
        print "subprocess server: starting a new one"
        import subprocess_server
        r = subprocess_server.Daemon(SUBPROCESS_PORT)
    else:
        print "subprocess server: using existing one"
        

    # TODO: more powerful control, e.g., verbosity, etc. ; only certain modules
    if len(sys.argv) > 1 and sys.argv[1] == '-d':

        import backend, client, frontend, misc, model, session, subprocess_server
        modules = [backend, client, frontend, misc, model, session, subprocess_server]
        
        if len(sys.argv) > 2:
            mods = [x.rstrip('.py') for x in sys.argv[2:]] #TODO: not how rstrip works!
            modules = [x for x in modules if x.__name__ in mods]
        doctest_modules(modules, verbose = '-v' in sys.argv)
    else:
        os.system('py.test %s'%(' '.join(sys.argv[1:])))
            

        
