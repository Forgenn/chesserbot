from math import cos, sin, atan2, sqrt

def inverse(x, y, l1, l2):
    a =((x**2+y**2-l1**2-l2**2)/(2*l1*l2))**2 
    o2 = atan2(sqrt(1-a), a)
    o1 = atan2(y,x) - atan2(l2*sin(o2), l1+l2*cos(o2))

    return o1, o2
