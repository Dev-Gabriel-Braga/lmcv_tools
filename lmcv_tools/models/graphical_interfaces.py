from tkinter import Tk, filedialog, END
from tkinter.ttk import (
   Style,
   Frame,
   Label,
   Entry,
   Spinbox,
   Combobox,
   Button
)
from ..interface import messenger

class PromptGenerateVirtualLamina:
   def __init__(self, params: dict):
      # Dicionário de Parâmetros para Geração das Lâminas
      self.params = params

      # Definindo Janela Principal
      self.root = Tk()
      self.root.title('Generate Virtual Laminas')
      self.root.resizable(False, False)
      self.root.geometry('+200+100')

      # Definindo Organização de Widgets
      self.frame = dict()
      self.label = dict()
      self.entry = dict()
      self.button = dict()

      # Estilos
      self.default_font = ('sans-serif', 12)
      self.style = Style(self.root)
      self.style.configure('TLabel', font = self.default_font)
      self.style.configure('TButton', font = self.default_font)
      self.style.configure('title.TLabel', font = ('sans-serif', 14, 'italic'))

      # Definindo Layout
      self.layout_grading_params()
      self.layout_simulation_params()
      self.layout_materials_params()
      self.layout_action()
   
   def layout_grading_params(self):
      self.frame['grading_params'] = Frame(
         master = self.root,
         padding = (10, 10),
      )
      self.frame['grading_params'].pack(fill = 'x')

      self.label['title_grading'] = Label(
         master = self.frame['grading_params'],
         text = 'Functionally Grading Parameters',
         style = 'title.TLabel',
         padding = (0, 0, 0, 10),
      )
      self.label['title_grading'].grid(row = 0, columnspan = 2, sticky = 'w')

      self.label['laminas_count'] = Label(
         master = self.frame['grading_params'], 
         text = 'Laminas Count:',
         padding = (0, 5, 10, 5),
      )
      self.label['laminas_count'].grid(row = 1, column = 0, sticky = 'w')

      self.entry['laminas_count'] = Spinbox(
         master = self.frame['grading_params'], 
         from_ = 1,
         to = 100.0,
         width = 3,
         font = self.default_font,
      )
      self.entry['laminas_count'].grid(row = 1, column = 1, sticky = 'w')

      self.label['power_law_exponent'] = Label(
         master = self.frame['grading_params'], 
         text = 'Power Law Exponent:',
         padding = (0, 5, 10, 5)
      )
      self.label['power_law_exponent'].grid(row = 2, column = 0, sticky = 'w')

      self.entry['power_law_exponent'] = Spinbox(
         master = self.frame['grading_params'], 
         from_ = 0,
         to = 10,
         increment = 0.1,
         width = 6,
         font = self.default_font,
      )
      self.entry['power_law_exponent'].grid(row = 2, column = 1, sticky = 'w')

      self.label['micromechanical_model'] = Label(
         master = self.frame['grading_params'], 
         text = 'Micromechanical Model:',
         padding = (0, 5, 10, 5),
      )
      self.label['micromechanical_model'].grid(row = 3, column = 0, sticky = 'w')

      self.entry['micromechanical_model'] = Combobox(
         master = self.frame['grading_params'],
         state = 'readonly',
         values = ['voight', 'mori_tanaka'],
         font = self.default_font,
         width = 12,
      )
      self.entry['micromechanical_model'].grid(row = 3, column = 1, sticky = 'w')

   def layout_simulation_params(self):
      self.frame['simulation_params'] = Frame(
         master = self.root,
         padding = (10, 10),
      )
      self.frame['simulation_params'].pack(fill = 'x')

      self.label['title_simulation'] = Label(
         master = self.frame['simulation_params'],
         text = 'Simulation Parameters',
         style = 'title.TLabel',
         padding = (0, 0, 0, 10),
      )
      self.label['title_simulation'].grid(row = 0, columnspan = 4, sticky = 'ws')

      self.label['element_type'] = Label(
         master = self.frame['simulation_params'],
         text = 'Element Type: ',
         padding = (0, 5, 0, 5),
      )
      self.label['element_type'].grid(row = 1, column = 0, sticky = 'w')

      self.entry['element_type'] = Combobox(
         master = self.frame['simulation_params'],
         state = 'readonly',
         values = ['Solid', 'Shell'],
         font = self.default_font,
         width = 12,
      )
      self.entry['element_type'].bind('<<ComboboxSelected>>', self.change_element_type)
      self.entry['element_type'].grid(row = 2, column = 0, sticky = 'w')

      self.label['absolute_thickness'] = Label(
         master = self.frame['simulation_params'], 
         text = 'Laminas Absolute\nThickness:',
         padding = (0, 5, 10, 5)
      )

      self.entry['absolute_thickness'] = Spinbox(
         master = self.frame['simulation_params'], 
         from_ = 0.1,
         to = 100,
         increment = 0.1,
         width = 6,
         font = self.default_font,
      )

      self.label['laminas_per_element'] = Label(
         master = self.frame['simulation_params'], 
         text = 'Laminas Per\nElement:',
         padding = (0, 5, 10, 5)
      )

      self.entry['laminas_per_element'] = Spinbox(
         master = self.frame['simulation_params'], 
         from_ = 1,
         to = 100,
         increment = 1,
         width = 6,
         font = self.default_font,
      )

      self.label['number_integration_points'] = Label(
         master = self.frame['simulation_params'], 
         text = 'Number of Integration\nPoints:',
         padding = (0, 5, 10, 5)
      )
      self.label['number_integration_points'].grid(row = 3, column = 0, sticky = 'w')

      self.entry['number_integration_points'] = Spinbox(
         master = self.frame['simulation_params'], 
         from_ = 1,
         to = 15,
         increment = 1,
         width = 6,
         font = self.default_font,
      )
      self.entry['number_integration_points'].grid(row = 3, column = 1, sticky = 'w')

   def layout_materials_params(self):
      self.frame['materials_params'] = Frame(
         master = self.root,
         padding = (10, 10),
      )
      self.frame['materials_params'].pack(fill = 'x')

      self.label['title_materials'] = Label(
         master = self.frame['materials_params'],
         text = 'Materials Parameters',
         style = 'title.TLabel',
         padding = (0, 0, 0, 10),
      )
      self.label['title_materials'].grid(row = 0, columnspan = 6, sticky = 'ws')

      self.label['E1'] = Label(
         master = self.frame['materials_params'],
         text = 'E1 = ',
         padding = (0, 5, 0, 5),
      )
      self.label['E1'].grid(row = 1, column = 0, sticky = 'w')

      self.entry['E1'] = Entry(
         master = self.frame['materials_params'], 
         width = 6,
         font = self.default_font,
      )
      self.entry['E1'].grid(row = 1, column = 1, sticky = 'w', padx = 5)

      self.label['nu1'] = Label(
         master = self.frame['materials_params'],
         text = 'ν1 = ',
         padding = (0, 5, 0, 5),
      )
      self.label['nu1'].grid(row = 1, column = 2, sticky = 'w', padx = 5)

      self.entry['nu1'] = Entry(
         master = self.frame['materials_params'], 
         width = 6,
         font = self.default_font,
      )
      self.entry['nu1'].grid(row = 1, column = 3, sticky = 'w', padx = 5)

      self.label['pho1'] = Label(
         master = self.frame['materials_params'],
         text = 'ρ1 = ',
         padding = (0, 5, 0, 5),
      )
      self.label['pho1'].grid(row = 1, column = 4, sticky = 'w', padx = 5)

      self.entry['pho1'] = Entry(
         master = self.frame['materials_params'], 
         width = 6,
         font = self.default_font,
      )
      self.entry['pho1'].grid(row = 1, column = 5, sticky = 'w')

      self.label['E2'] = Label(
         master = self.frame['materials_params'],
         text = 'E2 = ',
         font = self.default_font,
         padding = (0, 5, 0, 5),
      )
      self.label['E2'].grid(row = 2, column = 0, sticky = 'w')

      self.entry['E2'] = Entry(
         master = self.frame['materials_params'], 
         width = 6,
         font = self.default_font,
      )
      self.entry['E2'].grid(row = 2, column = 1, sticky = 'w', padx = 5)

      self.label['nu2'] = Label(
         master = self.frame['materials_params'],
         text = 'ν2 = ',
         padding = (0, 5, 0, 5),
      )
      self.label['nu2'].grid(row = 2, column = 2, sticky = 'w', padx = 5)

      self.entry['nu2'] = Entry(
         master = self.frame['materials_params'], 
         width = 6,
         font = self.default_font,
      )
      self.entry['nu2'].grid(row = 2, column = 3, sticky = 'w', padx = 5)

      self.label['pho2'] = Label(
         master = self.frame['materials_params'],
         text = 'ρ2 = ',
         padding = (0, 5, 0, 5),
      )
      self.label['pho2'].grid(row = 2, column = 4, sticky = 'w', padx = 5)

      self.entry['pho2'] = Entry(
         master = self.frame['materials_params'], 
         width = 6,
         font = self.default_font,
      )
      self.entry['pho2'].grid(row = 2, column = 5, sticky = 'w')

   def layout_action(self):
      self.frame['action'] = Frame(
         master = self.root,
         padding = (10, 10),
      )
      self.frame['action'].pack(fill = 'x')

      self.label['path'] = Label(
         master = self.frame['action'],
         text = 'Output File Path:',
         padding = (0, 5, 0, 5),
      )
      self.label['path'].grid(row = 0, column = 0, sticky = 'w')

      self.entry['path'] = Entry(
         master = self.frame['action'], 
         font = self.default_font,
         width = 25,
      )
      self.entry['path'].grid(row = 1, column = 0, )

      self.button['path'] = Button(
         master = self.frame['action'],
         text = 'Select Folder',
         command = self.select_path,
      )
      self.button['path'].grid(row = 1, column = 1)

      self.button['generate'] = Button(
         master = self.frame['action'],
         text = 'Generate',
         command = self.validate,
      )
      self.button['generate'].grid(row = 2, column = 0, columnspan = 2, pady=(5, 0))

   def start(self):
      self.root.mainloop()

   def select_path(self):
      path = filedialog.askdirectory()
      if path:
         self.entry['path'].delete(0, END)
         self.entry['path'].insert(0, path)

   def validate(self):
      # Copiando Entradas para Validação
      entries = self.entry.copy()

      # Verificando Tipo de Elemento
      if (element_type := entries['element_type'].get()) == '':
         return messenger.show('"Element Type" is required.')
      self.params['element_type'] = element_type

      # Verificando Espessura com Base no Tipo do Elemento
      if element_type == 'Shell':
         if (thickness := entries['absolute_thickness'].get()) == '':
            return messenger.show('"Laminas Absolute Thickness" is required.')
         self.params['laminas_thickness'] = float(thickness)
      else:
         if (laminas_per_element := entries['laminas_per_element'].get()) == '':
            return messenger.show('"Laminas Per Element" is required.')
         self.params['laminas_per_element'] = float(laminas_per_element)

      # Verificando Modelo Micromecânico
      if (micromechanical_model := entries['micromechanical_model'].get()) == '':
         return messenger.show('"Micromechanical Model" is required.')
      self.params['micromechanical_model'] = micromechanical_model

      # Atribuindo Caminho do Arquivo
      self.params['path'] = entries['path'].get().strip()

      # Deletando Entradas Verificadas
      del entries['element_type']
      del entries['laminas_per_element']
      del entries['absolute_thickness']
      del entries['micromechanical_model']
      del entries['path']

      # Verificando Demais Entradas
      for key, value in entries.items():
         if value.get() == '':
            return messenger.show('All fieds are required (except "Output File Path"), fill them.')
         type_class = int if key in ['laminas_count', 'number_integration_points'] else float
         self.params[key] = type_class(value.get())
      
      # Gerando Espessura Relativa para Elementos Sólidos
      if self.params.get('laminas_per_element'):
         self.params['laminas_thickness'] = 1 / self.params['laminas_per_element']
         del self.params['laminas_per_element']
      
      # Terminando Interface
      self.root.destroy()
   
   def change_element_type(self, e):
      value = self.entry['element_type'].get()
      if value == 'Shell':
         self.label['laminas_per_element'].grid_forget()
         self.entry['laminas_per_element'].grid_forget()
         self.label['absolute_thickness'].grid(row = 1, column = 1, sticky = 'w')
         self.entry['absolute_thickness'].grid(row = 2, column = 1, sticky = 'w')
      else:
         self.label['absolute_thickness'].grid_forget()
         self.entry['absolute_thickness'].grid_forget()
         self.label['laminas_per_element'].grid(row = 1, column = 1, sticky = 'w')
         self.entry['laminas_per_element'].grid(row = 2, column = 1, sticky = 'w')
