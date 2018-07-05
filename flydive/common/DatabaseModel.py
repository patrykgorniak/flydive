import sqlite3
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Date, Boolean, func, ForeignKey, Float, create_engine, Table

from sqlalchemy.orm import sessionmaker, relationship
import copy

Base = declarative_base()

class Helper:
    remove = ['_sa_instance_state']
    def to_dict(self):
        """TODO: Docstring for to_dict.
        :returns: TODO

        """
        dict = copy.deepcopy(self.__dict__)
        for key in self.remove:
            del dict[key]
        return dict

class Airline(Base):
    __tablename__ = 'airline'

    carrierCode = Column(String(10), primary_key=True)
    airlineName = Column(String(120), nullable=False)
#    checkedBaggage = Column(String)
#    handLuggage = Column(String)
    def __str__(self):
        return "Airline - code {0}, name: {1}".format(self.carrierCode, self.airlineName)

class Airport(Base):
    __tablename__ = 'airport'

    iata = Column(String(10), primary_key=True)
    name = Column(String(100), nullable=False)
    latitude =  Column(String(50))
    longitude = Column(String(50))
    country_name = Column(String(150))
    country_code = Column(String(150))
    currency_code = Column(String(150))
    currency_name = Column(String(150))
    currency_number = Column(String(150))

    def __str__(self):
        return "Airport: IATA: {0}, name: {1}, latitude: {2}, longitute: {3}, country: {4} country code: {} currency code: {}".format(self.iata,
                                                                                                                                       self.name,
                                                                                                                                       self.latitude,
                                                                                                                                       self.longitude,
                                                                                                                                       self.country_name,
                                                                                                                                       self.coutry_code,
                                                                                                                                       self.currency_code)

class Connections(Base, Helper):
    __tablename__ = 'connections'

    id = Column(Integer, primary_key=True)
    src_iata = Column(String(10), ForeignKey('airport.iata'), nullable=False)
    dst_iata = Column(String(10), nullable=False)
    carrierCode = Column(String(10),ForeignKey('airline.carrierCode'))
    updated = Column(Date, nullable=False, default = func.current_date())
    flightDetails = relationship("FlightDetails", back_populates="connection")

    def __str__(self):
        return "Connection: ID: {0}, from: {1}, to: {2}, airline code: {3}, updated: {4}".format(self.id,
                                                                                                 self.src_iata,
                                                                                                 self.dst_iata,
                                                                                                 self.carrierCode,
                                                                                                 self.updated)
    def __eq__(self, other):
        return self.src_iata==other.src_iata and self.dst_iata==other.dst_iata

    # def to_dict(self):
    #     """TODO: Docstring for to_dict.
    #     :returns: TODO

    #     """
    #     dict = self.__dict__
    #     del dict['_sa_instance_state']
    #     return dict

class FlightDetails(Base, Helper):
    __tablename__ = 'flightdetails'

    id = Column(Integer, primary_key=True )
    id_connections = Column(Integer, ForeignKey('connections.id'), nullable = False)
    departure_DateTime = Column(DateTime, nullable=False)
    arrival_DateTime = Column(DateTime, nullable=False)
    price = Column(Float, nullable=False)
    flightNumber = Column(Integer, nullable = False)
    currency = Column(String(5), nullable=False)
    isMacStation = Column(Boolean, nullable=False)
    isAirportChanged = Column(Boolean, nullable=False)
    inDC = Column(Boolean, nullable=False)
    availableCount = Column(Integer, nullable=True)
    connection = relationship("Connections", lazy='joined', back_populates = "flightDetails")
    # Helper.remove.extend(['src_iata', 'dst_iata'])

    #Helpers
    src_iata = ""
    dst_iata = ""

    def __str__(self):
        return """FlightDetails: \nID: {0}, ID_CON: {1}, depart_time: {2}, arrival_time: {3}, price: {4}, flight nb:{5}, currency: {6}, isMacStation: {7}, IsAirportChanged: {8} from: {9} to {10}, CLUB: {11}""".format(self.id,
                                                                                  self.id_connections,
                                                                                  self.departure_DateTime,
                                                                                  self.arrival_DateTime,
                                                                                  self.price,
                                                                                  self.flightNumber,
                                                                                  self.currency,
                                                                                  self.isMacStation,
                                                                                  self.isAirportChanged,
                                                                                  self.src_iata,
                                                                                  self.dst_iata,
                                                                                  self.inDC,
                                                                                  self.availableCount)
