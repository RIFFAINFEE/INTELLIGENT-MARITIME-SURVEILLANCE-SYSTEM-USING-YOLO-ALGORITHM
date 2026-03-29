from shapely.geometry import Point, Polygon


def point_in_polygon(x, y, points):

    poly = Polygon(points)

    p = Point(x, y)

    return poly.contains(p)