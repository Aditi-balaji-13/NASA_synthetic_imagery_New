import numpy as np
import bpy
import starfish
import starfish.annotation
from mathutils import Euler
import sys
import json
import time
import os
import tqdm
import csv
import random
import mathutils
import bpy_extras

"""
    script for generating training data with glare, blur, and domain randomized backgrounds.
"""
sys.stdout = sys.stderr

### user settings ###
spacecraft_name = "DEEP SPACE 1"
#SPACECRAFT THAT DONT WORK:    
# "CLOUDSAT": {
# "path": "loadable_spacecraft/cloudsat.fbx",
# "name": "CloudSat",
# "label": "007",
# "minStand": 100,
# "maxStand": 120
# },
# "SENTINEL 6": {
#     "path": "loadable_spacecraft/Sentinel6.fbx",
#     "name": "Sentinel6",
#     "label": "026",
#     "minStand": 140,
#     "maxStand": 190
# },
RANDOM_LIGHTING = True
spacecraft_directory = '../data/loadable_spacecraft/'
background_image_directory = '../data/rand_light_back/'
NUMBER_OF_IMAGES = 20 # how many images to generate
lighting_effect_types = ['Glare', 'Blur']
output_path ="./output/trial_0"   #### use edit this ####
# render resolution of image
RES_X = 1280
RES_Y = 1024
#background strength defaults 
BACKGROUND_STRENGTH_DEFAULT = 0.312
GLARE_TYPES = ['FOG_GLOW', 'SIMPLE_STAR', 'STREAKS', 'GHOSTS']
###

trial_number=1
while (os.path.isdir(output_path+str(trial_number))):
    trial_number=trial_number+1
output_path=output_path+str(trial_number)
print(output_path)
os.makedirs(output_path)

def set_filter_nodes(filters, node_tree):
    '''Set filter node parameters to random value.

    A function for modifying the filters that are applied to the image. These will generally be the blur, glare, and exposure of the image. Various different types of these three things can be added. 

    args:
        filters: What filters to apply
        node_tree: the Node tree for the blender scene.
    
    returns:
        result_dict: The lookup dict for the filter to apply by starfish.
    '''
    result_dict = {
        'Glare':{
            'mix':-1,
            'threshold': 8,
            'type': 'None'
        },
        
        'Blur':{
            'size_x':0,
            'size_y':0
        },
         
        'Exposure': -8.15
    }
    if 'Glare' in filters:
        glare_value = np.random.random()*1.0-1.0  #edit these values by tuning the compositing tab in Blender
        glare_type = np.random.randint(0,4)       #edit these values by tuning the compositing tab in Blender
        glare_threshold = np.random.beta(1,4)      #edit these values by tuning the compositing tab in Blender
        # configure glare node
        node_tree.nodes["Glare"].glare_type = result_dict['Glare']['type'] = GLARE_TYPES[glare_type]
        node_tree.nodes["Glare"].mix = result_dict['Glare']['mix'] = glare_value
        node_tree.nodes["Glare"].threshold = result_dict['Glare']['threshold'] = glare_threshold

    if 'Blur' in filters:
        # set blur values
        blur_x = int(np.random.uniform(0, 1))
        blur_y = int(np.random.uniform(0, 1))
        node_tree.nodes["Blur"].size_x = result_dict['Blur']['size_x'] = blur_x
        node_tree.nodes["Blur"].size_y = result_dict['Blur']['size_y'] = blur_y
    
    if 'Exposure' in filters:
        exposure = np.random.uniform(-2, 0)
        node_tree.nodes["Exposure"].exposure =  result_dict['Exposure'] =  exposure
    
    return result_dict

def line_from_points(x1,y1, x2,y2):
    '''Generate a line from two points. 
    
    Get the line that passes through the two points that are given.
    
    args:
        x1: The x coordinate of the first point.
        y1: The y coordinate of the first point.
        x2: The x coordinate of the second point.
        y2: The y coordinate of the second point.
        
    returns:
        m: The slope of the line.
        b: The y-intercept of the line.
    '''
    if(x2-x1 == 0):
        return -100000000, -10000000
    m = (y2-y1) /(x2-x1)
    b = y1-m*x1
    return m,b

