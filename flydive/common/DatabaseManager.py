from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists
from common.DatabaseModel import Airline, Airport, Connections, FlightDetails, Base 
from common import LogManager as lm

class DatabaseManager(object):

    def __init__(self, database_name, database_type):
        """TODO: Docstring for __init__.

        :database_name: TODO
        :database_type: TODO
        :returns: TODO

        """
        self.database_name = database_name
        self.database_type = database_type
        self.database_uri = self.database_type + ':///' + self.database_name + '.' + self.database_type
        self.engine = create_engine(self.database_uri)
        self.Session = sessionmaker(bind=self.engine)

        if not database_exists(self.database_uri):
            self.__createDatabaseModel()

    def log(self, message):
        lm.debug("DatabaseManager: {0}".format(message))

    def addAirport(self, airport):
        """TODO: Docstring for addAirport.

        :airport: TODO
        :returns: TODO

        """

        if not self.__exists(airport, { 'iata': airport.iata }):
            self.log("Added airport: IATA - {0}".format(airport.iata))
            self.__addAndCommit(airport)
        else:
            self.log("Airport {0} already exists in DB".format(airport.iata))

    def addConnection(self, connection):
        """TODO: Docstring for addConnection.

        :connection: TODO
        :returns: TODO

        """
        if not self.__exists(connection, { 'src_iata': connection.src_iata, 'dst_iata': connection.dst_iata }):
            self.__addAndCommit(connection)
        else:
            self.log("Object exists in DB")

    def queryConnections(self, filter_by = {}):
        session = self.Session()
        query = session.query(Connections).filter_by(**filter_by)
        # query = session.query(Connections.src_iata, Connections.dst_iata).filter_by(**filter_by)

        return query

    def addFlightDetails(self, flightDetails):
        """TODO: Docstring for addFlightDetails.

        :flightDetails: TODO
        :returns: TODO

        """
        if not isinstance(flightDetails, FlightDetails):
            raise ValueError

        self.log("Adding flight: " + str(flightDetails))
        # if not self.__exists(flightDetails, { 'iata': airport.iata }):
        #     __addAndCommit(airport)
        # else:
        #     print("Object exists in DB")

    def addAirline(self, airline):
        """TODO: Docstring for addAirline.

        :airline: TODO
        :returns: TODO

        """
        if not self.__exists(airline, { 'carrierCode': airline.carrierCode }):
            self.__addAndCommit(airline)
        else:
            self.log("Object exists in DB")

    def __createDatabaseModel(self):
        """TODO: Docstring for __createModel.
        :returns: TODO

        """
        Base.metadata.create_all(self.engine)

    def __addAndCommit(self, data):
        """TODO: Docstring for __addAndCommit.

        :data: TODO
        :returns: TODO

        """
        session = self.Session()
        session.add(data)
        session.commit()

    def __exists(self, entry, filtered_by):
        """TODO: Docstring for function.

        :arg1: TODO
        :returns: TODO

        """
        session = self.Session()
        return not session.query(type(entry)).filter_by(**filtered_by).first()==None

def main():
    dbMgr = DatabaseManager('flydive', 'sqlite')
    dbMgr.addAirline(Airline(carrierCode='W6', airlineName='wizzair'))
    dbMgr.addAirline(Airline(carrierCode='W6', airlineName='wizzair'))
    dbMgr.addAirline(Airline(carrierCode='W6', airlineName='wizzair'))
    dbMgr.addAirline(Airline(carrierCode='W6', airlineName='wizzair'))

if __name__ == "__main__":
    main()
