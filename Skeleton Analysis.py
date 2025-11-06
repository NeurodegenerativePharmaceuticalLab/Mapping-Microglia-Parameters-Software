#@File(label="Masks Directory", style="directory") masksDir
#@File(label="Output Directory", style="directory") outputDir
#@Float(label="Pixel Size (µm/pixel)", value=0.316) pixelSize

from ij import IJ, ImagePlus
from ij.measure import Calibration, ResultsTable
from sc.fiji.analyzeSkeleton import AnalyzeSkeleton_

import os
import csv
import re

def analyzeSkeleton(maskPath, pixelSize, outputDirPath):
    """
    Analyze skeleton of mask image.
    """
    print("Processing: " + os.path.basename(maskPath))
    
    # Open mask
    mask = IJ.openImage(maskPath)
    if mask is None:
        print("  ERROR: Could not open mask")
        return None
    
    # Set calibration
    cal = Calibration(mask)
    cal.pixelWidth = pixelSize
    cal.pixelHeight = pixelSize
    cal.setUnit("micron")
    mask.setCalibration(cal)
    
   
    maskProcessor = mask.getProcessor()
    maskWidth = mask.getWidth()
    maskHeight = mask.getHeight()
    
    maskPixelCount = 0
    for y in range(maskHeight):
        for x in range(maskWidth):
            if maskProcessor.getPixel(x, y) > 0:
                maskPixelCount += 1
    
    maskArea = maskPixelCount * (pixelSize * pixelSize)
    
    # Measure other mask properties using ImageJ
    IJ.setThreshold(mask, 1, 255)
    IJ.run(mask, "Set Measurements...", "area perimeter shape redirect=None decimal=3")
    IJ.run(mask, "Measure", "")
    rt = ResultsTable.getResultsTable()
    
    maskPerimeter = rt.getValue("Perim.", 0)
    maskCircularity = rt.getValue("Circ.", 0)
    maskAR = rt.getValue("AR", 0)
    maskRound = rt.getValue("Round", 0)
    maskSolidity = rt.getValue("Solidity", 0)
    
    rt.reset()
    
    # Create skeleton using Skeletonize (2D/3D) plugin - CRITICAL for matching reference
    skel = mask.duplicate()
    IJ.run(skel, "Skeletonize (2D/3D)", "")
    
    # Clear any ROI selection before analysis
    IJ.run(skel, "Select None", "")
    
    # Save skeleton image
    # Extract cell name by removing _area###_mask.tif suffix (handles area values 300-800)
    baseName = os.path.basename(maskPath)
    cellName = re.sub(r'_area[3-8]\d{2}_mask\.tif$', '', baseName)
    
    # If pattern didn't match, try without .tif extension first
    if cellName == baseName:
        cellName = re.sub(r'_area\d+_mask\.tif$', '', baseName)
    
    # If still no match, just remove _mask.tif
    if cellName == baseName or cellName.endswith('_mask'):
        cellName = re.sub(r'_mask\.tif$', '', baseName)
    
    skelPath = os.path.join(outputDirPath, cellName + "_skeleton.tif")
    IJ.save(skel, skelPath)
    print("  Saved skeleton: " + os.path.basename(skelPath))
    
    # Analyze skeleton with SHORTEST_BRANCH pruning - CRITICAL for matching reference
    analyzer = AnalyzeSkeleton_()
    analyzer.setup("", skel)
    
    # Run analysis with pruning to match: run("Analyze Skeleton (2D/3D)", "prune=[shortest branch] calculate")
    # NOTE: silent=True is critical - displaying labeled skeletons changes the results!
    result = analyzer.run(
        AnalyzeSkeleton_.SHORTEST_BRANCH,  # pruning method - removes shortest dead-end branches iteratively
        True,   # prune ends - enable pruning
        True,   # calculate shortest path
        None,   # original image
        True,   # silent - MUST be True, displaying windows changes results
        False   # verbose
    )
    
    # Get results (all return arrays, one per skeleton)
    branches = result.getBranches()
    junctions = result.getJunctions()
    endPoints = result.getEndPoints()
    junctionVoxels = result.getJunctionVoxels()
    slabVoxels = result.getSlabs()
    triplePoints = result.getTriples()
    quadruplePoints = result.getQuadruples()
    maxBranchLength = result.getMaximumBranchLength()
    shortestPathList = result.getShortestPathList()
    
    # Extract metrics (index [0] for first/only skeleton)
    numBranches = int(branches[0]) if len(branches) > 0 else 0
    numSlabVoxels = int(slabVoxels[0]) if len(slabVoxels) > 0 else 0
    
    try:
        avgBranchLengthArray = result.getAverageBranchLength()
        if avgBranchLengthArray is not None and len(avgBranchLengthArray) > 0:
            avgBranchLength = float(avgBranchLengthArray[0])
        else:
            avgBranchLength = 0.0
    except:
        # Fallback: calculate manually if the method fails
        if numBranches > 0 and numSlabVoxels > 0:
            # Slab voxels are the "non-junction" skeleton pixels
            # Average branch length ≈ total slab length / number of branches
            avgBranchLength = (numSlabVoxels * pixelSize) / float(numBranches)
        else:
            avgBranchLength = 0.0
    
    # Get longest shortest path (in calibrated units)
    longestShortestPath = 0.0
    try:
        if shortestPathList and len(shortestPathList) > 0:
            if hasattr(shortestPathList[0], '__len__') and len(shortestPathList[0]) > 0:
                longestShortestPath = float(max(shortestPathList[0]))
            elif shortestPathList[0]:
                longestShortestPath = float(shortestPathList[0])
    except:
        longestShortestPath = 0.0
    
   
    if avgBranchLength > 0 and numBranches > 0:
        totalSkeletonLength = avgBranchLength * numBranches
    else:
        # Fallback: slab voxels * pixel size (underestimates slightly)
        totalSkeletonLength = numSlabVoxels * pixelSize
    

    skelProcessor = skel.getProcessor()
    skelWidth = skel.getWidth()
    skelHeight = skel.getHeight()
    
    skelPixelCount = 0
    for y in range(skelHeight):
        for x in range(skelWidth):
            if skelProcessor.getPixel(x, y) > 0:
                skelPixelCount += 1
    
    skeletonArea = skelPixelCount * (pixelSize * pixelSize)
    
    # Assemble metrics dictionary
    metrics = {
        'mask_file': os.path.basename(maskPath),
        'cell_name': cellName,
        'skeleton_file': os.path.basename(skelPath),
        'pixel_size_um': pixelSize,
        
        # Original mask measurements (FIX: use correct mask area)
        'mask_area_um2': maskArea,
        'mask_perimeter_um': maskPerimeter,
        'mask_circularity': maskCircularity,
        'mask_aspect_ratio': maskAR,
        'mask_roundness': maskRound,
        'mask_solidity': maskSolidity,
        
        # Skeleton measurements
        'num_branches': numBranches,
        'num_junctions': int(junctions[0]) if len(junctions) > 0 else 0,
        'num_end_points': int(endPoints[0]) if len(endPoints) > 0 else 0,
        'num_junction_voxels': int(junctionVoxels[0]) if len(junctionVoxels) > 0 else 0,
        'num_slab_voxels': numSlabVoxels,
        'num_triple_points': int(triplePoints[0]) if len(triplePoints) > 0 else 0,
        'num_quadruple_points': int(quadruplePoints[0]) if len(quadruplePoints) > 0 else 0,
        'max_branch_length_um': float(maxBranchLength[0]) if len(maxBranchLength) > 0 else 0,
        'avg_branch_length_um': avgBranchLength,  # FIXED
        'longest_shortest_path_um': longestShortestPath,
        'total_skeleton_length_um': totalSkeletonLength,  # FIXED
        'skeleton_area_um2': skeletonArea,  # FIXED
    }
    
    # Calculate branching density (skeleton area / mask area)
    if maskArea > 0:
        metrics['branching_density'] = skeletonArea / maskArea
    else:
        metrics['branching_density'] = 0
    
    mask.close()
    skel.close()
    
    print("  SUCCESS: " + str(numBranches) + " branches, " + 
          str(metrics['num_junctions']) + " junctions, " +
          str(numSlabVoxels) + " slab voxels")
    print("  Mask area: " + str(round(maskArea, 2)) + " um^2")
    print("  Skeleton area: " + str(round(skeletonArea, 2)) + " um^2")
    print("  Avg branch length: " + str(round(avgBranchLength, 2)) + " um")
    print("  Total skeleton length: " + str(round(totalSkeletonLength, 2)) + " um")
    
    return metrics


