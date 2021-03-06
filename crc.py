def genTable():
	table = []
	for i in range(256):
		word = i
		for j in range(8):
			if word&1 == 1:
				word = (word >> 1) ^ 0xedb88320
			else:
				word >>= 1
		table.append(word)
	return table

def crc32(string, crc=0xFFFFFFFF, table = genTable()):
	for i in range(len(string)):
		crc = table[(crc&0xFF)^ord(string[i])] ^ (crc >> 8)
	return 0xFFFFFFFF^crc
