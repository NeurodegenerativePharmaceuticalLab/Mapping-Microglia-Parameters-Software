#@ File (label="Select folder with original mask images", style="directory") inputDir
#@ File (label="Select output folder (will create subfolders)", style="directory") outputDir
#@ String (label="Microns per pixel", value="0.316", required=false) micronsPerPixel
#@ Integer (label="Batch size", value=25) batchSize

"""
FracLac Preparation

This script:
1. Cleans all masks (ensures binary, removes metadata)
2. Saves to "FracLacImages" folder
3. Creates batches in "FracLacBatch" folder
4. Ready to process in FracLac!
"""

import os
import shutil
from ij import IJ

def main():
    inputPath = str(inputDir)
    outputPath = str(outputDir)
    scale = str(micronsPerPixel) if micronsPerPixel else None
    
    print("\n" + "=" * 80)
    print("FRACLAC PREPARATION - ALL-IN-ONE")
    print("=" * 80)
    print("Input: " + inputPath)
    print("Output: " + outputPath)
    if scale and scale.strip():
        print("Scale: " + scale + " um/pixel")
    print("Batch size: " + str(batchSize))
    
    # Create output folders
    cleanedFolder = os.path.join(outputPath, "FracLacImages")
    batchFolder = os.path.join(outputPath, "FracLacBatch")
    dataFolder = os.path.join(batchFolder, "FracLacData")
    
    if not os.path.exists(cleanedFolder):
        os.makedirs(cleanedFolder)
    
    if not os.path.exists(batchFolder):
        os.makedirs(batchFolder)
    
    if not os.path.exists(dataFolder):
        os.makedirs(dataFolder)
    
    print("\nFracLacImages: " + cleanedFolder)
    print("FracLacBatch: " + batchFolder)
    print("FracLacData: " + dataFolder)
    
    # Get scale value
    scaleValue = None
    if scale and scale.strip():
        try:
            scaleValue = float(scale)
            print("\nScale: 1 pixel = " + str(scaleValue) + " um")
        except:
            print("\nWARNING: Invalid scale value")
    
    # Find all TIFF files
    print("\n" + "=" * 80)
    print("STEP 1: CLEANING MASKS")
    print("=" * 80)
    
    allFiles = []
    for filename in os.listdir(inputPath):
        if filename.lower().endswith(('.tif', '.tiff')):
            filepath = os.path.join(inputPath, filename)
            if os.path.isfile(filepath):
                allFiles.append((filename, filepath))
    
    print("Found " + str(len(allFiles)) + " TIFF files")
    
    if len(allFiles) == 0:
        print("\nERROR: No TIFF files found!")
        return
    
    # Process each file
    print("\nCleaning and saving binary TIFFs...")
    
    cleaned = 0
    failed = 0
    
    for i, (filename, filepath) in enumerate(allFiles):
        if (i + 1) % 100 == 0:
            print("  Processing " + str(i + 1) + "/" + str(len(allFiles)) + "...")
        
        try:
            # Open image
            imp = IJ.openImage(filepath)
            if not imp:
                print("  ERROR: Cannot open " + filename)
                failed += 1
                continue
            
            # Make sure it's 8-bit
            if imp.getBitDepth() != 8:
                IJ.run(imp, "8-bit", "")
            
            # Make binary
            IJ.run(imp, "Make Binary", "")
            
            # Set scale if provided - use Set Scale command for FracLac compatibility
            if scaleValue:
                # Calculate: if 1 pixel = scaleValue um, then distance in pixels = 1/scaleValue
                # For "known distance" we use 1 pixel = scaleValue um
                # So we set: 1 pixel = scaleValue um
                IJ.run(imp, "Set Scale...", 
                       "distance=1 known=" + str(scaleValue) + " unit=um")
            
            # Save as clean TIFF
            outputFile = os.path.join(cleanedFolder, filename)
            IJ.save(imp, outputFile)
            
            imp.close()
            cleaned += 1
            
        except Exception as e:
            print("  ERROR processing " + filename + ": " + str(e))
            failed += 1
    
    print("\n" + "-" * 80)
    print("CLEANING COMPLETE")
    print("-" * 80)
    print("Successfully cleaned: " + str(cleaned))
    print("Failed: " + str(failed))
    print("Output: " + cleanedFolder)
    
    if cleaned == 0:
        print("\nERROR: No files were cleaned!")
        return
    
    # Now create batches
    print("\n" + "=" * 80)
    print("STEP 2: CREATING BATCHES")
    print("=" * 80)
    
    # Get list of cleaned files
    cleanedFiles = []
    for filename in os.listdir(cleanedFolder):
        if filename.lower().endswith(('.tif', '.tiff')):
            filepath = os.path.join(cleanedFolder, filename)
            if os.path.isfile(filepath):
                cleanedFiles.append((filename, filepath))
    
    cleanedFiles.sort()
    
    print("Files to batch: " + str(len(cleanedFiles)))
    
    # Calculate number of batches
    numBatches = (len(cleanedFiles) + batchSize - 1) // batchSize
    
    print("Will create " + str(numBatches) + " batches of ~" + str(batchSize) + " files each")
    
    # Create batches
    for batchNum in range(numBatches):
        startIdx = batchNum * batchSize
        endIdx = min(startIdx + batchSize, len(cleanedFiles))
        batchFiles = cleanedFiles[startIdx:endIdx]
        
        batchName = "Batch_{:03d}".format(batchNum + 1)
        batchPath = os.path.join(batchFolder, batchName)
        
        if not os.path.exists(batchPath):
            os.makedirs(batchPath)
        
        # Copy files to batch folder
        for filename, filepath in batchFiles:
            dstPath = os.path.join(batchPath, filename)
            if not os.path.exists(dstPath):
                shutil.copy2(filepath, dstPath)
        
        if (batchNum + 1) % 10 == 0 or batchNum == 0:
            print("  Created " + batchName + ": " + str(len(batchFiles)) + " files")
    
    print("\n" + "-" * 80)
    print("BATCHING COMPLETE")
    print("-" * 80)
    print("Total batches: " + str(numBatches))
    print("Batch location: " + batchFolder)
    
    # Summary
    print("\n" + "=" * 80)
    print("ALL DONE!")
    print("=" * 80)
    print("\nFOLDER STRUCTURE:")
    print("  " + outputPath + "/")
    print("    ├── FracLacImages/       (" + str(cleaned) + " cleaned binary TIFFs)")
    print("    └── FracLacBatch/        (" + str(numBatches) + " batch folders)")
    print("          ├── FracLacData/   (PUT FRACLAC RAW OUTPUT HERE)")
    print("          ├── Batch_001/     (~" + str(batchSize) + " files)")
    print("          ├── Batch_002/")
    print("          └── ...")
    
    print("\n" + "=" * 80)
    print("NEXT STEPS:")
    print("=" * 80)
    print("\n1. PROCESS EACH BATCH IN FRACLAC:")
    print("\n   For each Batch_XXX folder:")
    print("   a. Open FracLac (Plugins > Fractal Analysis > FracLac)")
    print("   b. Click 'BC' button")
    print("   c. Configure options:")
    print("      - UNCHECK 'use legacy mode'")
    print("      - CHECK 'results' in FILES")
    print("      - CHECK 'metrics' for HULL AND CIRCLE")
    print("      - Click OK")
    print("   d. Make sure 'Db' is selected")
    print("   e. Click 'Batch'")
    print("   f. Select the batch folder (e.g., Batch_001)")
    print("   g. Select SAME folder again (FracLac asks twice)")
    print("   h. Press Cmd+A (or Ctrl+A) to SELECT ALL FILES")
    print("   i. Click 'Open'")
    print("   j. Wait for FracLac to finish")
    print("   k. FracLac creates output folder with timestamp")
    print("   l. MOVE/COPY that output folder to FracLacData/")
    print("\n2. REPEAT FOR ALL " + str(numBatches) + " BATCHES")
    print("   (Move each FracLac output to FracLacData/)")
    print("\n3. COMBINE RESULTS:")
    print("   Run 'Combine_FracLac_Results.py'")
    print("   - Input: " + dataFolder)
    print("   - Output: Where to save final CSV")
    print("\n" + "=" * 80)
    
    # Show completion dialog
    from ij.gui import GenericDialog
    gd = GenericDialog("FracLac Preparation Complete")
    
    message = "Preparation complete!\n\n"
    message += "Cleaned files: " + str(cleaned) + "\n"
    message += "Batches created: " + str(numBatches) + "\n"
    message += "Files per batch: ~" + str(batchSize) + "\n\n"
    message += "Folder structure:\n"
    message += outputPath + "/\n"
    message += "  FracLacImages/ (cleaned TIFFs)\n"
    message += "  FracLacBatch/\n"
    message += "    FracLacData/ (move outputs here!)\n"
    message += "    Batch_XXX/ (process in FracLac)\n\n"
    message += "Next: Process batches in FracLac,\n"
    message += "move outputs to FracLacData/"
    
    gd.addMessage(message)
    gd.showDialog()

if __name__ == '__main__' or __name__ == '__builtin__':
    main()
