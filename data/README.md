# Overview of JSON Files
JSON files are used to maintain data about each spacecraft required for generation. These JSON files are first loaded by the python script, and then the desired spacecraft's or image's information is applied to the scene. In this document, a description of each parameter is provided, and instructions on adding your own spacecraft or background images is also given.

# Including Your Own Spacecraft
The spacecraft information is stored in the [`names.json`](https://gitlab-fsl.jsc.nasa.gov/stefan.d.caldararu/synthetic-imagery/-/blob/main/data/loadable_spacecraft/names.json?ref_type=heads) file. Each spacecraft has a [variable](https://gitlab-fsl.jsc.nasa.gov/stefan.d.caldararu/synthetic-imagery/-/blob/main/data/loadable_spacecraft/names.json?ref_type=heads#L2) entry, which must be modified in the desired python script to load the desired spacecraft. each entry contains the following information:
## File
The `file` variable specifies the filename in the [`loadable_spacecraft`](https://gitlab-fsl.jsc.nasa.gov/stefan.d.caldararu/synthetic-imagery/-/tree/main/data/loadable_spacecraft?ref_type=heads) folder to load.
> **&#9432; NOTE:**
> This is assumed to be an fbx file. 

## Name
The `name` variable stores the name of the spacecraft object. This can be determined by importing the spacecraft into a Blender instance, and checking the name of the object added. 

## Label
The `label` variable associates a label with each spacecraft, which is printed in the associated csv files for the data generated.

## Standoff
`minStand` and `maxStand` define the distance the camera should be from the spacecraft. Due to variably sized spacecraft, we may want to observe the spacecraft from different distances, and different definitions of render distances are required in Blender.
> **&#9432; NOTE:**
> Getting accurate parameters here may require a bit of trial and error. If the spacecraft can't be easily found in the image, it is likely because the spacecraft is very small, and the camera should be closer. If the spacecraft takes up the entire image or the majority of it, it is recommended to increase the standoff distance.

# Including Your Own Backgorund Images
Background images are used for the first phase of the competition. The data for each background image is stored in the `background.json` file in the [background](https://gitlab-fsl.jsc.nasa.gov/stefan.d.caldararu/synthetic-imagery/-/tree/main/data/background?ref_type=heads) folder. Each background image has the variable name as the filename that should be loaded. Each image has the following data associated with it:

## In Image, X, Y, Z
These variables correspond to the positioning of the lighting in the background image. These are required to maintain consistency in the lighting for the first phase of the competition. The first parameter, `in_image`, defines whether or not the lighting source is in the backgorund image or not. If it is, then the `x` and `y` parameters define the pixel coordinates of the light source, with origin defined as the top-left corner, and the positive x-axis going to the right, and positive y-axis going down (as commonly defined for images). The z parameter defines the forward-backward location of the light source in meters. If the light source is in the image, the light source should be behind the object, so the z coordinate should be a negative number.

If the light source is not in the image, then the `x` `y` and `z` parameters define the location of the light source relative to the spacecraft. The x-axis is the left/right location, y-axis is up/down, and z-axis is forward backward.
> **&#9432; NOTE:**
> These parameters can be rather confusing, and likely take a lot of trial and error to set correctly. It is recommended to try setting them one at a time.

## Alternative Background Images
If desired, the user can provide their own background images. It is worth noting that to be able to use the non-randomized lighting in the [bounding boxes](https://gitlab-fsl.jsc.nasa.gov/stefan.d.caldararu/synthetic-imagery/-/blob/main/bounding-box/README.md?ref_type=heads) it is necessary to annotate each background image by hand with the [lighting](https://gitlab-fsl.jsc.nasa.gov/stefan.d.caldararu/synthetic-imagery/-/blob/main/data/README.md?ref_type=heads#in-image-x-y-z) data. If it is desired to have a json file auto-generated for use with the random lighting feature, this can bed done by specifying the path to the folder containing these background images, and running the `generate_custom_backgrounds.py` script.