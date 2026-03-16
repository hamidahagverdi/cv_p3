<h1 align="center">Computer Vision Assignment 3</h1>

<h3 align="center">Noise Removal, Speckle Denoising, and MRI Visualization</h3>

<p align="center">
  Python application for chemical noise removal, speckle noise reduction, and MRI DICOM visualization.
</p>

<br>

<h2>Overview</h2>

<p>
This project was implemented in <b>Python</b> as a runnable command-line application for three image processing tasks:
</p>

<ul>
  <li><b>Noise removal and reconstruction</b> on chemical images</li>
  <li><b>Speckle noise removal</b> using classical image processing techniques</li>
  <li><b>MRI DICOM visualization and metadata inspection</b></li>
</ul>

<p>
The project follows the assignment requirements:
</p>

<ul>
  <li>Python programming language</li>
  <li>No machine learning algorithms for denoising tasks</li>
  <li>Separate folders for original and output images</li>
  <li>Runnable application instead of a notebook</li>
</ul>

<br>

<h2>Project Structure</h2>

```text
cv_p3/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── src/
│   ├── chemical_noise.py
│   ├── speckle_noise.py
│   ├── mri_viz.py
│   └── utils.py
│
├── data/
│   ├── original/
│   │   ├── chemical/
│   │   │   ├── inchi1.png
│   │   │   ├── inchi10.png
│   │   │   └── inchi8.png
│   │   └── speckle/
│   │       ├── 1.jpeg
│   │       ├── 5.png
│   │       └── 6.jpeg
│   └── mri/
│       └── E1154S7I.dcm
│
└── outputs/
    ├── chemical/
    ├── speckle/
    └── mri/
```

<br>

<h2>Requirements</h2>

<p>Install the required libraries with:</p>

```bash
pip install -r requirements.txt
```

<p><b>Main libraries used:</b></p>

<ul>
  <li>numpy</li>
  <li>matplotlib</li>
  <li>opencv-python</li>
  <li>scikit-image</li>
  <li>scipy</li>
  <li>pydicom</li>
  <li>PyWavelets</li>
</ul>

<br>

<h2>How to Run</h2>

<h3>Run chemical noise removal only</h3>

```bash
python app.py chemical --input .\data\original\chemical --output .\outputs\chemical
```

<h3>Run speckle denoising only</h3>

```bash
python app.py speckle --input .\data\original\speckle --output .\outputs\speckle
```

<h3>Run MRI visualization only</h3>

```bash
python app.py mri --input .\data\mri\E1154S7I.dcm --output .\outputs\mri
```

<h3>Run all tasks</h3>

```bash
python app.py all --chemical .\data\original\chemical --speckle .\data\original\speckle --mri .\data\mri\E1154S7I.dcm
```

<br>

<h2>Selected Images</h2>

<p>
The assignment required selecting <b>3 images randomly</b> for the experiments.
</p>

<h3>Chemical images</h3>

<ul>
  <li><code>inchi1.png</code></li>
  <li><code>inchi10.png</code></li>
  <li><code>inchi8.png</code></li>
</ul>

<h3>Speckle images</h3>

<ul>
  <li><code>1.jpeg</code></li>
  <li><code>5.png</code></li>
  <li><code>6.jpeg</code></li>
</ul>

<br>

<h2>Task 1: Noise Removal and Reconstruction</h2>

<h3>Objective</h3>

<p>
The goal of this task was to remove noise from chemical images and reconstruct meaningful structures such as lines, symbols, and letters.
</p>

<h3>Filters Applied</h3>

<ul>
  <li>Mean blur</li>
  <li>Gaussian blur</li>
  <li>Median filter</li>
  <li>Bilateral filter</li>
  <li>Non-local means</li>
</ul>

<h3>Summary of Results</h3>

<ul>
  <li><code>inchi1.png</code>: best = <b>bilateral_filter</b>, worst = <b>median_filter</b></li>
  <li><code>inchi10.png</code>: best = <b>mean_blur</b>, worst = <b>nl_means</b></li>
  <li><code>inchi8.png</code>: best = <b>bilateral_filter</b>, worst = <b>median_filter</b></li>
</ul>

<h3>Analysis</h3>

<p>
Among the tested methods, <b>bilateral filtering</b> gave the best overall performance for the selected chemical images. It reduced noise while preserving important edges and thin structural details, which is essential for reconstructing characters and line-based shapes.
</p>

