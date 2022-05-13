import os
import sys
    
def get_tools():
    from . import tools
    scripts = []
    for path in tools.__path__:
        for entry in os.scandir(path):
            if entry.is_file() and not entry.name.startswith('__') and entry.name.endswith('.py'):
                scripts.append(entry.name[:-3])
    return scripts
                
def print_usage():
    print("Usage: %s <tool> [arguments]" % sys.argv[0])
    print("tool:")
    for script in get_tools():
        print("- %s" % script)

def main():
    if len(sys.argv) < 2:
        print_usage()
        exit(0)
        
    scripts = get_tools()
    if sys.argv[1] in scripts:
        sys.argv = sys.argv[1:]
        import runpy
        runpy.run_module('synack.tools.' + sys.argv[0], run_name='__main__')
    else:
        print("Tool \"%s\" not found!" % sys.argv[1])
        print_usage()
        exit(1)

if __name__ == '__main__':
    main()
