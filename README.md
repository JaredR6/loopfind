# loopfind

Assists in finding loops in audio files.

By default, the program will print out 10 samples with decreasing accuracy for potential loop points, given an initial reference sample, search start and search length.

The program requires a wav file as input, otherwise the file is run though ffmpeg (locally!) to be converted as such.

## Usage

loopfind.py [-s] \<wav file\> \<loop sample\> \<search start sample\> \<search length\> [return length]

-s flag uses seconds instead of samples. The program still returns sample loop points.  
Return length is optional. The default return length is 10 potential samples.

## Todo

Find way to convert directly to brstm file. If anyone knows of any tools compatible with python, or can get RSTMlib working with python, please message me!
