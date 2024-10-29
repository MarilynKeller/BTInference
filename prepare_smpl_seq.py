import argparse
import json
import os
import pickle
import shutil

import numpy as np
import torch

easymocap_root = '/home/mkeller2/data2/Code/SMPL_fit_video/EasyMocap/output'
emdb_root = '/home/mkeller2/data2/Dropbox/MPI/TML/submission_video/EMDB'

def load_from_emdb(gender, exp_name="P8_69_outdoor_cartwheel", root=emdb_root):
    print("Loading from EMDB")
    smpl_file = os.path.join(root, exp_name + "_params.npz")
    smpl_data = np.load(smpl_file)
    """ ['body_pose', 'global_orient', 'betas', 'transl', 'gender']"""
    smpl_seq = {'poses': np.concatenate([smpl_data['global_orient'], smpl_data['body_pose']], axis=1), 
                'betas': cure_betas(smpl_data['betas']),
                'trans': smpl_data['transl'],
                'poses_body': smpl_data['body_pose'], 
                'poses_root': smpl_data['global_orient'],
                'gender': gender}
    return smpl_seq
    
def cure_betas(betas_in):
    """ Cure the betas by averaging them if they vary over the sequence"""
    # Check that the betas do not vary 
    if np.all(betas_in == betas_in[0]):
        betas = betas_in[0:1] # 1xF array
    else:
        #Compute the per beta variance 
        betas_var = np.var(betas_in, axis=0)
        print(f"WARNING: Betas vary over the sequence with variance {betas_var}. Keeping the average beta.")
        betas = np.mean(betas_in, axis=0, keepdims=True) 
    return betas

def load_from_easymocap(gender, exp_name="test5", root=easymocap_root):
    print("Loading from easymocap")
    smpl_data_folder = os.path.join(root, exp_name, "smpl")
    
    # This folder contains a json file for each frame of the sequence, make a loop to agregate them in a single dict
    #     [
    #     {
    #         "id": 0,
    #         "Rh": [
    #           [2.858, -0.133, -0.831]
    #         ],
    #         "Th": [
    #           [-0.122, -0.081, 2.665]
    #         ],
    #         "poses": [
    #           [-0.006, 0.241, 0.849, -0.918, -0.311, -0.781, 0.364, -0.019, 0.015, 0.347, -0.419, -0.078, 1.177, -0.135, 0.315, 0.116, 0.194, -0.151, 0.239, 0.270, -0.570, 0.053, -0.345, 0.424, -0.012, 0.067, -0.077, -0.271, 0.005, 0.656, -0.155, 0.141, -0.567, -0.090, -0.391, -0.133, -0.064, 0.126, -0.150, -0.009, 0.156, 0.077, 0.080, -0.502, 0.114, -0.140, 0.017, -0.064, -0.350, -0.131, -0.297, -0.569, -0.490, -0.088, -0.620, 0.270, 0.211, -0.448, -0.074, -0.039, 0.092, 0.035, 0.057, -0.100, 0.010, -0.076, -0.148, 0.018, 0.069]
    #         ],
    #         "shapes": [
    #           [0.482, 0.506, -0.510, 0.499, -0.347, 0.001, 0.000, 0.400, -0.005, 0.252]
    #         ]
    #     }
    # ]
    # I want poses = poses, betas = shapes, trans = Th, gender = gender
    # The files are sorted by name.

    smpl_seq = {'poses': [], 'betas':[], 'trans':[], 'poses_body':[], 'poses_root':[]}

    for file in sorted(os.listdir(smpl_data_folder)):
        json_data = json.load(open(os.path.join(smpl_data_folder, file)))[0]
        poses_full = json_data['Rh'][0] + json_data['poses'][0]
        smpl_seq['poses'].append(poses_full)
        smpl_seq['betas'].append(cure_betas(json_data['shapes'][0]))
        smpl_seq['trans'].append(json_data['Th'][0])
        
        smpl_seq['poses_body'].append(json_data['poses'][0])
        smpl_seq['poses_root'].append(json_data['Rh'][0])
        
    smpl_seq = {key: np.array(val) for key, val in smpl_seq.items() if isinstance(val, list)}
    
    # Check that the betas do not vary 
    if np.all(smpl_seq['betas'] == smpl_seq['betas'][0]):
        smpl_seq['betas'] = smpl_seq['betas'][0:1] # 1xF array
    else:
        #Compute the per beta variance 
        betas_var = np.var(smpl_seq['betas'], axis=0)
        print(f"WARNING: Betas vary over the sequence with variance {betas_var}. Keeping the average beta.")
        smpl_seq['betas'] = np.mean(smpl_seq['betas'], axis=0, keepdims=True)    
    
    smpl_seq['gender']=gender

    return smpl_seq

