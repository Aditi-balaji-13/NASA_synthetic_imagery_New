# Overview
This section contains a detailed explanation of the second phase of the competition, involving spacecraft pose estimation. For this phase, contestants are asked to generate relative pose data for a spacecraft, given a sequence of images, and corresponding Laser Ranger Finder (LRF) distance measurements. An example input image sequence is shown below.

> **&#9432; NOTE:**
> For this phase, it is guarunteed that the LRF will fire from the center of the image, and will always hit some point on the spacecraft.

<img src="https://gitlab-fsl.jsc.nasa.gov/stefan.d.caldararu/synthetic-imagery/-/raw/main/example_images/image_00.png?ref_type=heads" alt="image" width="300"/> <img src="https://gitlab-fsl.jsc.nasa.gov/stefan.d.caldararu/synthetic-imagery/-/raw/main/example_images/image_01.png?ref_type=heads" alt="image" width="300"/> <img src="https://gitlab-fsl.jsc.nasa.gov/stefan.d.caldararu/synthetic-imagery/-/raw/main/example_images/image_02.png?ref_type=heads" alt="image" width="300"/> <img src="https://gitlab-fsl.jsc.nasa.gov/stefan.d.caldararu/synthetic-imagery/-/raw/main/example_images/image_03.png?ref_type=heads" alt="image" width="300"/> <img src="https://gitlab-fsl.jsc.nasa.gov/stefan.d.caldararu/synthetic-imagery/-/raw/main/example_images/image_04.png?ref_type=heads" alt="image" width="300"/> <img src="https://gitlab-fsl.jsc.nasa.gov/stefan.d.caldararu/synthetic-imagery/-/raw/main/example_images/image_05.png?ref_type=heads" alt="image" width="300"/> <img src="https://gitlab-fsl.jsc.nasa.gov/stefan.d.caldararu/synthetic-imagery/-/raw/main/example_images/image_06.png?ref_type=heads" alt="image" width="300"/> <img src="https://gitlab-fsl.jsc.nasa.gov/stefan.d.caldararu/synthetic-imagery/-/raw/main/example_images/image_07.png?ref_type=heads" alt="image" width="300"/> <img src="https://gitlab-fsl.jsc.nasa.gov/stefan.d.caldararu/synthetic-imagery/-/raw/main/example_images/image_08.png?ref_type=heads" alt="image" width="300"/> <img src="https://gitlab-fsl.jsc.nasa.gov/stefan.d.caldararu/synthetic-imagery/-/raw/main/example_images/image_09.png?ref_type=heads" alt="image" width="300"/>

Currently, it can be assumed that the relative pose will not change by more than 30 degrees between consecutive images, and the distance between the camera and the center of the spacecraft will not change by more than 1 meter. 

> **&#9432; NOTE:**
> While the distance between the camera and the center of the spacecraft is restricted, the relative distance provided to the spacecraft can change much more. This is because the LRF gets the distance to the surface of the spacecraft, depending on the size of the spacecraft.

## Reference Frame Definitions
While Blender has well defined reference frames, we cannot expect competitors to extrapolate this information based purely off of the images (e.g. the center of the spacecraft is rarely well-defined). To this end, we provide a reference for consistent relative pose information. This is the method used for the priveledged data generation, and is the expected output the competitors should generate. 

### Reference Frame
the first image in a sequence is considered the **Base** image, grounding all future images with a reference frame. The reference frame is defined by the point on the spacecraft that the LRF hits in this base image, and a unit quaternion rotation.

### How data is generated in Blender
TODO: do we need this in the git repo?

### Relative Pose
TODO: do we need this in the git repo?

# Rendering Data
In order to render additional data for this phase of the competition, contestants must run the following command:
```bash
blender -b -E CYCLES --python render.py
```
> **&#9432; NOTE:**
> There is no blender file associated with this as it is designed to fully generate using the python script from the default blender scene.

This will generate a sequence of 10 images of consecutive rotations of the spacecraft. For more details on the specific options, see [this](https://gitlab-fsl.jsc.nasa.gov/stefan.d.caldararu/synthetic-imagery/-/tree/main/bounding-box?ref_type=heads#rendering-data) section.

## Double Lighting
An additional script is provided with two lighting sources, helping ensure that the spacecraft is lit from multiple angles and can be seen clearly in the image. To run this script, replace `render.py` with `render_double_lighting.py` in the above command.

# Data Format
There are two csv files associated with each sequence. The first, named `provided_data.csv` includes the range information for each image, and is formatted as follows: 
```
image_number, range
```

The second csv file is named `pose_data.csv`, and includes the priviledged information associated with each image. This includes the spacecraft label, relative position to the base image, and relative pose represented as a quaternion. This is formatted as follows:
```
image, label, x_location, y_locaiton, z_location, w_orientation, x_orientation, y_orientaiton, z_orientaiton
```

For more information on the spacecraft labels, see [this](https://gitlab-fsl.jsc.nasa.gov/stefan.d.caldararu/synthetic-imagery/-/blob/main/data/README.md?ref_type=heads#overview-of-json-files) document. The images are 1280 x 1024 resolution, with a 14 degree FOV, based on the specs of the [MQ013CG-E2](https://www.ximea.com/en/products/cameras-filtered-by-sensor-types/mq013cg-e2).

# Modifying the Data Produced
## Rendering More Images
Currently, only ten images are produced in a series. To modify this, change the [`NUMBER_OF_IMAGES`](https://gitlab-fsl.jsc.nasa.gov/stefan.d.caldararu/synthetic-imagery/-/blob/main/pose-estimation/render.py?ref_type=heads#L21) parameter in the python script.

## Changing the Spacecraft
Additionally, the only spacecraft rendered is the Deep Space 1 probe. To modify this, change the [`spacecraft_name`](https://gitlab-fsl.jsc.nasa.gov/stefan.d.caldararu/synthetic-imagery/-/blob/main/pose-estimation/render.py?ref_type=heads#L19) parameter in the python script to a different variable name from [this](https://gitlab-fsl.jsc.nasa.gov/stefan.d.caldararu/synthetic-imagery/-/blob/main/data/loadable_spacecraft/names.json?ref_type=heads) file (e.g. `ACRIMSAT`).

## Adding Spacecraft
For more instructions on augmenting the dataset with your own spacecraft models, follow the instructions described in [this](https://gitlab-fsl.jsc.nasa.gov/stefan.d.caldararu/synthetic-imagery/-/blob/main/data/README.md?ref_type=heads) document.