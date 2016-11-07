import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Boolean, func, ForeignKey, Float
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Airline(Base):
    __tablename__ = 'airline'

    carrierCode = Column(String(10), primary_key=True)
    airlineName = Column(String(120), nullable=False)
#    checkedBaggage = Column(String)
#    handLuggage = Column(String)

class Airport(Base):
    __tablename__ = 'airport'

    iata = Column(String(10), primary_key=True)
    name = Column(String(100), nullable=False)
    latitude =  Column(String(50))
    longitude = Column(String(50))
    country = Column(String(150))

class Connections(Base):
    __tablename__ = 'connections'

    id = Column(Integer, primary_key=True)
    src_iata = Column(String(10), nullable=False)
    dst_iata = Column(String(10), nullable=False)
    carrierCode = Column(String(10),ForeignKey('airline.carrierCode'))
    updated = Column(DateTime, nullable=False, default = func.now())

    def to_dict(self):
        """TODO: Docstring for to_dict.
        :returns: TODO

        """
        #TODO: To finish this function

        dict = {  }
        for (k, v) in self.__dict__:
            if k != __tablename__:
                if v:
                    dict.append(k,v);
        return dict

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

def main():
    engine = create_engine('sqlite:///flydive.sqlite')
    session = sessionmaker()
    session.configure(bind=engine)
    Base.metadata.create_all(engine)

if __name__ == "__main__":
    main()
