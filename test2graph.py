#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import matplotlib.pyplot as plt
import numpy as np
import os

config = {                      # Default values:
    'ncols': 3,                 # Number of graph per row
    'cols' : '1 2',             # Columns to read from the data file
    'nlinesReadme': 3,          # Numbers of line readed from the README file
    'prefixTitle': '',          # String used as prefix in the title of each graph 
    'legendLoc': 'upper right', # Default position for the legend
    'noYticks': 2,              # After almost no Y tics will be printed
}

def main():
    args = _parser()
    files = args.filenames
    readReadme = args.readReadme

    if args.xrange: plt.xlim(_parseRange(args.xrange, plt.xlim()))
    if args.yrange: plt.ylim(_parseRange(args.yrange, plt.ylim()))


    config['ncols'] = args.ncols
    config['cols']  = _parseColumns(args.columns)
    
    print('files:', files)

    f, axs = _subplotgenerator(len(files))
    print('cols:', config['cols'])

    k = 0
    for f in files:             # Main loop over the files

        if readReadme:
            # Read the title from the README file if you specified the option...
            title = _readReadme(f)
        else:
            # ...or use the default title
            title = config['prefixTitle']
            
        # Retrieve data and metadata
        metadata, data = _readData(f, config['cols'])

        # Retrieve the X label
        xlabel = metadata[config['cols'][0]]

        # Retrieve the Y label or the labels for each columns
        labels = []
        if len(data) > 2:
            for c in config['cols'][1:]:
                labels.append(metadata[c])
            ylabel = 'Generic'
        else:
            ylabel = metadata[config['cols'][1]]
            pass

        print('xlabel:',xlabel)
        print('ylabel:',ylabel)
        print('labels:',labels)
        print('title:',title)
        print(data)

        _makeGraph(axs[k], title, ylabel, xlabel, data, labels, len(axs))
        k += 1
    plt.show()


def _makeGraph(ax, title, ylabel, xlabel, data, labels, ngraph):
    """Create each subplot graph
    
    Input:
    @ax      obj   subplot
    @title   str   graph title
    @ylabel  str   label for the y axis
    @xlabel  str   label for the x axis
    @labels  list  labels for each set of data
    @ngraph  int   total number of subplots (to set some visual properties)
    
    Return:
    Nothing, all the edits will be enclose in the ax object

    Depends:
    * matplotlib
    """
    
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)

    if len(data) == 2:
        if len(labels) > 0:
            ax.plot(data[0], data[1], label=labels[0])
            ax.legend(loc=config['legendLoc'])
        else:
            ax.plot(data[0], data[1])
    else:
        for i, c in enumerate(data[1:]):
            try: 
                labels[i]
            except IndexError:
                labels.append('NotFound')
            ax.plot(data[0], data[i+1], label=labels[i])
                
        ax.legend(loc=config['legendLoc'])

    yt = ax.get_yticks()
    # print('yt_i:',yt)
    # print('#yt_i:',len(yt))
    ntic = _logicFunctionTicks(ngraph, len(yt), config['noYticks'])
    yt = yt[::ntic]
    # print('yt_fact',ntic)
    # print('#yt_f:',len(yt))
    ax.set_yticks(yt,minor=False)

def _logicFunctionTicks(x,L,n):
    """Sigmoid function 1 -> L-1

    Input:
    @x   int/flt  independent variable 
    @L   int/flt  maximum value of the function +1
    @n   int/flt  if x > n the value is L - 1

    Return:
    @ int  value of the function

    Depends:
    * math
    """
    import math

    x = float(x)/float(config['ncols'])
    print('x:',x)
    L = float(L-2)
    n = float(n)

    # Definition of B
    n = math.log(2.0 * L)
    d = math.log(1. / (2. * L))
    B = n/d
    
    # Definition of A
    A = math.log(4.*L**2)

    # Definition of k
    k = A / (n - 1)

    # Definition of x0
    n = (1 - (B * n))
    d = 1 - B
    x0 = n/d

    sig = L / (1. + math.exp(-k * (x - x0))) + 1
    
    sig = round(sig)

    return int(sig)

