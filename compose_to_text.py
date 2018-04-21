import hgtk
import sys
#import codecs

uncomposed = sys.argv[1]
compose = sys.argv[2]

fp = open(uncomposed, 'r', encoding='utf-8')

writefp = open(compose, 'a')
for line in fp:
	line = hgtk.text.compose(line)
	writefp.write(line + '\n')

writefp.close()
fp.close()

