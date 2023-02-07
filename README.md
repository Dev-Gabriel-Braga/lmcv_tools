# FAST Translator

## Introduction

FAST Translator, in short, is a **command line tool** to aim convert .inp files created by Abaqus in .dat files for FAST. 

Abaqus is a suite for Finite Element Analysis (FEA) developed by "Dassault Systèmes", while FAST is a console based FEA tool developed by "Laboratório de Mecânica Computacional e Visualização" of "Universidade Federal do Ceará" (UFC). Both of these softwares can simulate complex problems, but FAST has a clear disadvantage: differently of Abaqus, it hasn't a native GUI to generate its meshes. With that in mind, this project specifically seeks to translate meshes generated in Abaqus and exported in .inp format into meshes in .dat format to be used in FAST simulations.

## Build and Install from Source

```text
$ python -m build
$ pip install dist/[name of build].whl
```

## Examples of Use

Once installed, you can use fast-translator as shown bellow:

```text
$ ftrans -t [relative path to .inp]
```

To get helh, you also use:
```text Short Version
$ ftrans -h