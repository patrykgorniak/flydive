from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
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
        self.engine = create_engine(self.database_uri, 
                                    connect_args={'check_same_thread':False},
                                    poolclass=StaticPool)
                                    #echo=args.verbose_sql, poolclass=SingletonThreadPool)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

        if not database_exists(self.database_uri):
            self.__createDatabaseModel()

    def log(self, message):
        lm.debug("DatabaseManager: {0}".format(message))

    def addAirport(self, airport):
        """TODO: Docstring for addAirport.

        :airport: TODO
        :returns: TODO

        """
        if not isinstance(airport, Airport):
            raise TypeError('airport is not type of Airport.')

        if not self.__exists(airport, { 'iata': airport.iata }):
            self.log("Added airport: IATA - {0}".format(airport.iata))
            self.__addAndCommit(airport)
        else:
            self.log("Airport {0} already exists in DB".format(airport.iata))

    def addConnection(self, connection):
        """Add connection to the database.

        :connection: Connections object from DatabaseModel
        :returns: connection ID
        """
        if not isinstance(connection, Connections):
            raise TypeError('connection is not object of Connections.')

        inDb = self.__exists(connection, { 'src_iata': connection.src_iata, 'dst_iata': connection.dst_iata })

        if not inDb:
            self.log("Add connection from {0} to {1}".format(connection.src_iata, connection.dst_iata))
            self.__addAndCommit(connection)
            return True
        else:
            self.log("Connection from {0} to {1} exists in DB".format(connection.src_iata, connection.dst_iata))
            return False

    def updateConnection(self, connection):
        inDb = self.__exists(connection, { 'src_iata': connection.src_iata, 'dst_iata': connection.dst_iata })
        if inDb:
            inDb.updated = connection.updated #DateTime.date()
            self.session.commit()


    def queryConnections(self, filter_by = {}):
        """Query connections by given filter

        :filter_by: filtering criterion from DatabaseModel.Connecions type
        :returns: connection list
        """

        # session = self.Session()
        connectionsList = self.session.query(Connections).filter_by(**filter_by)
        # query = session.query(Connections.src_iata, Connections.dst_iata).filter_by(**filter_by)
        return connectionsList

    def getConnectionList(self, connectionQueryList = []):
        connectionList = []
        for connection in connectionQueryList:
            assert(isinstance(connection, Connections), "{} is not type of Connections".format(type(connection)))
            connectionList.extend(self.getConnections(connection))

        return connectionList

    def getConnections(self, connection = Connections()):
        """ Query connections

        :connection: default parameter. Allows to get specific connections.
        :returns: list with matched connections

        """

        # session = self.Session()
        connectionsList = self.session.query(Connections).filter_by(**(connection.to_dict()))
        # query = session.query(Connections.src_iata, Connections.dst_iata).filter_by(**filter_by)
        return connectionsList

    def getOrderedConnections(self, order = []):
        # session = self.Session()
        connectionList = self.session.query(Connections).join(Airport).\
                filter(Airport.currency_code=='PLN').all()
        connectionList.extend(self.session.query(Connections).join(Airport).\
                filter(Airport.currency_code=='EUR').all())
        connectionList.extend(self.session.query(Connections).join(Airport).\
                filter(Airport.currency_code!='PLN', Airport.currency_code!='EUR').all())

        return connectionList

    def addFlightDetails(self, flightDetails):
        """TODO: Docstring for addFlightDetails.

        :flightDetails: TODO
        :returns: TODO

        """
        if not isinstance(flightDetails, FlightDetails):
            raise TypeError('fightDetails is not object of FlightDetails.')

        self.log("Adding flight: " + str(flightDetails))
        dbFlightDetails = self.__exists(flightDetails, {'id_connections' : flightDetails.id_connections,
                                             'flightNumber': flightDetails.flightNumber,
                                             'inDC': flightDetails.inDC,
                                             'departure_DateTime': flightDetails.departure_DateTime})
        if not dbFlightDetails:
            self.__addAndCommit(flightDetails)
        else:
            self.updateFlightDetails(dbFlightDetails, flightDetails)
            # self.log("Object exists in DB -> UPDATED!")


    def updateFlightDetails(self, flightDetailsOld, flightDetailsNew):
        if not isinstance(flightDetailsNew, FlightDetails):
            raise TypeError('fightDetails is not object of FlightDetails.')
        
        flightDetailsOld.arrival_DateTime = flightDetailsNew.arrival_DateTime
        flightDetailsOld.price = flightDetailsNew.price
        flightDetailsOld.availableCount = flightDetailsNew.availableCount
        # session = self.Session()
        self.session.commit()

    def addAirline(self, airline):
        """TODO: Docstring for addAirline.

        :airline: TODO
        :returns: TODO

        """
        if not isinstance(airline, Airline):
            raise TypeError('airline is not type of Airline.')

        inDb = self.__exists(airline, { 'carrierCode': airline.carrierCode })

        if not inDb:
            self.log("Adding new airline: " + airline.carrierCode)
            return self.__addAndCommit(airline).carrierCode
        else:
            self.log("Airline {0} exists in DB".format(airline.carrierCode))
            return inDb.carrierCode

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
        # session = self.Session()
        self.session.add(data)
        self.session.commit()
        return data

    def exists(self, entry):
        filter_by = {}
        if isinstance(entry, Airline):
            filter_by = { 'carrierCode': entry.carrierCode }
        elif isinstance(entry, Airport):
            filter_by = { 'iata': entry.iata }
        elif isinstance(entry, Connections):
            filter_by = { 'src_iata': entry.src_iata, 'dst_iata': entry.dst_iata }
        else:
            raise TypeError('error')

        if not self.__exists(entry, filter_by):
            return False
        else:
            return True

    def __exists(self, entry, filtered_by):
        """TODO: Docstring for function.

        :arg1: TODO
        :returns: TODO

        """
        # session = self.Session()
        data = self.session.query(type(entry)).filter_by(**filtered_by).first()
        return data

def main():
    dbMgr = DatabaseManager('flydive', 'sqlite')
    for i in getOrderedConnections():
        print(i)

if __name__ == "__main__":
    main()
