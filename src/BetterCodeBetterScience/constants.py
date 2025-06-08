# project constants

# speed of light in a vacuum
C = 299792458


class Constants:
    C = 299792458
    
    def __setattr__(self, name, value):
        raise AttributeError("Constants cannot be modified")
