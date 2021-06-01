#!/usr/bin/env python3
import sys,os
import networkx as nx
import json
import argparse
from numpy import array
from scipy.sparse import csc_matrix
from scipy.sparse.linalg import expm, expm_multiply

def edges2nx(edges,attr_label='label',src_col=1,tgt_col=2):
	if isinstance(edges,str):
		try:
			with open(edges) as inpf:
				edges=[line.split()[src_col-1:tgt_col] for line in inpf]
		except IOError as e:
			if not os.path.isfile(heatf): sys.exit("ERROR! Couldn't locate '{}'.".format(heatf))
			else: sys.exit("ERROR! Couldn't open '{}'".format(heatf))
	G = nx.Graph()
	G.add_edges_from(edges)
	G.add_nodes_from(set((node for edge in edges for node in edge)))
	for node in G.nodes:  G.nodes[node][attr_label]=node
	return G

def heat_diffusion(network, input_key, output_key, normalize_laplacian, time):
	matrix = create_sparse_matrix(network, normalize_laplacian)
	heat_array = find_heat(network, input_key)
	diffused_heat_array = diffuse(matrix, heat_array, time)
	#print(diffused_heat_array,file=sys.stderr)
	network = add_heat(network, output_key, diffused_heat_array)
	return network

def diffuse(matrix, heat_array, time):
	return expm_multiply(-matrix, heat_array, start=0, stop=time, endpoint=True)[-1]

def create_sparse_matrix(network, normalize=False):
	if normalize:
		return csc_matrix(nx.normalized_laplacian_matrix(network))
	else:
		return csc_matrix(nx.laplacian_matrix(network))

def find_heat(network, heat_key):
	heat_list = []
	found_heat = False
	for node_id in network.nodes():
		if heat_key in network.nodes[node_id]:
			found_heat = True
		heat_list.append(network.nodes[node_id].get(heat_key, 0))
	if not found_heat:
		raise Exception('No input heat found')
	return array(heat_list,dtype=float)

def add_heat(network, output_key, heat_array):
	node_heat = {node_id: heat_array[i] for i, node_id in enumerate(network.nodes())}
	sorted_nodes = sorted(node_heat.items(), key=lambda x:x[1], reverse=True)
	node_rank = {node_id: i for i, (node_id, _) in enumerate(sorted_nodes)}
	nx.set_node_attributes(network, node_heat, output_key+'_heat')
	nx.set_node_attributes(network, node_rank, output_key+'_rank')
	return network

#Setting command-line args
hdargs=argparse.ArgumentParser(prog=os.path.basename(sys.argv[0]), description="Apply a network propagation algorythm based on heat diffusion. Network files must have an edge-list format (two columns of interacting nodes). Heat values should be input as a TSV file indicating the initial node and their corresponding heat value.",add_help=True)
hdargs.add_argument('input_network',help="Network as a two-column list of interacting nodes.")
hdargs.add_argument('heated_nodes',help='Nodes from which start the propagation and their initial heat value (from zero to one). Nodes of the network not found here will be assigned a value of zero.')
hdargs.add_argument('-t','--time',default=0.1,type=float, help='The upper bound on the exponential multiplication performed by diffusion.')
#-n is False unless used as option
hdargs.add_argument('-n','--normalize',action='store_true',default=False, help='Create a normalized laplacian matrix for diffusion (default: False)')
hdargs.add_argument('-o','--output_file',help='Use this file instead of the default for saving results.')
args=hdargs.parse_args()

#The names for these attributes in the network.
ian,oan='diffusion_input','diffusion_output'

#Checking output_file and creating default filename if needed
if args.output_file is None:
	norm='_normalized' if args.normalize else ''
	resultsfile='heatd_t{}{}_{}'.format(args.time,norm,os.path.basename(args.input_network))
	args.output_file=os.path.join(os.path.dirname(args.input_network),resultsfile)
elif os.path.isdir(args.output_file):sys.exit("ERROR! Can't use a directory for saving results")
elif not os.path.dirname(args.output_file)=='' and not os.path.isdir(os.path.dirname(args.output_file)):
	sys.exit("ERROR! Couldn't locate folder '{}'".format(os.path.dirname(args.output_file)))

#Load input network and heated nodes
network=edges2nx(args.input_network)
heat=[]
try:
	with open(args.heated_nodes) as inpf:
		for line in inpf:
			if len(line.split())>=2:heat.append(line.split()[:2])
			else: heat.append([line.split()[0],1])
except IOError as e:
	if not os.path.isfile(args.heated_nodes):sys.exit("ERROR! Couldn't locate '{}'".format(args.heated_nodes))
	else: sys.exit("ERROR! Couldn't open '{}'".format(args.heated_nodes))

#Checking that heated nodes are in network and setting the value for ian  
heat=dict(heat)
nodes=set(network.nodes())
notin=set(heat.keys()).difference(nodes)
if not any([k in nodes for k in heat.keys()]):
	sys.exit("ERROR! Not found any of the heated nodes in the network.")
elif len(notin)>0:
	print("WARNING! Some nodes NOT found in the input network:\n"+";".join(notin), file=sys.stderr)
for node in nodes:
	network.nodes()[node][ian]=heat[node] if node in heat else 0

#Diffusion
diffusedNetwork = heat_diffusion(network,ian,oan,args.normalize, args.time)

#heatf='\t'.join(['{:.7g}','{:.7g}','{.f}'])
#outcols=[labelcol,ian,oan+"_heat",oan+"_rank"]
#Saving results
outcols=[ian,oan+"_heat"]
print("Saving results into '{}'".format(args.output_file))
with open(args.output_file,'w') as outf:
	for node,attribs in diffusedNetwork.nodes(data=True):
		print(node,*[attribs[col] for col in outcols],sep='\t',file=outf)

