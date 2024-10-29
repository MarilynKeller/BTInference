# Copyright (C) 2024  MPI IS, Marilyn Keller
import argparse
import os
from aitviewer.models.smpl import SMPLLayer
import numpy as np
import torch

from aitviewer.viewer import Viewer
from aitviewer.renderables.skel import SKELSequence
from aitviewer.renderables.smpl import SMPLSequence
from aitviewer.configuration import CONFIG as C
from skel.skel_model import SKEL


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='Visualize a SKEL sequence.')
    
    parser.add_argument('exp_file', type=str, help='Path to the SKEL sequence to visualize.')
    parser.add_argument('--smpl_meshes', action='store_true', help='Export the SMPL sequence as meshes.')
    parser.add_argument('--skel_meshes', action='store_true', help='Export the SKEL sequence as meshes.')

    parser.add_argument('--fps', type=int, help='Fps of the sequence', default=30)
    parser.add_argument('--zu', help='Use Z-up coordinate system. \
        This is usefull for vizualizing sequences of AMASS that are 90 degree rotated', action='store_true')
    parser.add_argument('-g', '--gender', type=str, default=None, help='Forces the gender for visualization. By default, the code tries to load the gender from the skel file')
    parser.add_argument('--zd', help='Use Z-down coordinate system. \
        This is usefull for vizualizing sequences from EMDB that are 90 degree rotated', action='store_true')
    
    
    parser.add_argument('-e', '--export_mesh', type=str, help='Export the mesh of the skel model to this folder', default=None)
    parser.add_argument('--offset', help='Offset the SMPL model to display it beside SKEL.', action='store_true') 
                  
    args = parser.parse_args()
    
    smpl_file = os.path.join('output', args.exp_file, 'smpl_seq.npz')
    skel_file = os.path.join('output', args.exp_file, 'skel_seq.pkl')
    meshes_folder = os.path.join('output', args.exp_file, 'meshes')
    os.makedirs(meshes_folder, exist_ok=True)
    
    to_display = []
    
    fps_in = args.fps # Fps of the sequence
    fps_out = 30 # Fps at which the sequence will be played back
    # The skeleton mesh has a lot of vertices, so we don't load all the frames to avoid memory issues
    assert os.path.exists(smpl_file), f"SMPL file {smpl_file} does not exist."
    if args.offset:
        translation = np.array([-1.0, 0.0, 0.0])
    else:
        translation = None
        
    # Fetch the gender from the smpl file
    gender = np.load(smpl_file)["gender"].item()
    smpl_layer = SMPLLayer(model_type="smpl", gender=gender)
    smpl_seq = SMPLSequence.from_npz(
                    file=smpl_file,
                    smpl_layer = smpl_layer,
                    # fps_out=fps_out,
                    name="SMPL",
                    show_joint_angles=True,
                    position=translation,
                    z_up=args.zu,
                    z_down=args.zd
                    )   
    to_display.append(smpl_seq)
    
    if args.smpl_meshes:
        os.makedirs(os.path.join(meshes_folder, 'SMPL'), exist_ok=True)
        smpl_seq.export_meshes(os.path.join(meshes_folder, 'SMPL'))
        
    if os.path.exists(skel_file):
        skel_seq = SKELSequence.from_file(skel_seq_file = skel_file, 
                                        poses_type='skel', 
                                        fps_in=fps_in,
                                        fps_out=fps_out,
                                        is_rigged=True, 
                                        show_joint_angles=True, 
                                        name='SKEL', 
                                        z_up=args.zu,
                                        z_down=args.zd)
        to_display.append(skel_seq)
        
        if  args.skel_meshes:
            os.makedirs(os.path.join(meshes_folder, 'SKEL'), exist_ok=True)
            skel_seq.export_meshes(os.path.join(meshes_folder, 'SKEL'))

    v = Viewer()
    v.playback_fps = fps_out
    v.scene.add(*to_display)
    v.scene.camera.position = np.array([-5, 1.7, 0.0])
    v.lock_to_node(smpl_seq, (2, 0.7, 2), smooth_sigma=5.0)
    
    v.run_animations = True 
    v.run()
