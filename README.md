# TALOS: Toolkit for Applying Labels to Optical Simulations


## Introduction
This Toolkit contains software for generating simulated imagery of spacecraft on orbit, augmenting that data to account for effects on imagers, and labeing those images. These label types currently include object detection bounding boxes around the spacecraft, binary segmentation masks to segment the spacecraft from the background, and pose (position and orientation) information of the spacecraft which includes simulated laser range finder data, camera parameters, and simulated LiDAR point clouds.

This project was originally created to generate data for the Pose Bowl: spacecraft detection and pose estimation competition. This competition was split into two parts. In the first part, the goal is to identify the unknown spacecraft in an image, and determine the bounding box for the spacecraft. The second part of the competition involved pose estimation of an unknown spacecraft, given a sequence of images. The details of that competition can be found here: https://www.drivendata.org/competitions/group/competition-nasa-spacecraft/ 

This tool has also been used by Rice University in Fall 2024 to train and test a spacecraft segmentation algorithm to segment an unknown spacecraft from the background. That repo is located here: https://github.com/RiceD2KLab/NASA_segmentation_F24 

This repository includes: 
- [TALOS: Training and Labeling in an Optical Simulator](#talos-training-and-labeling-in-an-optical-simulator)
  - [Introduction](#introduction)
  - [Setup](#setup)
    - [Installing Blender](#installing-blender)
    - [Installing pip Dependencies](#installing-pip-dependencies)
    - [Running on FSL](#running-on-fsl)
    - [Hot fix for FSL](#hot-fix-for-fsl)
  - [Image Segmentation \& Pointcloud](#image-segmentation--pointcloud)
  - [Authors, acknowledgment, and contacts](#authors-acknowledgment-and-contacts)
  - [License](#license)
  - [Project status](#project-status)

Subfolder Documents:
- [Spacecraft Detection](SYNTHETIC-IMAGERY/bounding-box/README.md)
- [Pose Estimation](SYNTHETIC-IMAGERY/pose-estimation/README.md)
- [Segmentation and Pointclouds](SYNTHETIC-IMAGERY/seg-and-pointcloud/README.md)
- [Instructions for augmenting the dataset](SYNTHETIC-IMAGERY/data/README.md)
## Setup

### Installing Blender
While this tutorial is primarily meant for Linux users, it can be easily followed on a Windows machine. This can be done by using the parallel installers for Blender, and appropriate Powershell commands.

Blender can be installed either through through `snap`, which can be installed via `apt` on Ubuntu or `yum` on CentOS machines, or with prebuilt binaries by following [this](https://www.blender.org/download/) link. 

> **&#9432; NOTE:**
> Issues have been found with the prebuilt binaries on certain systems (specifically CentOS), so it is recomended to use the snap build. 

For Ubunutu users, run the following commands:
```bash
sudo apt update && sudo apt upgrade
sudo apt install snapd -y
sudo ln -s /var/lib/snapd/snap /snap
sudo snap install core
sudo snap install blender --classic
```
This ensures that the `apt` package manager is up to date, installs Snap and enables 'classic' mode, and finally installs blender. A comprehensive tutorial, as well as instructions on how to install directly with `apt` can be found [here](https://www.linuxcapable.com/how-to-install-blender-on-ubuntu-linux/#:~:text=Install%20Blender%20on%20Ubuntu%2022.04%20or%2020.04%20via,on%20Ubuntu%2022.04%20or%2020.04%20using%20Snap%20)

### Installing pip Dependencies
Blender must be configured with the required `pip` dependencies in order for it to be able to use them with it's python api. Therefore, all required packages must be installed within the `modules` configuration folder for blender. First, we must ensure this folder exists, and is the correct location to install the pip dependencies. This can be checked by running the `test_config.py` script through blender, by runing the following command: 
```bash
blender -b --python test_config.py
```

If run correctly, this should exit with no errors, and print out something like: `/home/[USER]/.config/blender/[BLENDER VERSION]/scripts`. If this is the case, we want to install our pip dependencies at `~/.config/blender/[BLENDER VERSION]/scripts/addons/modules`. 
> **&#9432; NOTE:**
> Replace `[BLENDER VERSION]` with the version of Blender that is installed on the system. It is recomended to use Blendre version 3.6, as this is what is used by the authors of this repository.

> **&#9432; NOTE:**
> By default, the path up to the `scripts` directory should exist after the first time blender renders on your system, but the `addons/modules` folder may not. If this is your first time runing blender and the `~/.config/blender` folder doesn't exist, or the `addons` path doesn't exist, run the following command:
```bash
pushd ~/.config && mkdir -p blender/[BLENDER VERSION]/scripts/addons/modules && popd
```

Once this folder is located/created, we can install the required pip dependencies here for Blender to use. This is done with the following command: 
```bash
pip install -r requirements.txt --no-deps --target ~/.config/blender/[BLENDER VERSION]/scripts/addons/modules/
```

This recursively installs all pip dependencies listed in the [`requirements.txt`](https://gitlab-fsl.jsc.nasa.gov/stefan.d.caldararu/synthetic-imagery/-/blob/main/requirements.txt?ref_type=heads) file. `--no-deps` instructs pip to not install associated dependencies of packages (see [this](https://github.com/autognc/starfish/tree/master#id2) link for more reasoning behind this), and the `--target` command instructs pip to install the modules at the target location specified. Once this command is run, you can ensure the packages installed by checking that the modules folder has been populated.

> **&#9432; NOTE:**
> If this is a fresh ubuntu system, you may need to install pip by runing `sudo apt-get install python-pip`.

### Running on FSL

The pipeline is slightly-broken post Rocky 8 update, but I have figured out the majority of running the pipeline. First, we need to set up our python environment.

```bash
    ml miniforge3 #load the miniforge module for python env management
    conda init #initialize conda (modifies your .bashrc file)
    source ~/.bahsrc #source your .bashrc file
    conda deactivate #deactivate the base environment
    conda create --name testenv python=3.10 -y #create a new python environment
    conda activate testenv #activate the new python env
    cd synthetic-imagery #go to the synthetic imagery folder once it has been cloned
    pip install -r ./requirements.txt --no-deps #install the python packages
```

now we are ready to try and generate some data.

```bash
    cd bounding-box #go to the bounding box folder.
    ml blender #load the blender submodule.
    PYTHONPATH=~/.conda/envs/testenv/lib/python3.10/site-packages/ blender -b no_spacecraft.blend -E CYCLES --python render.py --python-use-system-env
```

The above command is similar to what is written below in the documentation, with the exception of the definition of the `PYTHONPATH` and the `--python-use-system-env` flag.

### Hot fix for FSL

Unfortunately, post-Rocky8 update starfish doesn't seem to be able to generate the background images. Currently it just generates the image of the spacecraft with a clear background. As a result, I have written a small test script for adding the background image back in. This script lives in `synthetic-imagery/seg-and-pointcloud`.


## Image Segmentation & Pointcloud

**Image Segmentation**: Stephan: For the image segmentation, the script described above in the Hot Fix section also generates a segmented image using the `open-cv` python package. The `gen_seg.py` file is able to do this by reading the image generated by blender, and then modifying the pixels depending on if they are part of the spacecraft or not (this can be determined based off of the alpha value of the pixel, which will be 0 if the pixel is not part of the spacecraft). You can either set them to have a value of (0,0,0,255) or (255,255,255,255) depending on this, and then you get a "standard" segmented image. 

Additionally, you can use something similar to this script for the hot fix above, and get an image with the background, by loading in a background image and then modifying the pixels to look like the background image pixel at that spot if it is not part of the spacecraft.

Finally, I would write a python script that does this for all images. The easiest way would be to read in the background images JSON file, read in the generated JSON file from the blender generation script, and then based off of that load in the appropriate background image and the appropriate base image. This way you can generate many images that are segmented or with backgrounds at a time!

UPDATE: This may be fixed with the rice students work. We'll want to update this section based on their work.

**Point Cloud**: Stephan: I did not get as far in the point cloud generation, but this should also be pretty easy. I would recommend using a python package for point clouds to generate a `.pcd` file. Most of the python-based work for this is already done. If you look in the `BoundingBox` function in the `render.py` file, there is already a lot of code that does ray tracing to get a list of vertices for the spacecraft from the camera's perspective. I believe this is what the `coords_2d` list contains in the `BoundingBox` function. The only part that should be required for this is printing out these coordinates in a `.pcd` formated file, which can either be done manually (the approach I would take because it doesn't require understanding any other dependencies), or using some python package that can automatically do this. Either way, the hard part (blender interaction and ray tracing) is already  pretty much done and can be referenced from this function.

## Authors, acknowledgment, and contacts

Contributors:
- James Berck: Project Owner and POC. james.w.berck@nasa.gov
- Stefan Caldararu: Primary NASA Intern Developer
- Liam Smego: NASA Intern Developer
- Rice 2024 Segmentation D2KLab Class: https://github.com/nikhil-chigali, https://github.com/Y1chengJ, https://github.com/Jeffrey-Joan, https://github.com/Resne110799, https://github.com/janhavi-sathe, https://github.com/rr-85, https://github.com/RiceD2KLab
- Rice Spring 2025 Segmentation D2KLab Class:


## License
Apache 2.0

## Project status
pre-release build.
