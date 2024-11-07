"""Given a SMPL parameters, infer the tissues occupancy"""

import argparse
import os
import pickle
import time
import torch
import tqdm
import trimesh

from hit.utils.model import HitLoader
from hit.utils.data import load_smpl_data
import hit.hit_config as cg

def main():
    
    parser = argparse.ArgumentParser(description='Infer tissues from SMPL parameters')
    
    # parser.add_argument('--exp_name', type=str, default='rel_male',
    #                     help='Name of the checkpoint experiment to use for inference' 
    #                     ) #TODO change to checkpoint path
    parser.add_argument('--target_seq', type=str, default='/home/mkeller2/data2/Code/SMPL_fit_video/thesis_seq/output/P8_69_outdoor_cartwheel/smpl_seq.pkl', 
                        help='Path to the SMPL file to infer tissues from')
    parser.add_argument('--out_folder', type=str, default='output',
                        help='Output folder to save the generated meshes')
    parser.add_argument('--device', type=str, default='cuda:0', choices=['cuda:0', 'cpu'],
                        help='Device to use for inference')
    parser.add_argument('--ckpt_choice', type=str, default='best', choices=['best', 'last'],
                        help='Which checkpoint to use for inference')
    parser.add_argument('--mise_resolution0', type=int, default=128, help='Resolution of the Mise grid level 0 to extract the mesh')
    parser.add_argument('--mise_depth', type=int, default=3, help='Depth of the Mise grid to extract the mesh')
    parser.add_argument('--max_queries', type=int, default=4000000, help='Maximum number of queries for Mise. Try to lower this number if you run out of memory. Increase for faster mesh extraction')
    parser.add_argument('--encoding', type=str, default='binary', choices=['ascii', 'binary'],
                        help='Encoding to use for the output mesh files')
    
    args = parser.parse_args()

    target_seq = args.target_seq
    ckpt_choice = args.ckpt_choice
    device = torch.device(args.device)
    
    subj_name = os.path.dirname(target_seq).split('/')[-1]
    out_folder = os.path.join('output', subj_name, 'hit')
    os.makedirs(out_folder, exist_ok=True)


    
    smpl_data = pickle.load(open(target_seq, 'rb'))
    # dict_keys(['poses', 'betas', 'trans', 'poses_body', 'poses_root', 'gender'])
    smpl_seq = {}
    smpl_seq['global_orient'] = smpl_data['poses_root']
    smpl_seq['body_pose'] = smpl_data['poses_body']
    smpl_seq['betas'] = smpl_data['betas']
    smpl_seq['transl']  = smpl_data['trans']
    n_frame = smpl_seq['global_orient'].shape[0]
    
    to_tensor = lambda x: torch.tensor(x, dtype=torch.float32).to(device)
    smpl_seq = {key: to_tensor(val) for key, val in smpl_seq.items()}
    
    
    # data['body_pose'] = torch.zeros(1, 69).to(device) # Per joint rotation of the body (21 joints x 3 axis)
    # data['betas'] = torch.zeros(1, 10).to(device) # Shape parameters, values should be between -2 and 2
    # # data['betas'][0,0] = args.betas[0]
    # # data['betas'][0,1] = args.betas[1]
    # data['transl'] = torch.zeros(1, 3).to(device)
    
    # # Create a data dictionary containing the SMPL parameters 
    # smpl_seq = {}
    # smpl_seq['global_orient'] = torch.zeros(1, 3).to(device) # Global orientation of the body
    # smpl_seq['body_pose'] = torch.zeros(1, 69).to(device) # Per joint rotation of the body (21 joints x 3 axis)
    # smpl_seq['betas'] = torch.zeros(1, 10).to(device) # Shape parameters, values should be between -2 and 2
    # smpl_seq['betas'][0,0] = args.betas[0]
    # smpl_seq['betas'][0,1] = args.betas[1]
    # smpl_seq['transl'] = torch.zeros(1, 3).to(device) # 3D ranslation of the body in meters

    # Create output folder
    os.makedirs(out_folder, exist_ok=True)
    
    # Load HIT model
    
    # Select the pre-trained model
    if smpl_data['gender'] == 'female':
        model_name = 'hit_female'
    elif smpl_data['gender'] == 'male':
        model_name = 'hit_male'
    else:
        raise NotImplementedError(f"Gender '{smpl_data['gender']}' not implemented.")
    
    hl = HitLoader.from_expname(model_name, ckpt_choice=ckpt_choice)
    hl.load()
    hl.hit_model.apply_compression = False

    # Run smpl forward pass to get the SMPL mesh
    betas = smpl_seq['betas']
    body_pose = smpl_seq['body_pose'][0:1]
    global_orient = smpl_seq['global_orient'][0:1]
    transl = smpl_seq['transl'][0:1]
    
    smpl_output_xpose = hl.smpl.forward(betas=betas, body_pose=hl.smpl.x_cano().to(betas.device), global_orient=None, transl=None)  
        
    # smpl shaped and posed
   
    # tfs = smpl_output.tfs 
    # import ipdb; ipdb.set_trace()
    # For each tissue
    for ci, c_label in enumerate(hl.cfg.train_cfg.mri_labels):
        os.makedirs(os.path.join(out_folder, c_label), exist_ok=True)
        if c_label != 'NO':
            
            if c_label != 'BONE':
                continue
            
            # Extract the shaped mesh
            print(f"Extracting {c_label} canonical mesh...")
            hl.hit_model.train_cfg.max_queries = args.max_queries
            t_start = time.perf_counter()
            mesh_s = hl.hit_model.extract_mesh(smpl_output_xpose, channel=ci, grid_res=64, 
                                    use_mise=True, mise_resolution0=args.mise_resolution0,
                                    mise_depth=args.mise_depth, batch=None, 
                                    template=False, 
                                    unposed = True, # The compression should be applied after posing
                                    color_mode='compression')[0]
            print(f"Extracted {c_label} mesh in {time.perf_counter()-t_start:.2f}s")
            mesh_s.export(os.path.join(out_folder, f'{c_label}_canonical.ply'), encoding=args.encoding)
            
            for i in tqdm.tqdm(range(n_frame)):
            # for i in tqdm.tqdm(range(3)):
                # import ipdb; ipdb.set_trace()
                smpl_output = hl.smpl.forward(betas=betas, 
                                              body_pose=smpl_seq['body_pose'][i:i+1], 
                                              global_orient=smpl_seq['global_orient'][i:i+1], 
                                              transl=smpl_seq['transl'][i:i+1])
                mesh_p = hl.hit_model.pose_unposed_tissue_mesh(mesh_s, smpl_output) #trimesh
                
                mesh_p.export(os.path.join(out_folder, c_label, f'{c_label}_{i}.ply'))
                print(f"Exported {c_label}_{i}.ply")

if __name__ == "__main__":
    main()
    