from datetime import datetime
from datetime import timedelta

from math import cos, sin, asin, sqrt, radians
from shapely import wkt, MultiPolygon

class Boundary:
    """
    A Boundary is a class that defines the geo-spatial/temporal
    boundaries (longtitude, latitude and time).


    Attributes:
        lat_range (float[]): array contains the start and end of latitude range 
        long_range (float[]): array contains the start and end of longtitude range.
          In the case of constructing a global mesh, the longtitude range should be -180:180.
        time_range(string[]): array contains the start and end of time range 
        

    Note:
        All geospatial boundaries are given in a 'EPSG:4326' projection
    """ 
    @classmethod
    def from_json(cls, config):
        """
             constructs a boundary object from json input
            Args:
               config (json): json object that contains the boundary attributes
                
        """
        long_min = config['region']['long_min']
        long_max = config['region']['long_max']
        lat_min = config['region']['lat_min']
        lat_max = config['region']['lat_max']
        start_time = config['region']['start_time']
        end_time = config['region']['end_time']
        lat_range = [lat_min, lat_max]
        long_range = [long_min , long_max]
        time_range = [start_time , end_time]
        obj = Boundary (lat_range , long_range , time_range)
        return obj

    @classmethod
    def from_poly_string(cls, poly_string):
        """
        Creates a Boundary object from a string representation of a polygon.
        """
        if "MULTIPOLYGON" in poly_string:
            # Seperate out uneccessary components
            poly_string = poly_string.split("MULTIPOLYGON (((")[1]
            poly_string = poly_string.split(")))")[0]
            # Split into two sets of polygon coords
            coord_strings = poly_string.split(")), ((")
            assert(len(coord_strings) == 2), \
                "Too many polygons in multipolygon, cannot form boundary object"

            # pos_coords on +180 side of antimeridian
            # neg_coords on -180 side of antimeridian
            pos_coords, neg_coords = [[polygon_coords.split(',') 
                                        for polygon_coords in coord_string] 
                                        for coord_string in coord_strings]
            # Extract longs and lats for each polygon
            pos_x = [float(coord.split(" ")[1]) for coord in pos_coords]
            pos_y = [float(coord.split(" ")[0]) for coord in pos_coords]
            neg_x = [float(coord.split(" ")[1]) for coord in neg_coords]
            neg_y = [float(coord.split(" ")[0]) for coord in neg_coords]

            assert(pos_y == neg_y), "Latitudes of polygons in multipolygon " + \
                                    "don't match, cannot construct valid " + \
                                    "boundary object"
            
            lat_min = min(pos_y)
            lat_max = max(pos_y)
            long_min = min(pos_x)
            long_max = max(neg_x)

        else:    
            coords = poly_string.split("POLYGON ((")[1].split("))")[0].split(", ")
            x = [float(coord.split(" ")[1]) for coord in coords]
            y = [float(coord.split(" ")[0]) for coord in coords]

            lat_min = min(x)
            lat_max = max(x)
            long_min = min(y)
            long_max = max(y)

        long_range = [long_min, long_max]
        lat_range = [lat_min, lat_max]

        bounds = Boundary(long_range, lat_range)

        return bounds

    def __init__(self, lat_range , long_range , time_range=None):
        """

            Args:
               lat_range (float[]): array contains the start and end of latitude range 
               long_range (float[]): array contains the start and end of longtitude range 
               time_range(Date[]): array contains the start and end of time range 
                
        """
        if time_range is None:
            time_range=[]
        else: 
             time_range[0] = self.parse_datetime(time_range[0])
             time_range[1] = self.parse_datetime(time_range[1])

        self.validate_bounds(lat_range , long_range , time_range)
        # Boundary information 
        self.lat_range = lat_range
        self.long_range = long_range
        self.time_range = time_range

    def parse_datetime(self, datetime_str: str):
        """
            Attempts to parse a string containing reference to system time into datetime format.
            If given the string 'TODAY', will return system time.
            special characters '+' and '-' can be used to adjust system time. e.g 'TODAY + 3' 
            will return system time + 3 days, 'TODAY - 16' will return system time - 16 days
            
            Args:
                datetime_str (String): String attempted to be parsed to datetime format. 
                    Expected input format is '%d%m%Y'
            Returns:
                date (String): date in a String format, '%Y-%m-%d'.
            Raises:
                ValueError : If given 'datetime_str' cannot be parsed, raises ValueError.
        """
        DATE_FORMAT = "%Y-%m-%d"
        
        datetime_str = datetime_str.upper()

        # check if datetime_str is valid datetime format.
        try:
            datetime_object = datetime.strptime(datetime_str, DATE_FORMAT).date()
            return datetime_object.strftime(DATE_FORMAT)
        except ValueError:
            # check if datetime_str contains reference to system-time.
            if datetime_str.strip() == "TODAY":
                today = datetime.today()
                return today.strftime(DATE_FORMAT)
            elif "TODAY" not in datetime_str:
                raise ValueError(f'Incorrect date format given. Cannot convert "{datetime_str}" to date.')
            
                # check for increment to system time.
            if "+" in datetime_str:
                increment = datetime_str.split("+")[1].strip()
                try:
                    increment = float(increment)
                    datetime_object = datetime.today() + timedelta(days = increment)
                    return datetime_object.strftime(DATE_FORMAT)
                except ValueError:
                    raise ValueError(f'Incorrect date format given. Cannot convert "{datetime_str}" to date. ' + \
                        f'Time increment "{increment}" cannot be cast to float')
                
                # check for decrement to system time.
            elif "-" in datetime_str:
                decrement = datetime_str.split("-")[1].strip()
                try:
                    decrement = float(decrement)
                    datetime_object = datetime.today() - timedelta(days = decrement)
                    return datetime_object.strftime(DATE_FORMAT)
                except ValueError:
                    raise ValueError(f'Incorrect date format given. Cannot convert "{datetime_str}" to date. ' + \
                            f'Time decrement "{decrement}" cannot be cast to float')
            else:
                raise ValueError(f'Incorrect date format given. Cannot convert "{datetime_str}" to date')
        

    def validate_bounds (self, lat_range , long_range , time_range):
        """
            method to check the bounds are valid
            Args:
               lat_range (float[]): array contains the start and end of latitude range 
               long_range (float[]): array contains the start and end of longtitude range 
               time_range(Date[]): array contains the start and end of time range 
                
        """
        if len(lat_range) < 2 or len (long_range)<2 :
            raise ValueError('Boundary: range should contain two values')
        if lat_range[0] > lat_range [1]:
             raise ValueError('Boundary: Latitude start range should be smaller than range end')
        if long_range[0] < -180 or long_range[1] > 180:
            raise ValueError('Boundary: Longtitude range should be within -180:180')
        if len (time_range) > 0:
            if datetime.strptime(time_range[0], '%Y-%m-%d') > datetime.strptime(time_range[1], '%Y-%m-%d'):
                     raise ValueError('Boundary: Start time range should be smaller than range end')

    # Functions used for getting data from a cellbox
    def getcx(self):
        """
            returns x-position of the centroid of the cellbox

            Returns:
                cx (float): the x-position of the top-left corner of the CellBox
                    given in degrees longitude.
        """
        cx = self.long_range[0] + self.get_width()/2
        
        if cx > 180:
            cx -= 360
        
        return cx

    def getcy(self):
        """
            returns y-position of the centroid of the cellbox

            Returns:
                cy (float): the y-position of the top-left corner of the CellBox
                    given in degrees latitude.
        """ 
        return self.lat_range[0] + self.get_height()/2
    def get_height(self):
        """
            returns height of the cellbox

            Returns:
                height (float): the height of the CellBox
                    given in degrees latitude.
        """
        height = self.lat_range[1] - self.lat_range[0]
        return height
    def get_width(self):
        """
            returns width of the cellbox

            Returns:
                width (float): the width of the CellBox
                    given in degrees longtitude.
        """
        # If not over the antimeridian
        if self.long_range[1] > self.long_range[0]:
            width = self.long_range[1] - self.long_range[0]
        else:
            width = (180 - self.long_range[0]) + (self.long_range[1] + 180)
        return width
    def get_time_range (self):
        """
            returns the time range
        """
        return self.time_range
    def getdcx(self):
        """
            returns x-distance from the edge to the centroid of the cellbox

            Returns:
                dcx (float): the x-distance from the edge of the CellBox to the 
                    centroid of the CellBox. Given in degrees longitude
        """
        return self.get_width()/2
    def getdcy(self):
        """
            returns y-distance from the edge to the centroid of the cellbox

            Returns:
                dxy (float): the y-distance from the edge of the CellBox to the
                    centroid of the CellBox. Given in degrees latitude
        """
        return self.get_height()/2
    def get_lat_min(self):
        """
            returns the min latitude
        """
        return self.lat_range[0]
    def get_lat_max(self):
        """
            returns the max latitude
        """
        return self.lat_range[1]   
    def get_long_min(self):
        """
            returns the min longtitude
        """
        return self.long_range[0]
    def get_long_max(self):
        """
            returns the max longtitude
        """
        return self.long_range[1]
    def get_time_min(self):
        """
            returns the min of time range
        """
        return self.time_range[0]
    def get_time_max(self):
        """
            returns the max of time range
        """

        return self.time_range[1] 
    def get_bounds(self):
        """
            returns the bounds of this cellbox

            Returns:
                bounds (list<tuples>): The geo-spatial boundaries of this CellBox.
        """
        bounds = [[ self.long_range[0], self.lat_range[0] ],
                   [ self.long_range[0], self.lat_range[1]],
                    [ self.long_range[1], self.lat_range[1]],
                    [ self.long_range[1], self.lat_range[0]],
                    [self.long_range[0], self.lat_range[0], ]]
        return bounds
    
    def calc_size(self):
        """
        Calculate the great circle distance (in meters) between 
        two points on the earth (specified in decimal degrees)
        """
        # convert decimal degrees to radians
        lon1, lat1, lon2, lat2 = map(radians, [self.get_long_min(), 
                                               self.get_lat_min(),
                                               self.get_long_max(),
                                               self.get_lat_max()])
        # haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))
        # Get diagonal length
        m = (6371 * c * 1000)
        # Divide by sqrt(2) to get 'square' side length
        return m / sqrt(2)
    
    def to_polygon(self):
        """
        Creates a shapely polygon from the extent of the boundary. Will be a 
        rectangle in mercator projection.
        
        Returns:
            (shapely.geometry.polygon.Polygon):
                Shapely polygon with corners at the min/max lat/long 
                values of this boundary
        """
        # If boundary not going over the antimeridian
        if self.get_long_min() < self.get_long_max():
            # Create a polygon of boundary
            polygon = wkt.loads(
                        f'POLYGON(({self.get_long_min()} {self.get_lat_min()},' + \
                                f'{self.get_long_min()} {self.get_lat_max()},' + \
                                f'{self.get_long_max()} {self.get_lat_max()},' + \
                                f'{self.get_long_max()} {self.get_lat_min()},' + \
                                f'{self.get_long_min()} {self.get_lat_min()}))'
                )
        elif self.get_long_min() == 180:
            polygon = wkt.loads(
                        f'POLYGON((-180 {self.get_lat_min()},' + \
                                f'-180 {self.get_lat_max()},' + \
                                f'{self.get_long_max()} {self.get_lat_max()},' + \
                                f'{self.get_long_max()} {self.get_lat_min()},' + \
                                f'-180 {self.get_lat_min()}))'
                )
        elif self.get_long_max() == -180:
            polygon = wkt.loads(
                        f'POLYGON(({self.get_long_min()} {self.get_lat_min()},' + \
                                f'{self.get_long_min()} {self.get_lat_max()},' + \
                                f'180 {self.get_lat_max()},' + \
                                f'180 {self.get_lat_min()},' + \
                                f'{self.get_long_min()} {self.get_lat_min()}))'
            )
        else:
            # Create a multipolygon of boundary
            polygon_1 = wkt.loads(
                        f'POLYGON(({self.get_long_min()} {self.get_lat_min()},' + \
                                f'{self.get_long_min()} {self.get_lat_max()},' + \
                                f'180 {self.get_lat_max()},' + \
                                f'180 {self.get_lat_min()},' + \
                                f'{self.get_long_min()} {self.get_lat_min()}))'
                )
            polygon_2 = wkt.loads(
                        f'POLYGON((-180 {self.get_lat_min()},' + \
                                f'-180 {self.get_lat_max()},' + \
                                f'{self.get_long_max()} {self.get_lat_max()},' + \
                                f'{self.get_long_max()} {self.get_lat_min()},' + \
                                f'-180 {self.get_lat_min()}))'
                )
            polygon = MultiPolygon([polygon_1, polygon_2])
        return polygon

    def to_poly_string(self):
        """
        Creates a string representation of the polygon from the extent of the boundary. 
        Will be a rectangle in mercator projection.
        
        Returns:
            (str):
                String representation of the shapely polygon with corners at 
                the min/max lat/long values of this boundary
        """
        return self.to_polygon().wkt

    def split(self):
        """
        Splits the boundary into four equal parts.
        
        Returns:
            (list<Boundary>): 
                List of four new boundaries, each representing a quarter of the 
                original boundary.
        """
        lat_mid = self.get_lat_min() + (self.get_height() / 2)
        long_mid = self.get_long_min() + (self.get_width() / 2)

        # 0 = south_west, 1 = north_west, 2 = south_east, 3 = north_east
        bounds = [
            Boundary([self.get_lat_min(), lat_mid], [self.get_long_min(), long_mid]),
            Boundary([lat_mid, self.get_lat_max()], [self.get_long_min(), long_mid]),
            Boundary([self.get_lat_min(), lat_mid], [long_mid, self.get_long_max()]),
            Boundary([lat_mid, self.get_lat_max()], [long_mid, self.get_long_max()])
        ]

        return bounds
        
    def __str__(self):


        lat_range = "lat range :[" + str(self.get_lat_min()) + \
              "," + str(self.get_lat_max()) + "]"
        long_range = "long range :[" + str(self.get_long_min()) + \
              "," + str(self.get_long_max()) + "]"
        time_range = "time range :" + str(self.get_time_range())

        return "{"+ lat_range + ", " + long_range + ", " + time_range + "}"