def main():
    print("=" * 60)
    print("SKELETON ANALYSIS - BATCH PROCESSOR")
    print("=" * 60)
    
    masksDirPath = str(masksDir)
    outputDirPath = str(outputDir)
    
    # Find mask files
    maskFiles = [f for f in os.listdir(masksDirPath) if f.endswith('_mask.tif')]
    
    if len(maskFiles) == 0:
        print("ERROR: No mask files found")
        return
    
    print("Found " + str(len(maskFiles)) + " mask files")
    print("Pixel size: " + str(pixelSize) + " um/pixel")
    print("")
    
    allResults = []
    
    for maskFile in maskFiles:
        maskPath = os.path.join(masksDirPath, maskFile)
        
        metrics = analyzeSkeleton(maskPath, pixelSize, outputDirPath)
        
        if metrics is not None:
            allResults.append(metrics)
    
    # Save results
    if len(allResults) > 0:
        outputPath = os.path.join(outputDirPath, "Skeleton_Analysis_Results.csv")
        
        # Define column order
        idCols = ['cell_name', 'mask_file', 'skeleton_file', 'pixel_size_um']
        maskCols = ['mask_area_um2', 'mask_perimeter_um', 'mask_circularity', 
                    'mask_aspect_ratio', 'mask_roundness', 'mask_solidity']
        skelCols = ['num_branches', 'num_junctions', 'num_end_points', 
                    'num_junction_voxels', 'num_slab_voxels', 'num_triple_points',
                    'num_quadruple_points', 'max_branch_length_um', 
                    'avg_branch_length_um', 'longest_shortest_path_um',
                    'total_skeleton_length_um', 'skeleton_area_um2', 'branching_density']
        
        columns = idCols + maskCols + skelCols
        
        with open(outputPath, 'w') as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writeheader()
            writer.writerows(allResults)
        
        print("\n" + "=" * 60)
        print("COMPLETED: " + str(len(allResults)) + " cells processed")
        print("Results: " + outputPath)
        print("Skeleton images saved to: " + outputDirPath)
        print("=" * 60)
    else:
        print("\nERROR: No cells processed successfully")


if __name__ == '__main__':
    main()
