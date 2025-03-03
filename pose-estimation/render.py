import numpy as np
import bpy
from mathutils import Euler, Quaternion, Vector
import sys
import json
import os
import mathutils
import bpy_extras
import csv
import random
import copy




sys.stdout = sys.stderr

### user settings ###
spacecraft_name =str(sys.argv[7])
spacecraft_dir = '../data/loadable_spacecraft/'
NUMBER_OF_IMAGES = 200 # how many images to generate
output_path =str(sys.argv[8])
RES_X = 1280
RES_Y = 1024
BACKGROUND_STRENGTH_DEFAULT = 0.0
trial_number=1
while (os.path.isdir(output_path+str(trial_number))):
    trial_number=trial_number+1
output_path=output_path+str(trial_number)
print(output_path)
os.makedirs(output_path)


def initialize(light_loc = (-99,75,50), camera_loc = (-20,0,0)):
    '''Initialize the scene.
    
    This script is run with the default blender scene, and so need to initialize multiple objects. The default cube and lighting are removed, camera is moved and parameters are adjusted, and the new lighting and spacecraft are added into the scene.
    
    args:
        light_loc: The location for the lighting source to be placed at.
        camera_loc: The location for the camera to be placed at.
    
    returns:
        spacecraft_vector: The contents of the spacecrafts csv file.
        bpy.data.objects[spacecraft_vector[spacecraft_name]["name"]]: The name of the spacecraft.
        bpy.data.objects["Camera"]: The camera object.
        bias: The bias values that will be used for all of the rotations.'''
    # output_node = bpy.data.scenes["Render"].node_tree.nodes["File Output"]
    # output_node.base_path = output_path
    # set color management
    for scene in bpy.data.scenes:
        scene.view_settings.view_transform = 'Filmic'
        scene.view_settings.look = 'High Contrast' 
    # remove the initial cube that is loaded in, and the light source.
    for obj in bpy.context.scene.objects:
        if(obj.name == 'Cube' or obj.name == 'Light'):
            bpy.data.objects.remove(obj)
    #add sunlamp
    bpy.ops.object.light_add(type='SUN', radius=500, align='WORLD', location=light_loc) 

    #adjust the energy of the light source
    bpy.data.objects["Sun"].data.energy = 5
    #point the light towards the origin
    update_object(bpy.data.objects['Sun'], distance=100, target=mathutils.Vector((0,0,0)))
    #set the background default
    bpy.data.worlds['World'].node_tree.nodes['Background'].inputs['Strength'].default_value = BACKGROUND_STRENGTH_DEFAULT
    #load spacecraft metadata
    with open(spacecraft_dir + "/names.json", "r") as json_file:
        spacecraft_vector = json.load(json_file)

    #get a random quaternion...
    orient = Quaternion((np.random.uniform(0,1),np.random.uniform(0,1),np.random.uniform(0,1),np.random.uniform(0,1)))
    tot = np.sqrt(orient.w**2 + orient.x**2 + orient.y**2 + orient.z**2)
    orient.w = orient.w/tot
    orient.x = orient.x/tot
    orient.y = orient.y/tot
    orient.z = orient.z/tot
    load_spacecraft(spacecraft_vector, orient)
    #load_spacecraft(spacecraft_vector, Euler((0, 0, np.pi/2)).to_quaternion())#orient)
    #load_spacecraft(spacecraft_vector)
    #render resolution settings
    render_settings = bpy.context.scene.render
    render_settings.resolution_x = 1280
    render_settings.resolution_y = 1024
    bpy.data.objects["Camera"].data.angle = 14*3.1415/180
    bpy.data.objects["Camera"].data.clip_start = 0.1
    bpy.data.objects["Camera"].data.clip_end = spacecraft_vector[spacecraft_name]["maxStand"]+100
    #set the camera orig location
    bpy.data.objects["Camera"].location = Vector(camera_loc)
    #header data for the output csv's
    with open(os.path.join(output_path, 'provided_data.csv'), 'a+', newline='') as csvfile:
        csvwriter=csv.writer(csvfile)
        csvwriter.writerow(['image', 'range'])
    with open(os.path.join(output_path, 'pose_data.csv'), 'a+', newline='') as csvfile:
        csvwriter=csv.writer(csvfile)
        csvwriter.writerow(['image', 'label', 'x location', 'y location', 'z location', 'w orientaiton', 'x orientation', 'y orientation', 'z orientaiton'])
    #initiate bias values for the rotations...
    bias = [np.random.uniform(-10.,10.), np.random.uniform(-10.,10.)]
    print("======DONE INIT======")
    #return the spacecraft and camrea objects
    return spacecraft_vector, bpy.data.objects[spacecraft_vector[spacecraft_name]["name"]], bpy.data.objects["Camera"], bias
