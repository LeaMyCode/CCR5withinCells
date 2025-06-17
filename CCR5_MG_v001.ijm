input_path = getDirectory("Choose your data to be analyzed");
output_path = getDirectory("Select destination directory for your analyzed data");

fileList = getFileList(input_path) 

for (f = 0; f<fileList.length; f++){
		
		open(input_path + fileList[f]); 
		run("Z Project...", "projection=[Max Intensity]");
		Stack.getDimensions(width, height, channels, slices, frames); 
		title = getTitle();
		
		//Setting measurments
		run("Set Measurements...", "area mean min perimeter integrated redirect=None decimal=3");
		
		if (channels == 3) {
			run("Split Channels");
			selectWindow ("C1-" + title);
			rename("DAPI");
			selectWindow ("C2-" + title);
			rename("MG");
			selectWindow ("C3-" + title);
			rename("CCR5");
			
			//DAPI channel roi extraction
			selectWindow("DAPI");
			setAutoThreshold("Triangle dark");
			setOption("BlackBackground", false);
			run("Convert to Mask");
			run("Despeckle");
			waitForUser("Please correct the thresholding, then press ok.");
			run("Analyze Particles...", "size=20-500 add");
	    	roiManager('select', "*");
			roiManager("Save", output_path + title+ "-DAPI_ROI.zip");
			roiManager("reset");
			
			//Save thresholded DAPI
			selectWindow("DAPI");
			saveAs("PNG", output_path + title + "-DAPI_threshold.png");
			run("Close");
			
			//Make copy of MG to compare original and thresholded one
			selectWindow("MG");
			run("Duplicate...", "title=MG_copy");
			
			//IBA1 channel roi extraction
			selectWindow("MG");
			run("Enhance Contrast", "saturated=0.35");
			run("Apply LUT"); 
			setAutoThreshold("Li dark");
			setOption("BlackBackground", false);
			run("Convert to Mask");
			
			waitForUser("Please correct the thresholding, then press ok.");
			
			run("Analyze Particles...", "size=30-20000 add");
	    	roiManager('select', "*");
			roiManager("Save", output_path + title+ "-MG_ROI.zip");
			roiManager("reset");
			
			//Save thresholded IBA1
			selectWindow("MG");
			saveAs("PNG", output_path + title + "-MG_threshold.png");
			run("Close");
			
			//CCR5 processing
			selectWindow("CCR5");
			run("Duplicate...", "title=gaussian");
			//unsharp masks
			selectWindow("CCR5");
			run("Unsharp Mask...", "radius=3 mask=0.60");
			//gaussian blur
			selectWindow("gaussian");
			run("Gaussian Blur...", "sigma=25");
			//image calculator
			imageCalculator("Subtract create stack","CCR5", "gaussian");
			//Thresholding	
			selectWindow("Result of CCR5");
			setAutoThreshold("Triangle dark");
			setOption("BlackBackground", false);
			run("Convert to Mask");
			run("Watershed");
			//Analyze particles
			run("Analyze Particles...", "size= 0-infinity show=Nothing add");
			//Save 
			selectWindow("Result of CCR5");
			saveAs("PNG", output_path + title + "-CCR5_treshold.png");
			roiManager('select', "*");
			roiManager("Save", output_path + title+ "-CCR5_ROI.zip");
			
			//cleanup roimanager
			roiManager("reset");
			run("Close");
		
		}
			
		
		
		if (channels == 4) {
			run("Split Channels");
			selectWindow ("C1-" + title);
			rename("DAPI");
			selectWindow ("C2-" + title);
			rename("MG");
			selectWindow ("C3-" + title);
			rename("CCR5");
			selectWindow ("C4-" + title);
			run("Close");
			
			//DAPI channel roi extraction
			selectWindow("DAPI");
			run("Enhance Contrast", "saturated=0.35");
			setAutoThreshold("Triangle dark");
			setOption("BlackBackground", false);
			run("Convert to Mask");
			run("Despeckle");
			waitForUser("Please correct the thresholding, then press ok.");
			
			run("Analyze Particles...", "size=20-500 add");
	    	roiManager('select', "*");
			roiManager("Save", output_path + title+ "-DAPI_ROI.zip");
			roiManager("reset");
			
			//Save thresholded DAPI
			selectWindow("DAPI");
			saveAs("PNG", output_path + title + "-DAPI_threshold.png");
			run("Close");
			
			//Make copy of MG to compare original and thresholded one
			selectWindow("MG");
			run("Duplicate...", "title=MG_copy");
			
			//IBA1 channel roi extraction
			selectWindow("MG");
			run("Enhance Contrast", "saturated=0.35");
			run("Apply LUT"); 
			setAutoThreshold("Li dark");
			setOption("BlackBackground", false);
			run("Convert to Mask");
			
			waitForUser("Please correct the thresholding, then press ok.");
			
			run("Analyze Particles...", "size=30-1000 add");
	    	roiManager('select', "*");
			roiManager("Save", output_path + title+ "-MG_ROI.zip");
			roiManager("reset");
			
			//Save thresholded IBA1
			selectWindow("MG");
			saveAs("PNG", output_path + title + "-MG_threshold.png");
			run("Close");
			
			//CCR5 processing
			selectWindow("CCR5");
			run("Duplicate...", "title=gaussian");
			//unsharp masks
			selectWindow("CCR5");
			run("Unsharp Mask...", "radius=3 mask=0.60");
			//gaussian blur
			selectWindow("gaussian");
			run("Gaussian Blur...", "sigma=25");
			//image calculator
			imageCalculator("Subtract create stack","CCR5", "gaussian");
			//Thresholding	
			selectWindow("Result of CCR5");
			setAutoThreshold("Triangle dark");
			setOption("BlackBackground", false);
			run("Convert to Mask");
			run("Watershed");
			//Analyze particles
			run("Analyze Particles...", "size= 0-infinity show=Nothing add");
			//Save 
			selectWindow("Result of CCR5");
			saveAs("PNG", output_path + title + "-CCR5_treshold.png");
			roiManager('select', "*");
			roiManager("Save", output_path + title+ "-CCR5_ROI.zip");
			
			//cleanup roimanager
			roiManager("reset");
			run("Close");
			
			
			
		}
		
		
//Clean-up to prepare for next image
	roiManager("reset");
	run("Close All");
	run("Clear Results");
	close("*");
	
	if (isOpen("Log")) {
         selectWindow("Log");
         run("Close");
	}
	if (isOpen("Summary")) {
         selectWindow("Summary");
         run("Close");
	}
	
		
	}
print("Jeah, finished!");