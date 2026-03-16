# Report

## 1. Noise Removal and Reconstruction

For this experiment, three images were selected randomly from the `chemical` dataset. The goal was to remove noise and reconstruct important structures such as letters, symbols, and thin lines.

The following filters were tested:

- Mean blur
- Gaussian blur
- Median filter
- Bilateral filter
- Non-local means

After denoising, shape reconstruction was performed using Otsu thresholding followed by morphological opening and closing.

### Observations
The most successful filters were usually **median filter** and **non-local means**. These methods removed noise while preserving important boundaries and line structures. In contrast, **mean blur** produced the weakest result because it oversmoothed the image and reduced the visibility of small details.

### Conclusion
For chemical-like symbolic images, filters that preserve edges are more appropriate than simple averaging methods. Morphological post-processing also improved the continuity and readability of the reconstructed structures.

---

## 2. Speckle Removal

For the speckle dataset, three images were selected randomly and processed with the following techniques:

- Gaussian blur
- Median filter
- Bilateral filter
- Lee filter
- Total variation denoising
- Log-domain bilateral filtering

### Observations
The strongest results were generally produced by **Lee filter** and **log-domain bilateral filtering**, because they reduced speckle noise while keeping structural edges relatively sharp. The weakest method was usually **Gaussian blur**, which removed details together with the noise.

### Conclusion
Since speckle is multiplicative noise, it requires methods that preserve local structure instead of uniform smoothing. Classical edge-aware filtering is more effective than basic blur-based methods.

---

## 3. MRI Data Visualization

The MRI task was completed using the `pydicom` library. The program read the DICOM file, extracted the metadata, and visualized different image layers.

### Extracted information
The code describes:
- modality
- study and series information
- image dimensions
- slice count
- spacing information
- other technical metadata

### Visualization
The program generated:
- a slice grid showing several MRI layers
- orthogonal anatomical views when a full volume was available

### Conclusion
The MRI visualization task demonstrated how DICOM files can be programmatically inspected and visualized. This is useful for understanding both the structure of medical image data and the metadata attached to it.

---

## 4. Overall Conclusion

This assignment demonstrates that different noise types require different processing strategies. For symbolic noisy images, edge-preserving denoising and morphology provide the most useful reconstruction. For speckle noise, specialized filters such as Lee filter outperform basic smoothing. For MRI data, DICOM parsing and slice visualization allow both metadata inspection and intuitive image exploration.
