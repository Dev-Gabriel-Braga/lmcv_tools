import sys
from .interface.core import Core

def main():
   # Iniciando Interface com os Argumentos
   Core.start(sys.argv[1:])

if __name__ == '__main__':
   main()