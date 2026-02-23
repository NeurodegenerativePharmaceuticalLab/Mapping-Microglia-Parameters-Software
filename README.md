# Mapping Microglia Parameters Software

## User Guide

Introduction to Microglia Morphometry Methodology
Microglia morphometry analysis provides a quick, unbiased, and accurate mapping of microglia to determine microglial characteristics such as the number of branches, size, and more to determine microglial activity and activation state. This works based on several principles. The user identifies cells and outlines the soma. This will be used in future calculations to determine what constitutes branches, eccentricity etc. on each microglia. Mask generation is the most important aspect as this maps user-selected microglia, based on the pixel intensity, to create several “masks”. These masks represent different sizes (μm²) of the microglia. Here, this program maps microglia at 200, 300, 400, 500, 600, 700, and 800 μm². The user can determine which mask size best captures the differences they are studying. If unsure, 500 μm² is a typical mask size used by multiple groups. 
Introduction to this Application
This application, “Mapping Microglia Parameters Software”, is a comprehensive desktop application designed for immunohistochemistry processing and analyzing microscopy images of microglia cells. This software provides an intuitive graphical interface for background subtraction, manual cell annotation, morphological parameter calculation, and batch processing of multiple images. The application calculates simple characteristics of the cells. More complex analysis can be done by utilizing the jython files. This is recommended for in-depth microglial morphometry analysis. 

### Key Features

•	Background subtraction using rolling ball algorithm, deionization, and sharpening
•	Manual annotation of soma locations and soma outlines to increase accuracy
•	Fast mask generation and QA
•	Automated calculation of morphological parameters
•	Batch processing for multiple images
•	Export results to CSV format with metadata
 Getting Started
### Workflow Overview

The typical workflow consists of three main stages:
1.	Image Processing - Load images, apply background subtraction, and optional filters
2.	Manual Annotation - Mark soma locations and draw soma boundaries
3.	Batch Analysis - Review annotations, generate masks, and calculate morphological parameters

### Step 1: File Selection

This section handles loading images and applying preprocessing steps to improve image quality. 

Images that are to be used should be stored exclusively in one folder (ex. “raw_data_folder”). Only .tif or .TIF files are supported!

Loading Images
4.	In the top left, click Select Image Folder button. This prompts you to select a folder that has your images in it
5.	Click Select Output Folder button. This is where your masks, somas, and data will be saved
6.	Images will appear in the image list on the left
7.	Click on an image name to preview it. Select an image by checking the box next to it. Alternatively, to use all, click Select All, and click Clear All to deselect all. The circle next to the image names will be updated to reflect the stage the image is on. A full legend can be found at the bottom by clicking Legend
8.	Click Image Labeling if you would like to add the animal name and treatment group of each image at this stage. If not, it will prompt you at the end

### Step 2: Parameters

#### Background Subtraction

To improve the accuracy of the mask generation (and subsequently the associated calculations), cleaning the images is a critical step. At any point, click Preview Current Image in the middle left panel to see how selected algorithms would clean the image. Note: This step is reversible as this image will NOT be used or saved. It is simply a preview.

At minimum, background subtraction with the rolling ball method should be done as it removes uneven illumination and improves contrast:
•	Rolling Ball Radius: Adjust the slider or spin box (default: 50 pixels)
○	Smaller values: Better for fine structures
○	Larger values: Better for large, slowly varying backgrounds
•	Click the button Preview Current Image to see the effect on the selected image

#### Optional Filters (Recommended)

Denoising
•	Check the Enable Denoising checkbox
•	Adjust Denoising Size (default: 3)
•	Uses median filtering to reduce noise

Sharpening
•	Check the Enable Sharpening checkbox
•	Adjust Sharpening Amount (default: 1.3)
•	Enhances edges and fine details
*It is highly recommended to use a combination of these methods and previewing the results to create the best possible image

Processing Images
When the image preview is acceptable:
9.	Click Process Selected button
10.	Monitor progress in the log window. It may take some time to clean the images.

After processing, the image will have a green dot next to the name and the image will appear under the “Processed” tab.

#### Step 3: Batch Processing

This tab allows you to manually mark microglia somas, define cell boundaries, and QA generated masks.

Marking Soma Locations
11.	Click the Pick Soma (All Images) button
12.	Click on the center of each microglia cell body. Be as close as possible to increase reproducibility of results.
13.	Red markers will appear at each clicked location
14.	On the keyboard, press Enter/Return when done


Drawing Cell Masks
After marking somas, you need to define the boundary of each cell’s soma:
15.	Click the Outline Somas (All) button
16.	The first soma you selected should appear. Draw a polygon around the cell by clicking to create points. Note: More points will increase accuracy. On the mouse/keyboard,

•	Single Click: Add a point to the polygon
•	Double Click: Close the polygon
•	Remove Point: Click backspace to remove the latest point
•	Enter/Return: Confirm the current soma
•	Cancel: Exit mask drawing mode
•	
17.	Repeat for each soma

