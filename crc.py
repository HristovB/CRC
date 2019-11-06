import numpy as np
from sympy import symbols, simplify, Poly


def init(message, num_bits, generator=None, dest_message=None):
    x = symbols('x')

    origin_message = np.array(list(message), dtype=int)

    if dest_message is not None:
        dest_message = np.array(list(dest_message), dtype=int)

    if generator is not None:
        generator = np.array(list(generator), dtype=int)

    gen_dest_message = generate_error(origin_message, num_bits)

    if generator is None:
        origin_poly = Poly.from_list(origin_message, x)
        dest_poly = Poly.from_list(gen_dest_message, x)

        error_poly = Poly.sub(origin_poly, dest_poly)

        factorized_error = Poly.factor(error_poly)

        generator_poly = get_generator(factorized_error)

        generator = np.array(generator_poly.all_coeffs())

    return origin_message, dest_message, generator


def flip(bit):
    if bit:
        return 0
    else:
        return 1


def generate_error(message, num_bits):
    error = message.copy()
    for i in range(num_bits):
        error[i] = flip(error[i])

    return error


def clean_poly(poly):
    poly = poly.replace('x**', '')
    poly = poly.replace('*', '')
    poly = poly.replace('1', '0')
    poly = poly.replace('x', '1')
    poly = poly.replace('+', '')
    poly = poly.replace('-', '')

    return poly


def get_generator(error):
    error = simplify(error)
    error_str = str(error)
    error_str = error_str.strip(')').split('(')

    error_str = np.array([clean_poly(term) for term in error_str])

    max_orders = []
    for term in error_str:
        term = np.array(term.split())
        term = term.astype(dtype=int)

        max_orders.append(max(term))

    x = symbols('x')

    if max_orders[0] > max_orders[1]:
        generator = x**max_orders[0] + 1

    else:
        generator = x**(max_orders[1] + 1)

    return Poly(generator)


def xor(a, b):
    result = []
    i = 0
    for i in range(len(b)):
        if (a[i] == 0 and b[i] == 0) or (a[i] == 1 and b[i] == 1):
            result.append(0)

        else:
            result.append(1)

    result = np.array(result)
    result = np.concatenate((result, a[i+1:]), axis=0)

    return result


def calculate_remainder(message, generator):
    remainder = message.copy()
    while len(generator) < len(remainder):
        remainder = np.trim_zeros(xor(message, generator))
        message = remainder

    return remainder


def crc(origin, destination, generator):
    origin_rem = calculate_remainder(origin, generator)
    dest_rem = calculate_remainder(destination, generator)

    if not np.array_equal(origin_rem, dest_rem):
        print('ERROR DETECTED!')

    else:
        print('TRANSFER SUCCESSFUL!')


if __name__ == '__main__':

    original_message = '11001111'  # insert original message
    destination_message = '11010011'  # insert destination message as string, if None it is automatically generated
    generator_key = None  # insert custom generator as string, if None it is automatically generated

    error_bits = 3  # insert number of expected errors

    original_message, destination_message, key = init(message=original_message, num_bits=error_bits,
                                                      generator=generator_key, dest_message=destination_message)

    print(original_message)
    print(destination_message)
    crc(original_message, destination_message, key)
