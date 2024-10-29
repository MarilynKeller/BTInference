
1. Copy the SMPL sequence to be in a expected format 
```sh
python prepare_smpl_seq.py --gender female --exp_name P8_69_outdoor_cartwheel --source=emdb 
```
This code suport two types of source for now, EasyMocap and EMDB. 

You can visualize the SMPL sequence using the following code:


```sh
python vis.py P8_69_outdoor_cartwheel --zd 
```

2. Launch the SKEL inference
```sh
python run_skel_inference.py --exp_name P8_69_outdoor_cartwheel
```
You can visualize the SKEL sequence using the following code:

```sh
python vis.py P8_69_outdoor_cartwheel --zd 
```

3. Launch the HIT meshes extraction
```sh
python generate_hit.py  --mise_resolution 128 --mise_depth 3 --max_queries 500000  
```

4. Extract the SMPL and SKEL meshes
```sh
python vis.py P8_69_outdoor_cartwheel --zd --smpl_meshes --skel_meshes
```

5. Render the meshes with Blender

In blender, set your scene, load the script `render_meshes.py` and run it.

6. Make videos from the renders 

```sh
python make_videos.py --exp_name P8_69_outdoor_cartwheel
```