if __name__ == "__main__":
    
    argparser = argparse.ArgumentParser()
    
    parser = argparse.ArgumentParser(description='Load and save a sequence from EasyMocap')
    parser.add_argument('--gender', type=str, help='Gender of the subject', choices=['female', 'male'], default='female')
    parser.add_argument('--exp_name', type=str, help='Name of the experiment', default='test5')
    # parser.add_argument('--root', type=str, help='Root directory of the experiment', default='/home/mkeller2/data2/Code/SMPL_fit_video/EasyMocap/output')
    parser.add_argument('--fps', type=int, help='Fps of the sequence', default=60)
    parser.add_argument('--del_trans', action='store_true', help='Delete the translation from the sequence')
    parser.add_argument('--source', type=str, help='Source of the data, needed for processing', default='easymocap', choices=['easymocap', 'emdb'])
    args = parser.parse_args()
    
    if args.source == 'easymocap':
        smpl_seq = load_from_easymocap(args.gender, args.exp_name)
        video_path = os.path.join(easymocap_root, args.exp_name, 'render.mp4')
        # copy video locally
        shutil.copy(video_path, os.path.join('output', args.exp_name, 'video_smpl.mp4'))
    elif args.source == 'emdb':
        smpl_seq = load_from_emdb(args.gender, args.exp_name)
        video_path = os.path.join(emdb_root, args.exp_name + "_org.mp4")
        shutil.copy(video_path, os.path.join('output', args.exp_name, 'video.mp4'))
        smpl_video_path = os.path.join(emdb_root, args.exp_name + "_smpl.mp4")
        shutil.copy(smpl_video_path, os.path.join('output', args.exp_name, 'video_smpl.mp4'))

    if args.del_trans:
        smpl_seq['trans'] = 0* smpl_seq['trans']
        
    # Embed the verts and faces for OSSO
    from aitviewer.models.smpl import SMPLLayer
    smpl_layer = SMPLLayer(model_type="smpl", gender=args.gender)
    # import ipdb; ipdb.set_trace()
    # Set the parameters and fetch the vertices 
    to_torch = lambda x: torch.tensor(x, dtype=torch.float32).to('cpu')
    betas = to_torch(smpl_seq['betas'])
    poses = to_torch(smpl_seq['poses'])
    trans = to_torch(smpl_seq['trans'])
    vertices, joints = smpl_layer.fk(betas=betas, poses_body=poses[:,3:], poses_root=poses[:,:3], trans=trans)
    vertices = vertices.cpu().numpy()
    joints = joints.cpu().numpy()
    faces = smpl_layer.faces.cpu().numpy()
    smpl_seq['verts'] = vertices
    smpl_seq['joints'] = joints
    smpl_seq['faces'] = smpl_layer.faces.cpu().numpy()
  
    print(f"Loaded sequence with {smpl_seq['poses'].shape[0]} frames")
    
    outfile = os.path.join('output', args.exp_name, "smpl_seq.pkl")
    os.makedirs(os.path.dirname(outfile), exist_ok=True)
    pickle.dump(smpl_seq, open(outfile, 'wb'))
    
    smpl_seq['mocap_framerate'] = args.fps
    np.savez(outfile.replace('.pkl', '.npz'), **smpl_seq) # Save as npz for compatibility with AMASS
    
    print(f"Saved sequence to {outfile}")