def BoundingBox(obj,cam):
    '''Get the bounding box around the spacecraft.

    Construct the bounding box around the spacecraft by adding edge vertices and finding the minimum/maximum vertices. This is done by first looking at the edges and finding the ones that are on the boundary of the image, and then adding vertices on the edge of the image. Then, all vertices are then compared after being projected on the image, and the maximum/minimum values are then returned.
    
    args:
        obj: The spacecraft object we want the bounding box around.
        cam: The camera object which is taking the image.

    returns:
        X_min: The minimum x coordinate pixel for the bounding box around the spacecraft.
        Y_min: The minimum y coordinate pixel for the bounding box around the spacecraft.
        X_max: The maximum x coordinate pixel for the bounding box around the spacecraft.
        Y_max: The maximum y coordinate pixel for the bounding box around the spacecraft.
    '''
    in_image = []
    #first, go through, and add all cases of points being outside of the image.
    for edge in obj.data.edges:
        verts = [obj.data.vertices[v].co for v in edge.vertices]
        for i in range(len(verts)):
            verts[i] = obj.matrix_world @ verts[i]
        coords_2d = [bpy_extras.object_utils.world_to_camera_view(bpy.context.scene, cam, coord) for coord in verts]
        one_true = False
        one_false = False
        points = []
        for x, y, d in coords_2d:
            my_x = RES_X*x
            my_y = RES_Y-RES_Y*y
            points.append(tuple((my_x, my_y)))
            if my_x<=RES_X and my_x>=0 and my_y <=RES_Y and my_y >=0:
                one_true = True
            else:
                one_false = True
        if one_false and one_true:
            #first, get the line.
            m, b = line_from_points(points[0][0], points[0][1], points[1][0], points[1][1])

            #get the x=0 intersect, y=0 intersect, x=RES_X, y=RES_Y
            #find which one is (a) within the other boundary, and (b) between the two points.
            #x=0 intersect:
            if b<min(RES_Y, max(points[0][1], points[1][1])) and b>max(0, min(points[0][1], points[1][1])) :
                in_image.append(tuple((0,b)))
            #y=0 intersect
            elif -b/m<min(RES_X, max(points[0][0], points[1][0])) and -b/m>max(0, min(points[1][0], points[1][0])):
                in_image.append(tuple((-b/m,0)))
            #x=RES_X y = m*RES_X+b
            elif m*RES_X+b<min(RES_Y, max(points[0][1], points[1][1])) and m*RES_X+b>max(0, min(points[0][1], points[1][1])):
                in_image.append(tuple((RES_X,m*RES_X+b)))
            elif (RES_Y-b)/m<min(RES_X, max(points[0][0], points[1][0])) and (RES_Y-b)/m>max(0, min(points[0][0], points[1][0])):
                in_image.append(tuple(((RES_Y-b)/m,RES_Y)))
        



    #get the vertices
    mat = obj.matrix_world
    verts = [vert.co for vert in obj.data.vertices]
    for i in range(len(verts)):
        verts[i] = obj.matrix_world @ verts[i]

    #rotate the coords into the 2d camera view.
    coords_2d = [bpy_extras.object_utils.world_to_camera_view(bpy.context.scene, cam, coord) for coord in verts]

    for x, y, d in coords_2d:
        my_x = int(RES_X*x)
        my_y = int(RES_Y-RES_Y*y)
        if my_x<=RES_X and my_x>=0 and my_y <=RES_Y and my_y >=0:
            in_image.append(tuple((RES_X*x,RES_Y-RES_Y*y)))

    Y_max = int(max(in_image, key = lambda i : i[1])[1])
    X_max = int(max(in_image, key = lambda i : i[0])[0])
    Y_min = int(min(in_image, key = lambda i : i[1])[1])
    X_min = int(min(in_image, key = lambda i : i[0])[0])

    in_image.clear()

    return(
        X_min,
        Y_min,
        X_max,
        Y_max
    )