def load_spacecraft(spacecraft_vector, orient = Quaternion((1,0,0,0))):
    '''load the spacecraft into the scene.
    
    This loads the spacecraft into the scene, and then proceeds to reorient it so that it has the desired initial orientation.
    
    args:
        spacecraft_vector: The spacecraft csv file vector, which contains all the spacecrafts (plural) info
        orient: The quaternion orientation for the initial spaceraft orientation we desire.
    '''
    options = {
        'filepath': spacecraft_dir + spacecraft_vector[spacecraft_name]["file"],
        'directory': os.getcwd(),
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
    #set the initial orientation of the spacecraft
    bpy.data.objects[spacecraft_vector[spacecraft_name]["name"]].rotation_euler = orient.to_euler()

def update_object(obj, target, distance=10.0):
    '''Point an object towards a target.

    This is used to point an object towards a specified location, and place it a certian distance away. Used for setting the initial orientation of the camera and lighting.
    
    args:
        obj: The object we want to reorient/move.
        target: The target point we want to point at.
        distance: How far away we want the object to be from the target point.
    '''
    direct = obj.location - target
    rot_quat = direct.to_track_quat('Z', 'Y')

    obj.rotation_euler = rot_quat.to_euler()
    obj.location = rot_quat @ mathutils.Vector((0.0, 0.0, distance))

def render(direct, i):
    '''Render the scene into the image.
    
    Generate the rendered image, and write it to a png file.
    
    args: 
        direct: The directory to write to.
        i: The image id in the sequence.
    '''
    bpy.context.view_layer.update()
    bpy.context.scene.render.resolution_x = RES_X
    bpy.context.scene.render.resolution_y = RES_Y
    bpy.context.scene.camera = bpy.data.objects['Camera']
    bpy.context.scene.render.image_settings.file_format = 'PNG'
    filename = "image_"
    if(i<10):
        filename = filename+"0"+str(i)
    else:
        filename = filename+str(i)
    bpy.context.scene.render.filepath = os.path.join(direct, filename)
    bpy.ops.render.render(write_still=True)

#rpi = reference point index. ip = intersection point
def update_data( i, label, spacecraft, reference_point, orig_rot, rpi, ip, camera, camera_orig_location):
    '''Update the output data / csv files.
    
    Write the relative pose data and the range info as well as metadata to the appropriate csv files.
    
    args:
        i: The index of this image / run.
        label: The spacecraft label.
        spacecraft: The spacecraft object.
        reference_point: The reference point on the spacecraft that is used for the relative pose.
        orig_rot: The original rotaiton of the spacecraft.
        ip: The intersection point of the raycast between the camera and the spacecraft.
        camera: The camera object.
        camera_orig_location: The original camera location, to get the delta range of the spacecraft.
    '''
    #the reference point, rotated BACK to the global reference frame (the reference frame of the first image).
    bpy.context.view_layer.update()
    translation = spacecraft.rotation_euler.to_matrix() @ orig_rot.to_matrix().inverted()  @ camera_orig_location-camera.location

    rotation = spacecraft.rotation_euler.to_quaternion() @ orig_rot.inverted()
    range = (ip-camera.location).length
    with open(os.path.join(output_path, 'provided_data.csv'), 'a+', newline='') as csvfile:
        csvwriter=csv.writer(csvfile)
        csvwriter.writerow([i, range])
    with open(os.path.join(output_path, 'pose_data.csv'), 'a+', newline='') as csvfile:
        csvwriter=csv.writer(csvfile)
        csvwriter.writerow([i, label, filter(translation.x, 0.0001),filter(translation.y, 0.0001),filter(translation.z, 0.0001), filter(rotation.w, 0.000001),filter(rotation.x, 0.000001),filter(rotation.y, 0.000001), filter(rotation.z, 0.000001)])

def filter(number, epsilon):
    '''Checks if a number is within epsilon of some values.
    
    Checks if the given number is within epsilon of 1, 0, or -1 and if so, returns the appropriate number. This is so that we don't get 0.9999999 etc. when we are expecting 1 as output for our csv files.
    
    args:
        number: The number we want to compare to 1, 0, and -1
        epsilon: How close to the values we want to be.
        
    returns:
        number: The number that was passed in if it is not close to the given values, and the number it is close to otherwise.'''
    if(abs(1-number)<epsilon):
        return 1
    if(abs(-1-number)<epsilon):
        return -1
    if(abs(number)<epsilon):
        return 0
    return number 
def move_objects(camera, spacecraft, min_standoff, max_standoff, bias):
    '''Move the objects in the scene.
    
    Rotate the spacecraft and move the camera. Make sure that the maximum delta poses are still enforced, and make sure that the center pixel of the camera still hits the spacecraft. This is an assumption we are making for the LRF.

    args:
        camera: The camera object.
        spacecraft: The spacecraft object.
        min_standoff: How close the camera is allowed to get to the spacecraft.
        max_standoff: How far the camera is allowed to get from the spacecraft.
        bias: The rotation bias for the spacecraft, so that we are actually rotating in a certian direction.
        
    returns:
        intersection_point: The point on the spacecraft where the "LRF" (actually a raycast from the center pixel of the camera) hits the spacecraft.
    '''
    #we can at most rotate the camera 
    deg = 30.-abs(bias[0])-abs(bias[1])
    rad = np.deg2rad(deg)
    rad = random.uniform(0, rad)
    pitch = random.uniform(0,rad)
    rad = rad-pitch
    yaw = rad
    yaw = yaw*random.choice([-1,1])+np.deg2rad(bias[0])
    pitch = pitch*random.choice([-1,1])+np.deg2rad(bias[1])

    #generate the rotation
    rotation = ((Euler((0, pitch, yaw))).to_quaternion()).to_euler()
    spacecraft.rotation_euler  = (spacecraft.rotation_euler.to_matrix() @  rotation.to_matrix()).to_euler()
    #now move the spacecraft around slightly, after selecting some point to look at...
    #select some random point on the spacecraft to look at:
    raycast_failed = True
    while (raycast_failed):
        bpy.context.view_layer.update()
        target = spacecraft.matrix_world @ random.choice(spacecraft.data.vertices).co
        # #move the camera to the targets y/z location, and randomly select some x walk, making sure that we aren't too close / too far
        x = camera.location.x
        x = x+random.uniform(-1.0,1.0)
        if(x>-min_standoff):
            x = -min_standoff
        if(x<-max_standoff):
            x = -max_standoff
        camera.location = Vector((x, target.y, target.z))
        #jenky but need this to update objects
        for obj in bpy.context.scene.objects:
            obj.hide_render = obj.hide_render
        #find out the closest point between the camera and the target.
        #raycasting is done in local reference frame...
        #TODO: make sure we aren't ray casting through the center of the spacecraft, but through the taget point..
        print(target)
        cam_pos = camera.location
        vertex = target
        ray_direction = (vertex-cam_pos).normalized()
        ray_length = max_standoff*5
        ray_direction *= ray_length
        scan = spacecraft.ray_cast(spacecraft.matrix_world.inverted() @ cam_pos, spacecraft.matrix_world.inverted() @ ray_direction)
        print(scan)
        if(scan[0]):
            intersection_point = spacecraft.matrix_world @ scan[1]
            raycast_failed = False
            print("Ray Cast successful!")
        else:
            print("Ray Cast Failed! attemting with a new target vertex...")
    return intersection_point
    
def main():
    leftover = 10000
    r1 = random.uniform(-100,0)
    leftover -= r1*r1
    r2 = random.uniform(-np.sqrt(leftover), np.sqrt(leftover))
    leftover -= r2*r2
    r3 = random.choice([-1,1])*np.sqrt(leftover)
    spacecraft_vector, spacecraft, camera, rot_bias = initialize(light_loc=((r1,r2,r3)))
    #get the spacecraft id
    sc_id = spacecraft_vector[spacecraft_name]["label"]
    #get the min & max standoff distances...
    min_s = spacecraft_vector[spacecraft_name]["minStand"]
    max_s = spacecraft_vector[spacecraft_name]["maxStand"]
    #get a random point on the spacecraft to look at, and set the camera to be looking at that point.
    rpi = random.choice(range(0,len(spacecraft.data.vertices)))
    ref_point = copy.deepcopy(spacecraft.matrix_world @ spacecraft.data.vertices[rpi].co)
    print("REFERENCE POINT: ", rpi)
    #record the reference point
    #orient the camera to be looking along the x-axis
    update_object(camera, distance=min_s+random.uniform(0,max_s-min_s), target=Vector((0,0,0)))
    #move the camera to look at the reference point location
    camera.location = Vector((camera.location.x, ref_point.y, ref_point.z))
    #record the camera reference location
    orig_cam_loc = copy.deepcopy(camera.location)#Vector((camera.location.x, camera.location.y, camera.location.z))
    #set the intersection point (where the LRF hits the spacecraft)
    ip = ref_point
    orig_rot = copy.deepcopy(spacecraft.rotation_euler.to_quaternion())
    for i in range(0,NUMBER_OF_IMAGES-1):
        render(output_path, i)
        update_data(i,sc_id, spacecraft, ref_point, orig_rot, rpi, ip, camera, orig_cam_loc)
        ip = move_objects(camera, spacecraft, min_s, max_s, rot_bias)
    
    render(output_path, NUMBER_OF_IMAGES-1)
    update_data(NUMBER_OF_IMAGES-1, sc_id, spacecraft, ref_point, orig_rot, rpi, ip,camera, orig_cam_loc)
    bpy.ops.wm.quit_blender()

if __name__ == "__main__":
    main()