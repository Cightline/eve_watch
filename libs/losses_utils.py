from sql.db_connect import Connect
from sqlalchemy import func


class LossesUtils():
    def __init__(self, config):
        self.db = Connect(config['database']['data'])
        self.classes = self.db.base.classes
        

    def oldest_record(self, alliance_ids, start_date, kills='kills'):
        # Get the first killTime recorded
        if kills == 'kills':
            result = self.db.session.query(self.classes.attacker.killTime).filter(self.classes.attacker.allianceID.in_(alliance_ids)).filter(self.classes.attacker.killTime >= start_date).order_by(self.classes.attacker.killTime.asc()).first() 

            if not result:
                return None

            else:
                return result.killTime


        # been killed?
        #select * from kills where allianceID = 1006830534 order by killTime asc limit 1;
        return self.db.session.query(self.classes.kills.killTime).filter(self.classes.kills.allianceID.in_(alliance_ids)).order_by(self.classes.kills.killTime.asc()).first().killTime 


    # Returns total ships 
    def query_total(self, alliance_ids, start_date, characterID=None, kills='used'):
        print('FUCK')
        #if kills == 'used' and characterID:
        #    return self.db.session.query(self.classes.attacker.shipTypeID, func.count(self.classes.attacker.shipTypeID)).group_by(self.classes.attacker.shipTypeID).filter(
        #            self.classes.attacker.allianceID.in_(alliance_ids)).filter(self.classes.attacker.killTime >= start_date).filter_by(characterID=characterID).all()
        
        # Pulls from "attackers"
        if kills == 'used':
            return self.db.session.query(self.classes.attacker.shipTypeID, func.count(self.classes.attacker.shipTypeID)).group_by(self.classes.attacker.shipTypeID).filter(
                    self.classes.attacker.allianceID.in_(alliance_ids)).filter(self.classes.attacker.killTime >= start_date).all()


        #if characterID:
        #    return self.db.session.query(self.classes.kills.shipTypeID, func.count(self.classes.kills.shipTypeID)).filter(
        #            self.classes.kills.killTime >= start_date).group_by(self.classes.kills.shipTypeID).filter_by(characterID=characterID).filter(
        #                    self.classes.kills.allianceID.in_(alliance_ids)).all()

        
        return self.db.session.query(self.classes.kills.shipTypeID, func.count(self.classes.kills.shipTypeID)).group_by(self.classes.kills.shipTypeID).filter(self.classes.kills.killTime >= start_date).filter(
                self.db.base.classes.kills.allianceID.in_(alliance_ids))


    def query(self, alliance_ids, start_date, characterID=None, shipTypeID=None, type_='attacker'):

        if type_ == 'attacker':
            #if characterID and shipTypeID:
            #    return self.db.session.query(self.classes.attacker).filter_by(characterID=characterID, shipTypeID=shipTypeID).filter(
            #            self.classes.attacker.allianceID.in_(alliance_ids)).filter(self.classes.attacker.killTime >= start_date).all()

            #if characterID:
            #    return self.db.session.query(self.classes.attacker).filter_by(characterID=characterID).filter(
            #            self.classes.attacker.allianceID.in_(alliance_ids)).filter(self.classes.attacker.killTime >= start_date).all()

            #if shipTypeID:
            #    return self.db.session.query(self.classes.attacker).filter_by(shipTypeID=shipTypeID).filter(self.classes.attacker.allianceID.in_(alliance_ids)).filter(self.classes.attacker.killTime >= start_date).all()

            #else:
            
            return self.db.session.query(self.classes.attacker).filter(self.classes.attacker.allianceID.in_(alliance_ids)).filter(self.classes.attacker.killTime >= start_date).all()


