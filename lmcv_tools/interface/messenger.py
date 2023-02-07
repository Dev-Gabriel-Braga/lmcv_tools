from sys import exit

class Messenger:
   # Métodos Estáticos
   @staticmethod
   def show(message: str):
      print(message)

   @staticmethod
   def error(message: str):
      print(f'ERROR: {message}')
      exit(1)