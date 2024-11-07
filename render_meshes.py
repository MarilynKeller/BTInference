import os
import bpy
import math
import sys

def load_mesh(mesh_filename):
    
    assert os.path.exists(mesh_filename), f'Mesh file {mesh_filename} does not exist'
    
    # Check blender version 
    if bpy.app.version[0] < 4:
        if mesh_filename.endswith('.ply'):
            bpy.ops.import_mesh.ply(filepath=mesh_filename)
        elif mesh_filename.endswith('.obj'):
            bpy.ops.import_scene.obj(filepath=mesh_filename)
        else:
            raise NotImplementedError(f"Mesh format {mesh_filename} not implemented")
    else:
        # bpy.ops.wm.ply_import
        if mesh_filename.endswith('.ply'):
            bpy.ops.wm.ply_import(filepath=mesh_filename)
        elif mesh_filename.endswith('.obj'):
            bpy.ops.wm.obj_import(filepath=mesh_filename)
        else:
            raise NotImplementedError(f"Mesh format {mesh_filename} not implemented")

# def instanciate_mesh(mesh_filename, mat_name):
    
#     assert os.path.exists(mesh_filename), f'Mesh file {mesh_filename} does not exist'
    
#     bpy.ops.object.select_all(action='DESELECT')

#     print(f'Loading mesh {mesh_filename} with mat_name {mat_name}')
#     # bpy.ops.import_scene.obj(filepath=mesh_filename)
#     #import ply
#     load_mesh(mesh_filename)
    
#     print(f'Mesh loaded{mesh_filename} {len(bpy.context.selected_objects)}')
#     my_obj = bpy.context.selected_objects[0]
# #        bpy.context.scene.objects.active = bpy.context.selected_objects[0]
# #        object = bpy.context.active_object
#     my_obj.select_set(True)
#     # object_list.append(my_obj) # Keep q reference to this object in the list to be able to delete it later
#     bpy.ops.transform.rotate(value=math.pi/2, orient_axis='X')

#     #put in proper collections
#     #bpy.data.collections['bone'].object_list.link(bone)
#     #bpy.data.collections['body'].object_list.link(body)

#     # Set materials
#     # Get mat_name
#     # bone_mat = bpy.data.materials.get("bone")
#     mat = bpy.data.materials.get(mat_name)
#     # Assign it to object
#     if my_obj.data.materials:
#         # assign to 1st mat_name slot
#         my_obj.data.materials[0] = mat
#     else:
#         # no slots
#         my_obj.data.materials.append(mat)
        
#     # smooth the mesh
#     bpy.ops.object.shade_smooth()
#     return my_obj

        

def render_meshes(mesh_mat, render_file):
    """
    Render a list of meshes with the corresponding materials
    params:
    mesh_mat: list of tuples (mesh_filename, mat_name)
    render_file: output file
    
    """
    object_list = []
    

    for mesh_filename, mat_name in mesh_mat:
        
        bpy.ops.object.select_all(action='DESELECT')

        print(f'Loading mesh {mesh_filename} with mat_name {mat_name}')

        #import bone
        #bpy.ops.import_mesh.ply(filepath=bone_file)
        #bone = bpy.context.activxe_object
        ##bpy.ops.transform.resize(value=(0.001, 0.001, 0.001), constraint_axis=(False, False, False))
        #bpy.ops.transform.rotate(value=-90.0, orient_axis='X')

        #import mesh
        # bpy.ops.import_mesh.ply(filepath=mesh_filename)
        
        # bpy.ops.import_scene.obj(filepath=mesh_filename)
        load_mesh(mesh_filename)
        print(f'Mesh loaded{mesh_filename} {len(bpy.context.selected_objects)}')
        my_obj = bpy.context.selected_objects[0]
