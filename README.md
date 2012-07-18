## Introduction
This open source python package Egolpy (Extendable Game of Life in Python) provides classes and an interface for running games similiar to Conway's Game of Life (CGOL).
The graphical interface relies on pygame and ingame controls are mapped to keyboard bindings (the bindings are hardcoded in the main function in egolpy.py). Dimensions, rules and inital states of the game can be set and loaded at launch by passing arguments to the main program (run `python egolpy.py --help` for more info). Note: *This is an early prototype/alpha release - it works and has a somewhat decent interface but there is definitely room for major improvements and a need for refactoring.*


![Egolpy 4gol.rules screenshot (run cmd from 4gol.cmd)](https://github.com/bjodah/egolpy/raw/master/screenshot.png)


## Installation
This package is written in python, i.e. no compilation is required.
However, in order to speed facilitate rapid development the package relies on pygame for graphical presentation.

In order to get a copy of Egolpy execute:

    git clone https://github.com/bjodah/egolpy.git

In order to get stated execute e.g.:

    python egolpy.py -W 800 -H 800 -x 100 -y 100 -n num_Three -m numpy -p -u 20

(for further information on invocation see help by executing e.g. `python egolpy.py --help`)

## Prerequisites
This package relies on:

- [Python](http://python.org) 2.7.x or >3.2
- [Pygame](http://pygame.org) 1.9.1 to enable graphical output (Ubuntu package name: python-pygame)


## Game of Life
Conway's Game of Life
http://en.wikipedia.org/wiki/Conway%27s_Game_of_Life

Rules of Conway's game of life:

    1. Any live cell with fewer than two live
       neighbours dies, as if caused by under-population.
    2. Any live cell with two or three live neighbours
       lives on to the next generation.
    3. Any live cell with more than three live neighbours
       dies, as if by overcrowding.
    4. Any dead cell with exactly three live neighbours
       becomes a live cell, as if by reproduction.

This program is made *extendable* by representing the rules as a combination of numbers. One representation is the actual code for state propagation in the `Gol`-class. But in order to facilitate easy extenability a generalization of the algortihm is made. This generalization and how the resulting parameters giving the behaviour of Conway's Game of Life look like in the chosen representation is presented below:

First the game plan is represented as a two-dimensional grid where each square (or rectangle) on the grid has a stored state. The state history is not stored. In CGOL there are two states: Dead or Alive, here chosen to represented by 0 and 1 respectively. The fate of a grid cell is governed by rules. These rules depends on what state the grid cell has. Generally there are outcomes with conditions and a default outcome in case non of the conditions are matched.

In CGOL a dead cell stays dead unless the number of alive cells in the first "neighbour shell" is exactly 3, in which case the dead cell becomes alive. (This is rule number 4) A living cell on the other hand dies (rule 1 and 3) unless the number of alive cells around it in the first "neighbour shell" is 2 or 3 (rule 2).

In the generalized rules employed in this program a list of rules are looked up for each state in a rules dictionary, then a each rule is tried until one with satisfied conditions are met. If the list is exhausted the default outcome is applied. The individual rules are given as counting the number of cells of a specified kind in a range of neighbouring cell shells. If the number of cells of the special kind is present as a key in an outcome dictionary the resulting state (corresponding value in the dictionary) is applied.

For larger sets of states and outcomes these dictionaries can become quite large why it may be beneficial to write a small script generating these rules data structures. For how to accomplish this see "Generating rules"

## Generating rules
The rules are stored as class definitions in contrib/GameSpecifiaction

## Possible future extensions
Feel free to write them and make a pull request at github:
- Write alternative backends for graphics
- Make rule specification even more general
- Make GameState class use numpy arrays. (Need to write ufuncs also)
- Refactor classes for more intuitive representation
- Optimize performance (preferably cython based)
- Make a class based API to enhance brevity of rule generating scripts.

## Participate
Any comments and/or improvements of the code are greatly appreciated.
Improvements are best done by making a pull request at github
It is also the place to raise issues and filing bug reports.

Latest version is available at github.com/bjodah/egolpy


## Contact information
- Author of python package: Björn Ingvar Dahlgren
- Email (@gmail.com): bjodah

## License information
This work is open source and is released under the 2-clause BSD license (see LICENSE.txt for further information)

Copyright (c) 2011, 2012 Björn Ingvar Dahlgren, Axel Ingvar Dahlgren