Setting Parameters
Before you proceed with mask generation, confirm that the pixel size (in micrometers/pixel) is correct. If not, update it as it will influence the calculations.
Reviewing Masks
18.	Click Generate Masks. This will create the masks. You will then have an option for pixel intensity cut off through the “Use minimum intensity threshold” box. If background cleaning did not do a good job, or if you want to decrease number of grey pixels, select this and select what value to use (30% is recommended). Smaller values increase the size of masks at the cost of accuracy. Set 0% to not use or deselect the box. 
19.	Click QA All Masks to display all generated masks for review
20.	Review each mask for quality. If it accurately covers the cell and its branches, 
click on the keyboard “A” to accept and “R” to reject. Rejecting a mask will move to a mask smaller than it for QA. This will exempt it form any morphology calculations. Accepting a mask will accept all masks smaller than it

Note: Mask generation is not perfect! Make sure that generated masks do not capture blurry areas of the microglia nor miss branches. This will skew the calculations. If in doubt, it is almost always best to reject the mask and either (A) re-process the image to improve the mask generation, or (B) capture another image

Calculating Simple Characteristics
21.	Again, ensure pixel size is correct!
22.	Click Calculate Simple Characteristics button. This can take a bit depending on the number of cells/complexity
23.	Enter animal name and treatment if not done in Step 8
24.	Results will be automatically saved in a .csv files in the output folder. Each image will receive its own .csv file and one .csv file named “combined_morphology_results.csv” with all the data

#### Calculated Parameters

The program calculates the following morphological parameters for each cell:
•	Roundness: Ratio of minor to major axis (0-1, where 1 is perfectly round)
•	Eccentricity: Ratio of major to minor axis (measures elongation)
•	Soma Area: Area of the cell body in μm²
•	Mask Area: Total area of the entire cell including processes in μm²
•	Perimeter: Perimeter of the cell mask in μm
•	Average Centroid Distance (formerly known as Cell Spread): Average distance from centroid to extremities in μm

Export and Results
Output Files
After processing, the program creates several output files in your selected output directory:

Processed Images
•	Format: [original_name]_processed.tif
•	Contains: Background-subtracted images with applied filters

Mask Images
•	Directory: masks/ subdirectory
•	Format: [image_name]_[soma_id]_mask.tif
•	Contains: Binary mask for each annotated cell

Soma Images
•	Directory: masks/ subdirectory
•	Format: [image_name]_[soma_id]_soma.tif
•	Contains: Binary mask for soma only

Results Files (CSV)
•	combined_morphology_results.csv: All results from all images in a single file
•	[image_name]_morphology_results.csv: Individual results for each image
•	mask_metadata.csv: Metadata linking masks to images and parameters (in masks/ directory)

#### CSV File Structure

The results CSV files contain the following columns:
•	image_name - Original image filename
•	animal_id - Animal identifier (if provided)
•	treatment - Treatment condition (if provided)
•	soma_id - Unique identifier for each soma (Soma_1, Soma_2, etc.)
•	soma_idx - Index of the soma (0-based)
•	All calculated morphological parameters (roundness, eccentricity, etc.)

### Tips and Best Practices

Image Quality
•	Use high-quality TIFF images with good contrast
•	Avoid over-processing images – processing images can increase accuracy on the soma and primary branches but often comes at the cost of smaller branches
•	Test different rolling ball radius values and additional processing combinations to find the optimal setting
•	Use the preview function to verify settings before batch processing

Annotation Accuracy
•	Take time to carefully mark soma centers - accuracy here improves downstream analysis
•	Include all visible processes when drawing masks
•	Be consistent in how you draw masks across all cells
•	Review all masks in the Batch Analysis tab before calculating parameters

Workflow Efficiency
•	Process similar images together with the same parameters
•	Save your work frequently - the program saves masks automatically
•	Organize your data with meaningful Animal IDs and Treatment labels
•	Keep track of pixel size settings for each microscope/objective combination

Data Management
•	Use descriptive filenames for your images
•	Keep raw and processed images in separate directories
•	Back up your mask files - they represent significant annotation time
•	Document your analysis parameters for reproducibility
•	Ensure enough disk space for generation of mask and soma images

Troubleshooting
Common Issues
Program won't start
•	Verify all dependencies are installed
•	Check Python version (3.7 or higher required)
•	Run from command line to see error messages

Images not loading
•	Ensure images are in TIFF format
•	Check file permissions
•	Verify images are not corrupted

Poor background subtraction results
•	Adjust rolling ball radius - try both smaller and larger values
•	Enable denoising for noisy images
•	Consider preprocessing images in another program first

Mask drawing not working
•	Ensure you've marked somas first
•	Try restarting the drawing if polygon looks incorrect
•	Remember to double-click to close polygons

Unexpected measurement values
•	Double-check pixel size setting - this is the most common cause
•	Verify mask quality in the Batch Analysis tab
•	Ensure masks fully encompass the cells

Program running slowly
•	Process fewer images at once
•	Close other applications
•	Consider using smaller image files if possible

Getting Help
If you encounter issues not covered here:
•	Check the log window for error messages
•	Document the steps that led to the problem
•	Note any error messages displayed

#### Conclusion

MMPS provides a comprehensive workflow for processing microscopy images and quantifying microglia morphology. By following this guide, you should be able to successfully:
•	Load and preprocess microscopy images
•	Manually annotate microglia somas and cell boundaries
•	Calculate morphological parameters for batch analysis
•	Export results with metadata for statistical analysis

For best results, take time to carefully annotate your images and verify the quality of your masks before running batch calculations. Consistent, accurate annotations lead to reliable, reproducible measurements.

Happy analyzing!