def _readReadme(filename):
    """Read the README file, if exist, in the same directory as
    the data file. The number of line readed is hardly implemented 
    in the config dict.
    
    Input:
    @filename  str  name of the data file
    
    Return:
    @ str  Title of the graph deduced join the first 3 lines of the filename

    Depends:
    * os
    * sys
    """

    # Find the path to the README and check if it exists
    folder = os.path.dirname(os.path.realpath(filename))
    filename = os.path.join(folder,'README')
    if not os.path.isfile(filename):
        sys.stderr.write('WARNING: README file not found in '+folder+'\n')
        return
    
    # Read the first "config[nlinesReadme]" lines
    k = 0
    title = ''
    fc = open(filename,'r').readlines()
    while k < config['nlinesReadme']:
        try:                    # If the file is shorter than three line just exit the loop
            if fc[k] != '#':
                title += fc[k]
                k += 1
        except:
            break

    return title.replace('\n',' ')
                

def _readData(filename, columns):
    """Read the given columns from the data file
    
    Input:
    @filename  str   name of the file containing the data
    @columns   list  list of columns that have to be stored

    Return:
    @ dict  containing a label for the columns if specified in the filename
            (see the example)
    @ array with all the data readed

    Depends:
    * numpy as np
    *
    """
    metadata = {}
    
    # To retrieve metadata the datafile should contains something of this form:
    # <number of column(>0)> --> <title_of_column(no spaces)>
    with open(filename,'r') as fp:
        for l in fp:
            if l[0] == '#':
                if l.find('-->') >= 0:
                    ws = l.split()
                    splitidx = ws.index('-->')
                    try:
                        # Assign the metadata in a dict where the key is the column position starting at 0
                        # this is the second "-1" in the expression below
                        metadata[int(ws[splitidx-1])-1] = ws[splitidx+1]
                    except ValueError as e:
                        sys.stderr.write('WARNING: The head section must contain:\n<column> --> <what is in the colum>\nwhere column must be an integer')
                        sys.stderr.write(e)
                        

    data = np.loadtxt(filename, usecols=columns)
    return metadata, data.T

def _subplotgenerator(n):
    """Check the number of files and generate the subplot grid
    
    Input:
    @n  int  number of columns in the grid

    Return:
    @ obj   figure object of matplotlib
    @ list  of the ax object from matplotlib

    Depends:
    * matplotlib
    * math
    """
    import math
    # Compute the number of needed rows
    nrows = int(math.ceil(n/float(config['ncols'])))

    # Generate the matplotlib objs
    f, axs = plt.subplots(nrows, config['ncols'], sharex='col')

    return f, axs.ravel()

def _parseColumns(columns):
    import re
    tmp = []
    if type(columns) == str: columns = columns.split()
    colRange = re.compile('(\d+)-(\d+)')
    for c in columns:
        if colRange.match(c):
            tmp = tmp + range(int(colRange.match(c).group(1)), int(colRange.match(c).group(2))+1)
        else:
            tmp.append(int(c))
    
    return map(lambda x: x-1, tmp) # To use column indexes starting from 1 instrad of 0


def _parseRange(rangel, lims):
    for i in xrange(2):
        if rangel[i] == ':':
            rangel[i] = lims[i]
        else:
            rangel[i] = float(rangel[i])

    print(rangel)
    return rangel

def _parser():
    import argparse
    parser = argparse.ArgumentParser(version='%prog 0.1',
                                     description='Compare a lot of graphs')

    parser.add_argument('filenames',
                        action = 'store',
                        metavar = '<REGEX>',
                        nargs = '+',
                        help = 'regex identifing the files you want to graph')

    parser.add_argument('-r', '--readme',
                        action = 'store_true',
                        dest = 'readReadme',
                        default = 'False',
                        help = 'check and read the README file to create the graph title')

    parser.add_argument('-nc', '--number-of-columns',
                        action = 'store',
                        dest = 'ncols',
                        default = config['ncols'],
                        type = int,
                        help = 'number of graph in each row')

    parser.add_argument('-c', '--columns',
                        action = 'store',
                        dest = 'columns',
                        type = str,
                        nargs = '*',
                        metavar = 'col',
                        default = config['cols'],
                        help = 'columns to build the graph (starting from 1)')

    parser.add_argument('-xr', '--xrange',
                        action = 'store',
                        dest = 'xrange',
                        nargs = 2,
                        help = 'set the x range (: for nothing)')

    parser.add_argument('-yr', '--yrange',
                        action = 'store',
                        dest = 'yrange',
                        nargs = 2,
                        help = 'set the y range (: for nothing)')


    return parser.parse_args()


if __name__ == '__main__':
    main()
