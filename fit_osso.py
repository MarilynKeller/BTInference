import pickle
from osso.utils.fit_osso import fit_osso


if __name__ == "__main__":
    import argparse
    import os
    import shutil
    import json
    import numpy as np

    argparser = argparse.ArgumentParser()
    
    parser = argparse.ArgumentParser(description='Fit the OSSO model to a sequence of SMPL parameters')
    parser.add_argument('--exp_name', type=str, help='Name of the sequence', default='P8_69_outdoor_cartwheel')
    parser.add_argument('-o', '--out_dir', type=str, help='Output directory', default='output')
    parser.add_argument('-D', '--display', help='Display the fitting process', action='store_true')
    
    args = parser.parse_args()
    
    smpl_pkl = os.path.join('output', args.exp_name, 'smpl_seq.pkl')
    output_folder = os.path.join(args.out_dir, args.exp_name, 'osso')
    
    smpl_data = pickle.load(open(smpl_pkl, 'rb'))

    fit_osso(smpl_data, output_folder, display=args.display)