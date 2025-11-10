#@ File (label="Select FracLacBatch folder (contains FracLacData)", style="directory") batchDir
#@ File (label="Select output folder for combined CSV", style="directory") outputDir

"""
Combine FracLac Batch Results

After processing all batches in FracLac and moving outputs to FracLacData/,
run this to combine all results into a single CSV file.

Looks in: FracLacBatch/FracLacData/ for all FracLac output folders
"""

import os
import csv
import re

def main():
    batchPath = str(batchDir)
    outputPath = str(outputDir)
    
    # Look for FracLacData folder inside the batch folder
    dataPath = os.path.join(batchPath, "FracLacData")
    
    print("\n" + "=" * 80)
    print("COMBINING FRACLAC BATCH RESULTS")
    print("=" * 80)
    print("Batch folder: " + batchPath)
    print("Data folder: " + dataPath)
    print("Output: " + outputPath)
    
    # Check if FracLacData exists
    if not os.path.exists(dataPath):
        print("\nERROR: FracLacData folder not found!")
        print("Expected location: " + dataPath)
        print("\nMake sure you:")
        print("  1. Selected the FracLacBatch folder (not FracLacData)")
        print("  2. Have moved FracLac outputs to FracLacData/")
        
        from ij.gui import GenericDialog
        gd = GenericDialog("Error")
        gd.addMessage("FracLacData folder not found!\n\n" +
                     "Expected: " + dataPath + "\n\n" +
                     "Make sure FracLac outputs are in FracLacData/")
        gd.showDialog()
        return
    
    # Column mapping
    column_map = {
        '6.': 'fractal_dimension',
        '87.': 'lacunarity',
        '131.': 'density',
        '132.': 'span_ratio',
        '134.': 'maximum_span_across_hull',
        '135.': 'convex_hull_area',
        '136.': 'convex_hull_perimeter',
        '137.': 'convex_hull_circularity',
        '140.': 'maximum_radius_from_hulls_centre_of_mass',
        '141.': 'max_min_radii',
        '142.': 'cv_for_all_radii',
        '143.': 'mean_radius',
        '145.': 'diameter_of_bounding_circle',
        '146.': 'maximum_radius_from_circles_centre',
        '147.': 'max_min_radii_from_circles_centre',
        '148.': 'cv_for_all_radii_from_circles_centre',
        '149.': 'mean_radius_from_circles_centre',
    }
    
    # Find all FracLac output folders in FracLacData
    print("\nSearching for FracLac output folders in FracLacData...")
    fracLacFolders = []
    
    for item in os.listdir(dataPath):
        itemPath = os.path.join(dataPath, item)
        if os.path.isdir(itemPath):
            # Look for Box Count Summary files
            hasBoxCount = False
            try:
                for filename in os.listdir(itemPath):
                    if ('box' in filename.lower() and 
                        'count' in filename.lower() and 
                        'summary' in filename.lower()):
                        hasBoxCount = True
                        break
            except:
                pass
            
            if hasBoxCount:
                fracLacFolders.append(itemPath)
                print("  Found: " + os.path.basename(itemPath))
    
    print("\nTotal FracLac output folders: " + str(len(fracLacFolders)))
    
    if len(fracLacFolders) == 0:
        print("\nERROR: No FracLac output folders found!")
        print("Make sure you've:")
        print("  1. Processed batches with FracLac")
        print("  2. Moved output folders to: " + dataPath)
        
        from ij.gui import GenericDialog
        gd = GenericDialog("Error")
        gd.addMessage("No FracLac outputs found!\n\n" +
                     "Location checked:\n" + dataPath + "\n\n" +
                     "Make sure outputs are there.")
        gd.showDialog()
        return
    
    # Process each folder
    print("\n" + "=" * 80)
    print("PROCESSING FOLDERS")
    print("=" * 80)
    
    allData = {}
    
    for i, folder in enumerate(sorted(fracLacFolders)):
        print("\n[" + str(i + 1) + "/" + str(len(fracLacFolders)) + "] " + os.path.basename(folder))
        
        # Find Box Count Summary file
        boxCountFile = None
        for filename in os.listdir(folder):
            if ('box' in filename.lower() and 
                'count' in filename.lower() and 
                'summary' in filename.lower() and
                filename.lower().endswith('.txt')):
                boxCountFile = os.path.join(folder, filename)
                break
        
        if not boxCountFile:
            print("  WARNING: No Box Count Summary file found")
            continue
        
        print("  File: " + os.path.basename(boxCountFile))
        
        # Process file
        folderData = processFracLacFile(boxCountFile, column_map)
        
        print("  Extracted " + str(len(folderData)) + " cells")
        
        # Merge into allData
        for filename, measurements in folderData.items():
            if filename in allData:
                allData[filename].update(measurements)
            else:
                allData[filename] = measurements
    
    print("\n" + "=" * 80)
    print("DATA EXTRACTION COMPLETE")
    print("=" * 80)
    print("Total unique cells: " + str(len(allData)))
    
    if len(allData) == 0:
        print("\nERROR: No data extracted!")
        return
    
    # Write combined CSV
    outputFile = os.path.join(outputPath, "FracLac_Combined_Results.csv")
    
    print("\nWriting CSV...")
    
    # Get all column names
    allColumns = set()
    for data in allData.values():
        allColumns.update(data.keys())
    allColumns.discard('filename')
    
    columnOrder = ['filename'] + sorted(allColumns)
    
    with open(outputFile, 'w') as f:
        writer = csv.DictWriter(f, fieldnames=columnOrder, extrasaction='ignore')
        writer.writeheader()
        for filename in sorted(allData.keys()):
            writer.writerow(allData[filename])
    
    print("\n" + "=" * 80)
    print("SUCCESS!")
    print("=" * 80)
    print("Output file: " + outputFile)
    print("Total cells: " + str(len(allData)))
    print("Measurements per cell: " + str(len(columnOrder) - 1))
    print("=" * 80)
    
    # Show dialog
    from ij.gui import GenericDialog
    gd = GenericDialog("Combination Complete")
    
    message = "Successfully combined batch results!\n\n"
    message += "Total cells: " + str(len(allData)) + "\n"
    message += "Measurements: " + str(len(columnOrder) - 1) + "\n\n"
    message += "Output file:\n" + os.path.basename(outputFile) + "\n\n"
    message += "Location:\n" + outputPath
    
    gd.addMessage(message)
    gd.showDialog()


