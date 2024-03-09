# GamryParser User Guide

## System Requirements
- **Python:** This program requires Python to be installed on your system. If you haven't installed Python, please visit [Python's official website](https://www.python.org/downloads/) to download and install it.

## Getting Started
### Running the Program
#### From the command line or terminal
1. Open a new command line or terminal window
2. Navigate to the folder containing the GamryParser folder. This can be done by using the command <pre lang="bash"><code>cd filepath (example: 'cd C://My PC/Desktop/GamryParser')</code></pre> If your the last word in your terminal window is the directory you are in. For example if you are in Desktop and GamryParser is saved to your desktop, using <pre lang="bash"><code> cd GamryParser</code></pre>will enter open the GamryParser folder.
3. Once in the GamryParser folder, the command <pre lang="bash"><code>python main.py</code></pre> will run the program.

### Selecting a File
Upon running `main.py`, a popup window will appear, prompting you to select a file for analysis.

## Choosing Analysis Type
After selecting a file, you will be asked whether you want to:
- Analyze just the selected file.
- Analyze all files in the containing folder.

### Analyzing a Single File
If you choose to analyze a single file:
1. A dialog will prompt you to choose a location to save the output file.
2. Specify the desired save location, and the program will process the file and save the analysis there.

### Analyzing All Files in a Folder
If you choose to analyze all files in the folder:
1. The program will automatically process each file in the same folder.
2. It will save the analysis results in the same folder, naming each output file corresponding to its original file.

## Output Format
The program outputs the analysis results in a CSV format, convenient for further data manipulation and review.

## Support
For any issues or questions, please reach out to Max.

## Additional Resources
- [Python Installation Guide](https://www.python.org/downloads/)
- [More Information on CSV Files](https://en.wikipedia.org/wiki/Comma-separated_values)