#        bpy.context.scene.objects.active = bpy.context.selected_objects[0]
#        object = bpy.context.active_object
        my_obj.select_set(True)
        object_list.append(my_obj) # Keep q reference to this object in the list to be able to delete it later
        # bpy.ops.transform.rotate(value=math.pi, orient_axis='Y')
        bpy.ops.transform.rotate(value=math.pi, orient_axis='Z')
        bpy.ops.transform.rotate(value=-1/2*math.pi, orient_axis='X')

        #put in proper collections
        #bpy.data.collections['bone'].object_list.link(bone)
        #bpy.data.collections['body'].object_list.link(body)

        # Set materials
        # Get mat_name
        # bone_mat = bpy.data.materials.get("bone")
        mat = bpy.data.materials.get(mat_name)
        # Assign it to object
        if my_obj.data.materials:
            # assign to 1st mat_name slot
            my_obj.data.materials[0] = mat
        else:
            # no slots
            my_obj.data.materials.append(mat)
            
        # smooth the mesh
        bpy.ops.object.shade_smooth()
        bpy.ops.object.select_all(action='DESELECT')
        
    if not skip_render:

        # render
        bpy.context.scene.render.filepath = render_file
        bpy.ops.render.render(write_still = True)

    if not skip_delete:

        # remo0ve object_list
        for my_obj in object_list:
            my_obj.select_set(True)
            bpy.ops.object.delete() 
            
        # Ensure mesh data is removed from memory
#        if my_obj.type == 'MESH':
#            # Remove the mesh data block if it exists
#            mesh_data = my_obj.data
#            if mesh_data:
#                bpy.data.meshes.remove(mesh_data, do_unlink=True)

def get_mesh_path(name, frame_i, exp_name, root):
    
    assert os.path.exists(root), f'Folder {root} contaning the meshes does not exist'
    assert name in ['skel_skel', 'skel_skin', 'smpl', 'osso', 'at', 'lt', 'bone' ], f'Mesh name {name} not recognized'
    if name == 'skel_skel':
        # f'/{exp_name}/meshes'
        return f'{root}/{exp_name}/meshes/SKEL/SKEL_skel{frame_i:04d}.ply'
    if name == 'skel_skin':
        return f'{root}/{exp_name}/meshes/SKEL/SKEL_skin{frame_i:04d}.ply'
    elif name == 'smpl':
        return f'{root}/{exp_name}/meshes/SMPL/SMPL_{frame_i:04d}.ply'
    elif name == 'osso':
        return f'{root}/{exp_name}/osso/skel/skel_{frame_i:04d}.ply'
    else:
        if name in ['at','lt', 'bone']:
            return f'{root}/{exp_name}/hit/{name.upper()}/{name.upper()}_{frame_i}.ply'
        else:
            raise NotImplementedError(f'Mesh name {name} not implemented')
    
def get_material(name):
    return name+'_mat'
    
if __name__ == "__main__":
    
    output = '/home/mkeller2/data2/Code/SMPL_fit_video/thesis_seq/output'
    
    exp_name = 'P8_69_outdoor_cartwheel'
    
    queue = [
#             [('smpl', 'smpl_mat')],
#             [('skel_skel', 'bone_mat')], 
#             [('osso', 'bone_mat')],
              [('at', 'at_mat')],
            #   [('at', 'at_mat'), ('lt', 'lt_trans_mat'), ('bone', 'bone_mat')],
            [('lt', 'lt_mat')],
            # [('lt', 'lt_mat'),('bone', 'bone_mat')],
           [('skel_skel', 'bone_mat'), ('skel_skin', 'skel_skin_mat')], 
           [('osso', 'bone_mat'), ('smpl', 'smpl_trans_mat')], 
#            [('skel_skel', 'bone_mat'), ('smpl', 'smpl_wire')], 
            #   [('lt', 'lt_mat'), ('bone', 'bone_mat'), ('smpl', 'smpl_wire')],
            #   [('lt', 'lt_mat'), ('skel_skel', 'bone_mat'),('smpl', 'smpl_wire')]
             ]
    
    debug = 0
    min_frame = 0
    max_frame = 656
    skip_render = False
    skip_delete = False
    force = 1
    
    if debug:
        min_frame = 0
        max_frame = 1
        skip_render = False
        skip_delete = False
        force = 1
    
    for task in queue:
        task_name = '_'.join([t[0] for t in task])
        task_folder = os.path.join(output, exp_name, 'Render', task_name)
        os.makedirs(task_folder, exist_ok=True)
    
        for frame in range(min_frame,max_frame):
            
            render_file = os.path.join(task_folder, f'frame_{frame:04d}.png')
            if os.path.exists(render_file) and not force:
                print(f'Frame {frame} for task {task_name} already rendered, force to re-render')
                continue
    
            mesh_mat = [(get_mesh_path(name, frame, exp_name, output), mat) for name, mat in task]

            try:
                render_meshes(mesh_mat, render_file)
            except Exception as e:
                print(f'Error rendering frame {frame} for task {task_name} as {render_file}')
                print(e)
                
            print(f'Rendered frame {frame} for task {task_name} as {render_file}')
            
    
