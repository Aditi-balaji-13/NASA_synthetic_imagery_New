# Generate Mask and New Images

The codes in this folder are used to generate the mask and new images from models.

## The pipeline is as follows:
**Step 1**: Generate Images with Transparent Background:
   ```shell
    blender -b no_spacecraft.blend -E CYCLES --python render_fbx.py
  ```
  It will generate 2000 images with random lightning, camera position and spacecraft position.

**Step 2**: Generate Mask in YOLO format with bbox and polygons:
   ```shell
    python gen_masks.py <image_folder> <output_txt_folder> <output_mask_folder> <class_id>
  ```
  It will generate 2000 masks for the images.
  
**Step 3**: Generate New Images:
  ```shell
    python gen_seg_pipe.py <objects_folder> <masks_folder> <backgrounds_folder> <output_images_folder> <output_masks_folder> --num_images <number_of_images>
  ```
  It will generate new images with random images generated above and random background images.



# Others
If you are training the model without the need of bbox:
```shell
python remove_bbox_info.py <folder_path>
```

In advance if you want to merge test and val datasets, since all the generated images are named starting from 00, so there may exist a conflict in the names of the images. So, you can rename the images using this program:
```shell
python script.py --val_image_folder <path_to_val_images> --val_label_folder <path_to_val_labels> \
                        --test_image_folder <path_to_test_images> --test_label_folder <path_to_test_labels>
```
