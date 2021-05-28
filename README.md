# simple-HeatDiffusion

Application of a network propagation algorythm based on heat diffusion.

The implementation of the algorythm is the same of the [_Diffusion_ plugin for Cytoscape](http://apps.cytoscape.org/apps/diffusion). Functions for calculating the heat propagation are taken from [the code](https://github.com/idekerlab/heat-diffusion/blob/master/heat_diffusion_service.py) that runs behind that plugin.

Network files used as input must have an edge-list format (two columns of interacting nodes). Heat values should be input in a separate TSV file indicating the node and their corresponding heat value. The output is a list of the nodes of the network and their heat values after propagation. The results of the propagation will depend on the topology of the network, the initial heat of the nodes and the time value (default: _0.1_) set for the propagation. See _**Usage**_ section for more information.

## Requirements

The number indicate the version used for running the examples in the _Usage_ section.

 - python (3.8)
     - networkx (2.5)
     - numpy (1.20)
     - scipy (1.6)

## Usage

The script expects at least two files: one with the interacting nodes of a network and another with the nodes and their initial heat.
                             
`python3 heat_diffusion.py network_edges heated_nodes`
 

Heat values must range from zero to one. Nodes not included in _heated_nodes_ will be assigned a value of zero. The result is a file including all the nodes of the network with their heat value before and after propagation. By default this file is saved in the same folder as the _network_edges_ file used. 
By default it is used a time value of _0.1_ for the propagation.

_Ex:_
```python
python3 heat_diffusion.py test_files/galFiltered_edges test_files/galFiltered_heat
```
 
 Use  _-t_  option to modify the value of propagation time and  _-o_  option to indicate a specific file for saving the results.

_Ex:_
```python
python3 heat_diffusion.py -t 0.005 test_files/galFiltered_edges test_files/galFiltered_heat -o heat_galFiltered_t005.tsv
```

## References
- https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1005598 (Implementation of heat-diffusion algorythm)
- https://github.com/idekerlab/heat-diffusion/blob/master/heat_diffusion_service.py (Code of the Cytoscape plugin) 
