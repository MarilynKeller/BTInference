# BTInference - Bone and Tissue inference wrapper

This repo contains wrapper code to run [OSSO](https://osso.is.tue.mpg.de/), [SKEL](https://skel.is.tue.mpg.de/) and [HIT](https://skel.is.tue.mpg.de/) fits on various [SMPL](https://smpl.is.tue.mpg.de/) data input, visualize and render the result.

https://github.com/user-attachments/assets/88f022ea-5dcd-4df9-9c13-c2f1cce8df0a

Sequence from the [EMDB dataset](https://eth-ait.github.io/emdb/) (P8_69_outdoor_cartwheel), from left to right: input SMPL sequence on video, OSSO, SKEL and HIT fits superimposed to the video. 
The OSSO, SKEL and HIT fits and their rendering were generated with this repo.

This repo has been tested on sequences from the [EMDB dataset](https://eth-ait.github.io/emdb/) and output from [EasyMocap](https://chingswy.github.io/easymocap-public-doc/) (video + SMPL sequence).
[Easymocap](https://chingswy.github.io/easymocap-public-doc/) is an easy-to-use library that allows the extraction of SMPL sequences from any video from the internet. 

This repo lets you, given a SMPL sequence obtained from EasyMocap or EMBD, run the OSSO, SKEL and HIT inference, visualize the results and render the meshes using Blender

This repo is mainly a personal tool, so I don't plan to offer much support but feel free to adapt it to other input data. Basically, you will just need to adapt the `prepare_smpl_seq.py` script to process input data.

## Installation

Depending on what you want to generate, you will need to install the following dependencies:

- OSSO: https://github.com/MarilynKeller/OSSO
- SKEL: https://github.com/MarilynKeller/SKEL
- HIT: https://github.com/MarilynKeller/HIT
- aitviewer-skel: https://github.com/MarilynKeller/aitviewer-skel

You can install them all in the same Python virtual environment. 


## This is the pipeline offered by this repo. After 1., all the other steps are optional. 

1. Preprocess the SMPL sequence to be in an expected format (requires aitviewer or aitviewer-skel)
```sh
python prepare_smpl_seq.py --gender female --exp_name P8_69_outdoor_cartwheel --source=emdb 
```
This code support two types of sources for now, EasyMocap and EMDB, but it can easily be adapted to other sources. 

You can visualize the SMPL sequence using the following code (requires aitviewer or aitviewer-skel):

```sh
python vis.py P8_69_outdoor_cartwheel --zd 
```

2. Launch the SKEL inference (requires SKEL)
```sh
python run_skel_inference.py --exp_name P8_69_outdoor_cartwheel
```
You can visualize the SKEL sequence using the following code  (requires aitviewer-skel):

```sh
python vis.py P8_69_outdoor_cartwheel --zd 
```

3. Launch the HIT meshes extraction (requires HIT)
```sh
python generate_hit.py  --mise_resolution 128 --mise_depth 3 --max_queries 500000  
```

4. Extract the SMPL and SKEL meshes (requires aitviewer-skel)
```sh
python vis.py P8_69_outdoor_cartwheel --zd --smpl_meshes --skel_meshes
```

5. Render the meshes with Blender (requires the [Blender](https://www.blender.org/) software installed)

Open the Blender software from the terminal, set your scene, load the script `render_meshes.py`, edit it to point to the sequence you want to render, and run the script.
In case of an error, check the terminal for the error message.

I did set up the scene manually for this specific example. I guess the scene could be made more generic through scripting for the compositing by loading the video and setting the proper camera pose and focal.

6. Make videos from the rendered frames 

```sh
python make_videos.py --exp_name P8_69_outdoor_cartwheel
```

7. Copy the videos to Dropbox
```sh
sh copy_dropbox.sh P8_69_outdoor_cartwheel
```


## Citation

If you use this code, please consider citing the relevant papers:

```
@inproceedings{Keller:CVPR:2022,
  title = {{OSSO}: Obtaining Skeletal Shape from Outside},
  author = {Keller, Marilyn and Zuffi, Silvia and Black, Michael J. and Pujades, Sergi},
  booktitle = {Proceedings IEEE/CVF Conf.~on Computer Vision and Pattern Recognition (CVPR)},
  month = jun,
  year = {2022},
  month_numeric = {6}}
```

```
@inproceedings{keller2023skel,
  title = {From Skin to Skeleton: Towards Biomechanically Accurate 3D Digital Humans},
  author = {Keller, Marilyn and Werling, Keenon and Shin, Soyong and Delp, Scott and 
            Pujades, Sergi and Liu, C. Karen and Black, Michael J.},
  booktitle = {ACM ToG, Proc.~SIGGRAPH Asia},
  volume = {42},
  number = {6},
  month = dec,
  year = {2023},
}
```

```
@inproceedings{keller2024hit,
  title = {{HIT}: Estimating Internal Human Implicit Tissues from the Body Surface},
  author = {Keller, Marilyn and Arora, Vaibhav and Dakri, Abdelmouttaleb and Chandhok, Shivam and Machann, J{\"u}rgen and Fritsche, Andreas and Black, Michael J. and Pujades, Sergi},
  booktitle = {IEEE/CVF Conf.~on Computer Vision and Pattern Recognition (CVPR)},
  pages = {3480--3490},
  month = jun,
  year = {2024},
  month_numeric = {6}
}
```

