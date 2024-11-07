# copy an experiment videos to my Dropbox

exp_name=$1

destination='/home/mkeller2/data2/Dropbox/MPI/Thesis_writing/defense/videos'

mkdir $destination/$exp_name
cp -r /home/mkeller2/data2/Code/SMPL_fit_video/thesis_seq/output/$exp_name/Videos/* $destination/$exp_name
cp /home/mkeller2/data2/Code/SMPL_fit_video/thesis_seq/output/$exp_name/video.mp4 $destination/$exp_name

# Image renders
mkdir $destination/$exp_name/render
cp -r /home/mkeller2/data2/Code/SMPL_fit_video/thesis_seq/output/$exp_name/Render/smpl $destination/$exp_name/render/smpl
cp -r /home/mkeller2/data2/Code/SMPL_fit_video/thesis_seq/output/$exp_name/Render/skel_skel $destination/$exp_name/render/skel_skel
# ls -l /home/mkeller2/data2/Code/SMPL_fit_video/thesis_seq/output/$exp_name/Videos