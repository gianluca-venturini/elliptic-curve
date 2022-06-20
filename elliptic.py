from math import floor

p = 61

def add(n, m):
    return (n + m) % p


def mul(n, m):
    return (n * m) % p


def pow(n, m):
    return (n ** m) % p


def div(n, m, table_inv):
    if m == 0:
        raise Exception('Division by zero')
    return mul(n, table_inv[m])


def inv(n, table_inv):
    return table_inv[n]


# Note: this depends on the curve
def calculate_lambda(point1, point2, table_inv):
    if point1 == point2:
        # Needs to be the tangent to the curve, use the derivative in point1
        return div(add(mul(3, pow(point1[0], 2)), 9), mul(2, point1[1]), table_inv)
    # Just the slope of the rect between the two points
    return div(add(point2[1], -point1[1]), add(point2[0], -point1[0]), table_inv)


def add_points(point1, point2, table_inv):
    m = calculate_lambda(point1, point2, table_inv)

    new_x = add(add(pow(m, 2), -point1[0]), -point2[0])
    new_y = add(mul(m, add(point1[0], -new_x)), -point1[1])

    return (new_x, new_y)


# Curve used y^2 = x^3 + 9*x + 1
def calculate_curve_y(x, sqrt_index, table_sqrt):
    if sqrt_index != 0 and sqrt_index != 1:
        raise Exception('sqrt_index must be 0 or 1')
    y = calculate_curve_sqrt((x ** 3 + 9 * x + 1) % p, table_sqrt)
    if y is None:
        raise Exception('Point x: {} is not defined on the curve'.format(x))
    return y[sqrt_index]


def is_on_curve(point):
    return pow(point[1], 2) == add(add(pow(point[0], 3), mul(9, point[0])), 1)


def calculate_curve_sqrt(n, table_sqrt):
    if n not in table_sqrt:
        return None
    return table_sqrt[n]


def calculate_table_sqrt():
    table_sqrt = {}
    for n in range(0, p):
        m = mul(n, n)
        table_sqrt[m] = (n, p - n)
    return table_sqrt


def calculate_table_inv():
    table_inv = {}
    for n in range(0, p):
        for m in range(0, p):
            if (n * m) % p == 1:
                table_inv[n] = m
                table_inv[m] = n
    return table_inv


# Finds a point on the curve, doesn't really matter what point it is
def calculate_base_point(table_sqrt):
    x = floor(p / 2)
    while(x > 0):
        try:
            y = calculate_curve_y(x, 0, table_sqrt)
            return (x, y)
        except:
            x -= 1
    raise Exception('Cant find a base point. Something wrong with your curve')


# Given point, finds 2point
def calculate_double(point, table_inv):
    return add_points(point, point, table_inv)


def calculate_fast_mul_table(base_point, table_inv):
    fast_mul_table = {}
    point = base_point
    fast_mul_table[1] = base_point
    m = 2
    while m < p:
        point = calculate_double(point, table_inv)
        fast_mul_table[m] = point
        m *= 2
    return fast_mul_table


def calculate_fast_mul_point(n, point, table_inv):
    fast_mul_table = calculate_fast_mul_table(point, table_inv)
    keys = [key for key in fast_mul_table.keys()]
    new_point = None
    while n > 0:
        largest_usable_key = -1
        for key_index in range(0, len(keys)):
            if keys[len(keys) - 1 - key_index] <= n:
                largest_usable_key = keys[len(keys) - 1 - key_index]
                break
        if largest_usable_key == -1:
            raise Exception('Didnt find the largest_usable_key')
        if new_point is None:
            new_point = fast_mul_table[largest_usable_key]
        else:
            new_point = add_points(new_point, fast_mul_table[largest_usable_key], table_inv)
        n -= largest_usable_key
    return new_point


if __name__ == '__main__':
    print('Initializing')
    table_sqrt = calculate_table_sqrt()
    table_inv = calculate_table_inv()

    base_point = calculate_base_point(table_sqrt)

    print('table_sqrt', table_sqrt)
    print('table_inv', table_inv)

    print('base_point', base_point)
    print('double base_point', calculate_double(base_point, table_inv))

    ka = 48
    kb = 29

    print('Alice choses', ka)
    print('Bob choses', kb)

    pub_a = calculate_fast_mul_point(ka, base_point, table_inv)
    pub_b = calculate_fast_mul_point(kb, base_point, table_inv)

    print('Alice public value', pub_a)
    print('Bob public value', pub_b)

    print('Alice and bob exchange their public values')

    key_a = calculate_fast_mul_point(kb, pub_a, table_inv)
    key_b = calculate_fast_mul_point(ka, pub_b, table_inv)

    assert key_a == key_b
    print('Alice finds the key', key_a)
    print('Bob finds the key', key_b)
    print('No one else can find the key from pub_a and pub_b without knowing ka or kb or brute forcing them')
