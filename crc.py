import numpy
from bitarray import bitarray

input_bits = bitarray('11010011101100')
input_divisor = bitarray('1011')

def crc(input_bits, input_divisor):
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

def reverse_crc(input_bits, input_divisor, check_value):
	len_crc = len(input_divisor)-1
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
		return False
	else:
		return True

check_value = crc(input_bits, input_divisor)
print check_value
print reverse_crc(input_bits, input_divisor, check_value)