def generate(num,
             filters,
             sc,
             background_dir=background_image_directory,
             spacecraft_dir=spacecraft_directory):
    '''Generate a bunch of images.
    
    This is the main body of this script, and actually generates the images. It must be run with the `no_spacecraft.blend` scene. It first creates a sequence of scene configurations using Starfish, modifies the lighting if we are not using random lighting, finds the bounding box around the spacecraft, and updates the output csv file.

    args:
        num: The number of images to render.
        filters: What Blur / Glare / Exposure filters to apply.
        background_dir: The path to the background images folder.
        spacecraft_dir: The path the the spacecraft fbx file foler.
    '''
    #where does the image save
    output_node = bpy.data.scenes["Render"].node_tree.nodes["File Output"]
    output_node.base_path = output_path

    # remove all animation
    for scene in bpy.data.scenes:
        for obj in scene.objects:
            obj.animation_data_clear()
    bpy.context.scene.frame_set(0)

    # set color management
    for scene in bpy.data.scenes:
        scene.view_settings.view_transform = 'Filmic'
        scene.view_settings.look = 'High Contrast' 
    if background_dir is not None:
        images_list = []
        for f in os.listdir(background_dir):
            if f.endswith(".exr") or f.endswith(".jpg") or f.endswith(".png"):
                images_list.append(f)

    #load background metadata
    with open(background_dir+"/background.json", "r") as json_file:
        background_vector = json.load(json_file)
    #load spacecraft metadata
    with open(spacecraft_dir + "/names.json", "r") as json_file:
        spacecraft_vector = json.load(json_file)
    #call starfish to generate series of random poses, lightings, and backgrounds
    sequence = starfish.Sequence.standard(
        pose=starfish.utils.random_rotations(num),
        position=[(0,0,0) for i in range(0,num)],
        lighting=starfish.utils.random_rotations(num),
        background=starfish.utils.random_rotations(num),
        #NOTE: sc must be within ~200m of camera
        distance=np.random.uniform(20, 850, size=(num,)),   ### important: how far are you away from the upper stage (m)
        offset=np.random.uniform(low=0.05, high=0.95, size=(num,2))
    )

    #Load in a new spacecraft...
    fp = spacecraft_dir + spacecraft_vector[sc]["file"]
    sc_name = spacecraft_vector[sc]["name"]
    direct = spacecraft_dir
    options = {
        'filepath': fp,
        'directory': direct,
        'use_image_search': True,
        'use_custom_props': True,
    }
    bpy.ops.import_scene.fbx(**options)

    for img in bpy.data.images:
        if not img.users:
            bpy.data.images.remove(img)

    for img in bpy.data.images:
        if img.source == 'FILE':
            img.reload()
    spacecraft = bpy.data.objects[sc_name]
    spacecraft.parent = bpy.data.objects["spacecraft"]
    spacecraft.hide_render=False

    bpy.data.scenes['Render'].render.resolution_x = RES_X
    bpy.data.scenes['Render'].render.resolution_y = RES_Y
    bpy.data.objects["Camera_Real"].data.angle = 14*3.1415/180
    bpy.data.objects["Camera_Real"].data.clip_start = 15
    bpy.data.objects["Camera_Real"].data.clip_end = 900

    # set default background in case base blender file is messed up
    bpy.data.worlds['World'].node_tree.nodes['Background'].inputs['Strength'].default_value = BACKGROUND_STRENGTH_DEFAULT 
    
    # set background image mode depending on nodes in tree either sets environment texture or image node
    # NOTE: if using image node it is recommended that you add a crop node to perform random crop on images.
    # WARNING: this only looks to see if nodes are in the node tree. does not check if they are connected properly.
    image_node_in_tree = 'Image' in bpy.data.scenes['Render'].node_tree.nodes.keys()
    if image_node_in_tree:
        random_crop = 'Crop' in bpy.data.scenes['Render'].node_tree.nodes.keys()

    #create header for bounding box csv file
    with open(os.path.join(output_node.base_path, 'bounding_box_data.csv'), 'a+', newline='') as csvfile:
            csvwriter=csv.writer(csvfile)
            csvwriter.writerow(['image', 'label spacecraft', 'label background','xmin', 'ymin', 'xmax', 'ymax'])

    # render images
    for i, frame in enumerate(sequence):
        #first set the lighting strength, if generating random lighting
        if RANDOM_LIGHTING:
            bpy.data.objects["Sun"].data.energy = np.random.normal(200, 90)
        print("ENERGY: ", bpy.data.objects["Sun"].data.energy)
        #get background image for lighting
        background_image = np.random.choice(images_list)
        b = background_vector[background_image]
        #set up scene to get correct lighting position (will need to setup again later)
        frame.setup(bpy.data.scenes['Render'], bpy.data.objects["spacecraft"], bpy.data.objects["Camera_Real"], bpy.data.objects["Sun"])
        off_x = 0
        off_y = 0
        image = bpy.data.images.load(filepath =  background_dir + '/' + background_image)
        frame.background_image = str(background_image)
        if image_node_in_tree:
            if random_crop: 
                if RES_X < image.size[0]:
                    frame.crop_x = off_x = np.random.randint(0, image.size[0]-RES_X-1)
                    bpy.data.scenes["Render"].node_tree.nodes["Crop"].min_x = off_x
                    bpy.data.scenes["Render"].node_tree.nodes["Crop"].max_x = off_x + RES_X
                else:
                    bpy.data.scenes["Render"].node_tree.nodes["Crop"].min_x = 0
                    bpy.data.scenes["Render"].node_tree.nodes["Crop"].max_x = image.size[0]
                if RES_Y < image.size[1]:
                    frame.crop_y = off_y = np.random.randint(0, image.size[1]-RES_Y-1)
                    bpy.data.scenes["Render"].node_tree.nodes["Crop"].min_y = off_y
                    bpy.data.scenes["Render"].node_tree.nodes["Crop"].max_y = off_y + RES_Y
                else:
                    bpy.data.scenes["Render"].node_tree.nodes["Crop"].min_y = 0
                    bpy.data.scenes["Render"].node_tree.nodes["Crop"].max_y = image.size[1]
            bpy.data.scenes['Render'].node_tree.nodes['Image'].image = image

        #bounding box. We need to get this here so that we can ge the center of the spacecraft...
        #TODO: fails when the spacecraft loaded is a parent object of multiple meshes.

        if not RANDOM_LIGHTING:
            box = BoundingBox(spacecraft, bpy.context.scene.camera)
            box = np.array([box[0], box[1], box[2], box[3]])

            #TODO: need to set this up so that we move the point depending on what part of the image we crop...
            if(b["in_image"]):
                #get the center of the bounding box...
                centerBox = np.array([box[0]+(box[2]-box[0])/2, box[1]+(box[3]-box[1])/2])
                print(centerBox)
                xy_light = np.array([-centerBox[0]+b["x"]-off_x, centerBox[1]-b["y"]-off_y])
                print(off_x)
                print(off_y)
                mag = np.linalg.norm(xy_light)
                xy_light = xy_light/mag
                vt = mathutils.Vector((xy_light[0]*np.random.uniform(0.8,1.2),xy_light[1]*np.random.uniform(0.8,1.2),b["z"]*np.random.uniform(0.8,1.2)))
            else:
                vt = mathutils.Vector((b["x"]*np.random.uniform(0.8,1.2),b["y"]*np.random.uniform(0.8,1.2),b["z"]*np.random.uniform(0.8,1.2)))

            vf = mathutils.Vector((0,0,0))
            rotation_matrix = (vt-vf).to_track_quat('Z','Y').to_matrix().to_4x4()
            e = rotation_matrix.decompose()[1]
            frame.lighting = starfish.utils.to_quat(e)
        #actually setup scene, with correct lighting.
        frame.setup(bpy.data.scenes['Render'], bpy.data.objects["spacecraft"], bpy.data.objects["Camera_Real"], bpy.data.objects["Sun"])

        # create name for the current image (unique to that image)
        output_node.file_slots[0].path = "image_#" + str(i)
        #output_node.file_slots[1].path = "mask_#" + str(i)

        # set filters to random values
        #frame.augmentations = set_filter_nodes(filters, bpy.data.scenes["Render"].node_tree)
        
        # render
        bpy.ops.render.render(scene="Render")
        # get the bounding box... again 
        box = BoundingBox(spacecraft, bpy.context.scene.camera)
        box = np.array([box[0], box[1], box[2], box[3]])
        minx = box[0]
        miny = box[1]
        maxx = box[2]
        maxy = box[3]
        try:
            bbox=[i, spacecraft_vector[sc]["label"],background_vector[background_image]["label"] , minx, miny, maxx, maxy]
        except:
            bbox=[i, 1, 0, 0, 0, 0,0]

        with open(os.path.join(output_node.base_path, 'bounding_box_data.csv'), 'a+', newline='') as csvfile:
            csvwriter=csv.writer(csvfile)
            csvwriter.writerow(bbox)


def main():
    generate(NUMBER_OF_IMAGES, lighting_effect_types,spacecraft_name, background_image_directory, spacecraft_directory)


if __name__ == "__main__":
    main()