def processFracLacFile(boxCountFile, column_map):
    """Process one Box Count Summary file"""
    data = {}
    
    try:
        with open(boxCountFile, 'r') as f:
            reader = csv.DictReader(f, delimiter='\t')
            fieldnames = reader.fieldnames
            
            # Build actual column mapping
            actualColumns = {}
            for pattern, name in column_map.items():
                for col in fieldnames:
                    if col.startswith(pattern):
                        actualColumns[col] = name
                        break
            
            # Read rows
            for row in reader:
                filename = extractFilenameFromRow(row)
                
                if filename not in data:
                    data[filename] = {'filename': filename}
                
                # Extract measurements
                for col, newName in actualColumns.items():
                    if col in row and row[col]:
                        value = row[col]
                        if value and value != 'Not Calculated' and value.strip():
                            data[filename][newName] = value
        
    except Exception as e:
        print("  ERROR: " + str(e))
    
    return data


def extractFilenameFromRow(row):
    """Extract filename from FracLac row"""
    # Check first column (usually has filename)
    for key, value in row.items():
        if key.startswith('1.'):
            return cleanFilename(value)
    
    # Search for _mask in any field
    for value in row.values():
        value_str = str(value)
        if '_mask' in value_str.lower() or '.tif' in value_str.lower():
            result = cleanFilename(value_str)
            if result and not result.startswith("unknown"):
                return result
    
    return "unknown"


def cleanFilename(value):
    """Clean FracLac's filename format"""
    if not value:
        return "unknown"
    
    value = str(value).strip()
    
    # Remove FracLac markers if present
    markers = ['ImageDescription', 'Software', 'tifffile']
    
    for marker in markers:
        if marker in value:
            before_marker = value.split(marker)[0]
            # FracLac often duplicates filename
            half_len = len(before_marker) // 2
            filename = before_marker[:half_len]
            
            match = re.search(r'(.+?_mask)\.?tif', filename, re.IGNORECASE)
            if match:
                return match.group(1) + '.tif'
    
    # Try direct match
    match = re.search(r'(.+?_mask)\.?tif', value, re.IGNORECASE)
    if match:
        return match.group(1) + '.tif'
    
    # Try to extract any .tif filename
    match = re.search(r'([^/\\]+\.tif)', value, re.IGNORECASE)
    if match:
        return match.group(1)
    
    return "unknown_" + value[:30]


if __name__ == '__main__' or __name__ == '__builtin__':
    main()