user_newsletter_table = Table('user_newsletter', Base.metadata,
                          Column('newsletter_id', Integer, ForeignKey('newsletter.id')),
                          Column('airport_iata', String(10), ForeignKey('airport.iata'))
                          )
class User(Base, Helper):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    login = Column(String(100), nullable = False)
    password = Column(String(100), nullable = False)
    fullname = Column(String(100), nullable = False)
    email = Column(String(150), nullable = False)
    newsletter = relationship("Newsletter", back_populates="user")

    def __str__(self):
        return "User: Login: {}, Name: {} {}, E-Mail: {}\n".format(
            self.login,
            self.fullname,
            self.surname, 
            self.email )

class Newsletter(Base, Helper):
    __tablename__ = 'newsletter'
    id = Column(Integer, primary_key=True) 
    user_id = Column(Integer, ForeignKey('user.id'))
    name = Column(String(100), nullable = False)
    departure_datetime = Column(DateTime, nullable=False)
    arrival_datetime = Column(DateTime, nullable=False)
    days = Column(Integer, nullable=True)
    max_changes = Column(Integer, nullable=True)
    flex_time_d = Column(Integer, nullable=True)
    max_change_time_h = Column(Integer, nullable=True)
    user = relationship("User", lazy='joined', back_populates = "newsletter")
    departures = relationship("Airport", secondary=user_newsletter_table)
    arrivals = relationship("Airport", secondary=user_newsletter_table)
    
    def __str__(self):
        return "Newsletter: Name: {}, Start: {}, End: {}\n".format(
        self.name,
        self.departure_datetime,
        self.arrival_datetime )


# class UserNewsletter(Base, Helper):
#     __tablename__ = "user_newsletter"
#     user_id = Column(Integer, ForeignKey('users.id'), nullable = False)
#     newsletter_id = Column(Integer, ForeignKey('newsletter.id'), nullable = False)
#     users = relationship("User", lazy='joined', back_populates = "newsletter")



# class WatchFlight(Base, Helper):
#     __tablename__ = 'watchFlight'

#     id = Column(Integer, primary_key=True)
#     src_iata = Column(String(10),ForeignKey('airport.iata'))
#     dst_iata = Column(String(10),ForeignKey('airport.iata'))

#     def __str__(self):
#         return "WatchDirections: ID: {}, src_iata: {}, dst_iata: {}\n".format(self.id,
#                                                                               self.src_iata,
#                                                                               self.dst_iata)

# class WatchConfig(Base, Helper):
#     __tablename__ = 'watchConfig'
#     id = Column(Integer, primary_key=True)
#     user_id = Column(Integer, ForeignKey('users.id'))
#     watchFlight_id = Column(Integer, ForeignKey('watchFlight.id'))
#     mode = Column(Integer, nullable = False)
#     datetime_start = Column(DateTime, nullable=False)
#     datetime_end = Column(DateTime, nullable=False)
#     days = Column(Integer, nullable=False)

#     def __str__(self):
#         return "WatchConfig: ID: {}, User_ID: {}, WatchFlight_ID: {}, mode: {}, \
#                 datatime_start: {}, datetime_end {}, days: {}".format(
#                     self.id,
#                     self.user_id,
#                     self.watchFlight_id,
#                     self.mode,
#                     self.datetime_start,
#                     self.datetime_end,
#                     self.days )

class Statistics(Base, Helper):
    __tablename__ = 'statistics'
    id = Column(Integer, primary_key = True)
    airline_code = Column(String(10), ForeignKey('airline.carrierCode'))
    airportCount = Column(Integer, nullable = False, default = 0)
    connectionCount = Column(Integer, nullable = False, default = 0)

    def __str__(self):
        return "Statistics for {}: {} airports, {} connections".format(self.airline_code, airportCount, connectionCount)

def main():
    engine = create_engine('sqlite:///flydive.sqlite')
    session = sessionmaker()
    session.configure(bind=engine)
    Base.metadata.create_all(engine)

if __name__ == "__main__":
    main()


