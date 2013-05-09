import numpy
from bitarray import bitarray

def crc(input_bits, input_divisor = bitarray('100110000010001110110110111')):
	if type(input_bits) == type(str()):
		s = input_bits
		input_bits = bitarray()
		input_bits.frombytes(s)
	len_crc = len(input_divisor)-1
	input_bits = input_bits + bitarray('0') * len_crc
	start_ct = 0
	end_ct = len(input_divisor)
	while (end_ct <= len(input_bits)):
		if input_bits[start_ct] == True:
			bits_to_xor = input_bits[start_ct: end_ct]
			input_bits[start_ct: end_ct] = bits_to_xor ^ input_divisor
		start_ct += 1
		end_ct += 1
	check_value = input_bits[-(len_crc):]
	return check_value

def reverse_crc(input_bits, check_value, input_divisor=bitarray('100110000010001110110110111')):
	if type(input_bits) == type(str()):
		s = input_bits
		input_bits = bitarray()
		input_bits.frombytes(s)
	len_crc = 32
	input_bits = input_bits + check_value
	start_ct = 0
	end_ct = len(input_divisor)
	while (end_ct <= len(input_bits)):
		if input_bits[start_ct] == True:
			bits_to_xor = input_bits[start_ct: end_ct]
			input_bits[start_ct: end_ct] = bits_to_xor ^ input_divisor
		start_ct += 1
		end_ct += 1
	check_value = input_bits[-(len_crc):]
	if check_value == bitarray('0') * len_crc:
		return True
	else:
		return False

print [hex(ord(x)) for x in crc("hello world").tobytes()]
import binascii
print hex(binascii.crc32('hello world'))

check_value = crc("hello world")
print reverse_crc("hello world", check_value)