<p>
For one image, <code>inchi10.png</code>, <b>mean blur</b> achieved the best result, which suggests that this image responded better to stronger smoothing. However, across the selected samples, bilateral filtering was the most reliable method.
</p>

<p>
The weakest results were produced by <b>median filter</b> and <b>non-local means</b> in these experiments. In some cases, they either oversmoothed the image or failed to preserve the fine structures required for reconstruction.
</p>

<h3>Conclusion</h3>

<p>
For the chemical noise task, <b>bilateral filter</b> was the best overall method for the selected images.
</p>

<br>

<h2>Task 2: Speckle Removal</h2>

<h3>Objective</h3>

<p>
The goal of this task was to remove speckle noise from the selected images using classical image processing techniques only.
</p>

<h3>Methods Applied</h3>

<ul>
  <li>Bilateral filter</li>
  <li>Lee filter</li>
  <li>Total variation denoising (<code>tv_chambolle</code>)</li>
  <li>Gaussian blur</li>
  <li>Median filter</li>
  <li>Log-bilateral filtering</li>
</ul>

<h3>Summary of Results</h3>

<ul>
  <li><code>1.jpeg</code>: best = <b>bilateral_filter</b>, worst = <b>log_bilateral</b></li>
  <li><code>5.png</code>: best = <b>log_bilateral</b>, worst = <b>bilateral_filter</b></li>
  <li><code>6.jpeg</code>: best = <b>log_bilateral</b>, worst = <b>lee_filter</b></li>
</ul>

<h3>Analysis</h3>

<p>
For the speckle images, <b>log-bilateral filtering</b> performed best overall because it achieved the top result in two out of the three selected images. This is a reasonable outcome because speckle is multiplicative noise, and processing in the log domain often improves denoising quality.
</p>

<p>
<b>Bilateral filtering</b> also performed well and was the best method for one image. It preserved edges more effectively than simple smoothing filters.
</p>

<p>
The weakest method was not the same for every image, which indicates that denoising performance depends on the image content and the strength of the noise. Still, the general pattern showed that edge-preserving approaches were more effective than basic smoothing.
</p>

<h3>Conclusion</h3>

<p>
For the speckle removal task, <b>log-bilateral filtering</b> was the best overall method for the selected images.
</p>

<br>

<h2>Task 3: MRI Data Visualization</h2>

<h3>Objective</h3>

<p>
The goal of this task was to read a DICOM MRI file, extract its metadata, and visualize different layers of the MRI scan.
</p>

<h3>Extracted Metadata</h3>

<ul>
  <li><b>Modality:</b> MR</li>
  <li><b>StudyDescription:</b> </li>
  <li><b>SeriesDescription:</b> Unknown</li>
  <li><b>Rows:</b> 512</li>
  <li><b>Columns:</b> 512</li>
  <li><b>NumberOfSlicesOrFrames:</b> 76</li>
  <li><b>PixelSpacing:</b> Unknown</li>
  <li><b>SliceThickness:</b> Unknown</li>
  <li><b>BitsStored:</b> 16</li>
  <li><b>PhotometricInterpretation:</b> MONOCHROME2</li>
  <li><b>Manufacturer:</b> </li>
  <li><b>MagneticFieldStrength:</b> Unknown</li>
</ul>

<h3>Analysis</h3>

<p>
The program successfully loaded the MRI DICOM file and extracted the available metadata. The image volume contains <b>76 slices/frames</b>, each with a resolution of <b>512 × 512</b> pixels. The MRI visualization module displayed different layers of the scan and saved the generated outputs.
</p>

<p>
This part satisfies the assignment requirement to both describe the contents of the file and visualize different layers of the MRI image.
</p>

<h3>Conclusion</h3>

<p>
The MRI visualization task was completed successfully.
</p>

<br>

<h2>Output</h2>

<p>All generated results are stored in separate folders:</p>

<ul>
  <li><code>outputs/chemical/</code></li>
  <li><code>outputs/speckle/</code></li>
  <li><code>outputs/mri/</code></li>
</ul>

<p>
These folders contain processed images, visual comparisons, and summary files generated by the program.
</p>

<br>

<h2>Notes</h2>

<ul>
  <li>The project was implemented as a <b>runnable Python application</b>, not a notebook.</li>
  <li>No machine learning algorithms were used for the denoising tasks.</li>
  <li>Original images and output images are stored in separate folders as required.</li>
  <li>If the MRI file is too large for GitHub, it should be stored externally and linked below.</li>
</ul>

<br>

<h2>Author</h2>

<p><b>Hamida Hagverdiyeva</b></p>

