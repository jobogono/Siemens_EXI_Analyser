Author: Joshua Bognar

Script for summarising Siemens Ysio EXI logs.

Tested on Ysio, Ysio Max, Ysio X.Pree

Takes as input a directory containing .csv files of raw EXI log exports. This directory must not contain any other .csv files.

Saved output contains number of examinations and median data for each examination of:
  - kV
  - mAs
  - DAP
  - EXI
  - Collimation
  - SID
  - Target dose

Siemens raw EXI logs can contain some issues:
  - Misplaced commas: Some rows in the raw EXI logs contain misplaced commas. This can manifest in multiple ways. The underlying cause for this is not known. The impact is that data are misaligned to columns, or assigned an incorrect datatype. Currently this is handled by simply removing this data from the analysis.
  - Duplicates: Siemens EXI logs will create a new line when an image is digitally collimated after the exposure. Duplicate entries are deleted based on the duplicate SOPInstanceUID column.
  - Zero DAP: It has been found in some files that a large number of DAP entries is zero. The cause for this is unknown but it does not appear to be common. The entire entry is excluded for analysis.
The number of entries removed due to misplaced commas or zero DAP is printed to the console. Note that entries deleted due to misplaced commas may also include duplicate entries.
