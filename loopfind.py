import wave, subprocess, sys
from pathlib import Path
from operator import itemgetter

def samplesimilarity(samples_a, samples_b):
  num = 0
  den = 0
  for i in range(min(len(samples_a), len(samples_b))):
    num += abs(samples_a[i] * samples_b[i])
    den += samples_a[i]**2 + samples_b[i]**2
    
  return 2 * num / den
  
def samplesearch(stream, s_original, s_start=0, 
                 s_range=0, s_length=100, width=1):
  width = 1 # TODO: Implement width properly
  if s_range == 0:
    s_range = stream.getnframes()
  framerate = stream.getframerate()
  sampwidth = stream.getsampwidth()
  
  sample_o = []
  stream.setpos(s_original)
  for i in range(s_length):
    sample_o.append(int.from_bytes(stream.readframes(width)[:sampwidth],
                                   byteorder="little", signed=True))

  sample_n = []
  stream.setpos(s_start)
  for i in range(s_length):
    sample_n.append(int.from_bytes(stream.readframes(width)[:sampwidth],
                                   byteorder="little", signed=True))
  
  compare = [(s_start, samplesimilarity(sample_o, sample_n))]
  percent = 10
  searchlen = s_length * width
  max = min(stream.getnframes() - s_start, s_range + searchlen) - searchlen
  for i in range(1, max):
    del sample_n[0]
    sample_n.append(int.from_bytes(stream.readframes(width)[:sampwidth],
                                   byteorder="little", signed=True))
    compare.append((i + s_start, samplesimilarity(sample_o, sample_n)))
    if (i / max * 100) > percent:
      print(f"{percent}% done")
      percent += 10
  
  compare.sort(key=itemgetter(1))
  return compare[::-1]

def start(args, flags):

  # Input file exists

  file = None
  try:  
    file = Path(args[0])
  except IndexError:
    print("Too few arguments supplied")
    exit(1)
    
  if not file.is_file():
    print("File not found")
    exit(1)
    
  # Try to convert to wav
    
  if file.suffix != ".wav":
    new_file = file.with_suffix('.wav')
    if new_file.is_file():
      print("Converted file found in path, using instead")
    else:
      output = subprocess.run(['ffmpeg.exe', '-i', str(file), str(new_file)])
      if output.returncode != 0:
        print("Invalid file: unable to convert to .wav")
        exit(1)
    file = new_file
    
  # Get arguments
    
  c_args = [0, 0, 0]
  try:
    if 's' in flags:
      for i in range(1, 4):
        c_args[i-1] = float(args[i])
    else:
      for i in range(1, 4):
        c_args[i-1] = int(args[i])
  except IndexError:
    print("Too few arguments supplied")
    exit(1)
  except ValueError:
    print("Non-file arguments must be integers (use -s to specify seconds)")
    exit(1)

  results_len = 10
  if len(args) > 4:
    try:
      results_len = int(args[4])
    except ValueError:
      print("Non-file arguments must be integers")
      exit(1)
      
  with wave.open(str(file), "rb") as stream:
    if "s" in flags:
      for i in range(3):
        c_args[i] = int(c_args[i] * stream.getframerate())
      
    top = samplesearch(stream, *c_args)
    print("Rankings for samples that loop at sample #{0}".format(c_args[0]))
    for i in range(results_len):
      print(top[i])

if __name__ == "__main__":
  argc = len(sys.argv)
  if len(sys.argv) < 2:
    print("Usage: {0} [-s] <file> <start sample> <end sample> <search length> [return length]".format(sys.argv[0]))
    exit(0)
    
  valid_flags = {'s'}
  selected_flags = set()
  while sys.argv[1][0] == '-':
    flag = sys.argv.pop(1)
    if len(flag) != 2:
      print("Invalid flag: {1}".format(flag))
      exit(1)
    if not flag[1] in valid_flags:
      print("Invalid flag: {1}".format(flag))
      exit(1)
    selected_flags.add(flag[1])
      
  start(sys.argv[1:], selected_flags)
  