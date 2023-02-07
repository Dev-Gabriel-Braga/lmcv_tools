# LMCV Tools

## 1 - Introduction

LMCV Tools is a **command line tool**  that provides a series of useful functionalities for the day-to-day simulations of the "Laboratório de Mecânica Computacional e Visualização" of the "Universidade Federal do Ceará" (UFC).

### 1.1 - Build and Install from Source

```text
$ pip install build
$ python -m build
$ pip install dist/[name of wheel file].whl
```

### 1.2 - How to Use

Once installed, the basic form of the LMCV Tools commands is:

```text
$ lmcv_tools [commands] [args]
```

To check the installed version, use the command bellow:

```text
$ lmcv_tools version
```

To get help, it's possible use the following command:

```text
$ lmcv_tools help
```
For more complex commands, check out the detailed descriptions in the next section.

---

## 2 - Complex Commands

Considering that the routine activities for which LMCV Tools was developed are quite varied, specific commands were developed for each one of them. These commands are:
- translate (in implementation)

### 2.1 Translate

The command **translate**, in short, aims convert .inp files created by Abaqus in .dat files for FAST.

Abaqus is a suite for Finite Element Analysis (FEA) developed by "Dassault Systèmes", while FAST is a console based FEA tool developed by "Laboratório de Mecânica Computacional e Visualização" of "Universidade Federal do Ceará" (UFC). Both of these softwares can simulate complex problems, but FAST has a clear disadvantage: differently of Abaqus, it hasn't a native GUI to generate its meshes. With that in mind, this command specifically seeks to translate meshes generated in Abaqus and exported in .inp format into meshes in .dat format to be used in FAST simulations.

Its usage is quite simple:

```text
$ lmcv_tools translate [relative path to .inp file]
```

If you need to specify the .dat output path, another possible way is:

```text
$ lmcv_tools translate [relative path to .inp file] [relative path to .dat file]
```