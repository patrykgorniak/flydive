import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Boolean, func, ForeignKey, Float
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Helper:
    def to_dict(self):
        """TODO: Docstring for to_dict.
        :returns: TODO

        """
        dict = self.__dict__
        del dict['_sa_instance_state']
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
    country = Column(String(150))
    
    def __str__(self):
        return "Airport: IATA: {0}, name: {1}, latitude: {2}, longitute: {3}, country: {4}".format(self.iata,
                                                                                                   self.name,
                                                                                                   self.latitude,
                                                                                                   self.longitude,
                                                                                                   self.country)

class Connections(Base, Helper):
    __tablename__ = 'connections'

    id = Column(Integer, primary_key=True)
    src_iata = Column(String(10), nullable=False)
    dst_iata = Column(String(10), nullable=False)
    carrierCode = Column(String(10),ForeignKey('airline.carrierCode'))
    updated = Column(DateTime, nullable=False, default = func.now())

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

class FlightDetails(Base):
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

    def __str__(self):
        return """FlightDetails: ID: {0}, ID_CON: {1}, depart_time: {2}, arrival_time: {3}, price: {4}, flight nb: {5},
                currency: {6}, isMacStation: {7}, IsAirportChanged: {8}""".format(self.id,
                                                                                  self.id_connections,
                                                                                  self.departure_DateTime,
                                                                                  self.arrival_DateTime,
                                                                                  self.price,
                                                                                  self.flightNumber,
                                                                                  self.currency,
                                                                                  self.isMacStation,
                                                                                  self.isAirportChanged)

def main():
    engine = create_engine('sqlite:///flydive.sqlite')
    session = sessionmaker()
    session.configure(bind=engine)
    Base.metadata.create_all(engine)

if __name__ == "__main__":
    main()


