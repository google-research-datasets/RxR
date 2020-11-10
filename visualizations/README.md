# RxR Visualizations

Code for javascript visualizations of aligned RxR instructions and pose traces.

First, download the RxR data (guide annotations and pose traces), the
[Matterport3D dataset](https://niessner.github.io/Matterport/), and clone the
[Matterport3D simulator](https://github.com/peteanderson80/Matterport3DSimulator)
for the navigation connectivity graphs.

In this directory, create symlinks to these resources:

```bash
cd visualizations
ln -s <PATH_TO_MATTERPORT3D_DATASET> mp3d
ln -s <PATH_TO_RXR_DATA> rxr_data
ln -s <PATH_TO_MATTERPORT3D_SIMULATOR> Matterport3DSimulator
```

where `<PATH_TO_MATTERPORT3D_DATASET>` contains the unzipped Matterport3D data
(e.g., `v1/scans/..`), `<PATH_TO_RXR_DATA>` contains the RxR json lines files
and the `pose_traces` directory, and `<PATH_TO_MATTERPORT3D_SIMULATOR>` is the
cloned repo.

Install python dependencies:

```bash
pip3 install absl-py
pip3 install numpy
```

## First Person Mesh-based Visualization

![first_person](first_person.gif)

To set up the visualization for a given dataset split and instruction id, run:

```bash
python3 setup.py \
  --split rxr_train \
  --instruction_id 46944 \ # Corresponds to Figure 4 in the paper.
  --logtostderr

python3 -m http.server
```

and browse to
[localhost:8000/first_person.html](http://localhost:8000/first_person.html).

Rendering may take a few seconds depending on the size of the mesh. The `split`
argument must be one of `rxr_train`, `rxr_val_seen`, `rxr_val_unseen`.

## Third Person Mesh-based Visualization

Coming soon!
