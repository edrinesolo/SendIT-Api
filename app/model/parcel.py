import datetime
import json
import requests
from flask import Response
import requests
from flask_mail import Message

class ParcelList:
    """
    data structures
    """
    parcels=[]
    def __init__(self):
        self.base_price = 5
        self.trulysKey='esAok6JidUSx18ampgZAt5T8QjCiuw5w'

    def is_parcel_exist(self, id):
        """check if parcel not exist in the parcel list """
        for parcel in self.parcels:
            if parcel['id'] == id:
                return True
        return False

    def is_valid_parcel(self, parcel_data):
        """ check whether parcel is a valid one """
        details = parcel_data
        comment_description = details['comment_description']
        weight = details['weight']
        recipient_email = details['recipient_email']
        if not isinstance(comment_description, str):
            return "Description should be string format"

    def add_parcel(self, parcel_data):
        '''
        creates a new parcel order
        '''
        if self.is_valid_request(parcel_data):
            if "id" in parcel_data:
                id = parcel_data['id']
            else:
                id = len(self.parcels) + 1
            parcel = {
                'id': id,
                'pickup_address': parcel_data['pickup_address'],
                'destination_address': parcel_data['destination_address'],
                'comment_description': parcel_data['comment_description'],
                'status': parcel_data['status'],
                'current_location': parcel_data['current_location'],
                'created': datetime.datetime.now(),
                'user_id': parcel_data['user_id'],
                'recipient_address': parcel_data['recipient_address'],
                'recipient_phone': parcel_data['recipient_phone'],
                'recipient_email': parcel_data['recipient_email'],
                'weight': parcel_data['weight'],
                'distance': self.get_distance(parcel_data['pickup_address'], parcel_data['destination_address']),
                'pick_up_lat_lng': self.getpickuplatlng(parcel_data['pickup_address']),
                'destination_lat_lng': self.getdestinationlatlng(parcel_data['destination_address']),
                'price': self.get_charge(parcel_data['weight'], self.get_distance(parcel_data['pickup_address'],
                                                                                  parcel_data['destination_address']))

            }
            self.parcels.append(parcel)
            response = Response(response=json.dumps({
                'msg': "Parcel delivery successfully created", 'orderid': parcel.get('id')}),
                status=201, mimetype="application/json")
            response.headers['Location'] = "parcels/" + str(parcel['id'])
            return response
        else:
            response = Response(json.dumps({"error": "Invalid Parcel delivery order object"}),
                                status=400, mimetype="application/json")
            return response

    def get_all_parcel(self):
        """
        get all parcels posted
        """
        return self.parcels

    def get_one_parcel(self, id):
        """
        get one parcel by its id
        """
        for parcel in self.parcels:
            if parcel['id'] == id:
                return parcel

    def cancel_parcel(self, id):
        global cancelled_parcel
        for parcel in self.parcels:
            if parcel['id'] == id:
                cancelled_parcel = {
                    'id': parcel['id'],
                    'pickup_address': parcel['pickup_address'],
                    'destination_address': parcel['destination_address'],
                    'comment_description': parcel['comment_description'],
                    'status': "cancelled",
                    'current_location': parcel['current_location'],
                    'created': parcel['created'],
                    'user_id': parcel['user_id'],
                    'recipient_address': parcel['recipient_address'],
                    'recipient_phone': parcel['recipient_phone'],
                    'recipient_email': parcel['recipient_email'],
                    'weight': parcel['weight'],
                    'distance': self.get_distance(parcel['pickup_address'], parcel['destination_address']),
                    'pick_up_lat_lng': self.getpickuplatlng(parcel['pickup_address']),
                    'destination_lat_lng': self.getdestinationlatlng(parcel['destination_address']),
                    'price': self.get_charge(parcel['weight'],
                                             self.get_distance(parcel['pickup_address'], parcel['destination_address']))

                }
                parcel.update(cancelled_parcel)

        return cancelled_parcel

    def delete_one_parcel(self, id):
        """ delete an parcel by its id
        """
        parcel = self.get_one_parcel(id)
        if parcel:
            self.parcels.remove(parcel)
            return "deleted successfully"

    def is_valid_request(self, newparcel):
        if "destination_address" in newparcel and "pickup_address" in newparcel \
                and "comment_description" in newparcel and "created" in newparcel and \
                "user_id" in newparcel and "recipient_address" in newparcel and "recipient_phone" in newparcel and \
                "recipient_email" in newparcel and "status" in newparcel and "recipient_name" in newparcel and "weight" in newparcel:
            return True
        else:
            return False

    def is_order_delivered(self, id):
        '''
        checks that we cannot cancel an already delivered order
        '''
        for parcel in self.parcels:
            if parcel['id'] == id:
                if parcel['status'] == 'delivered':
                    return True
        return False

    def get_charge(self, weight, distance):
        return self.base_price + (weight * distance)

    def get_distance(self, point1, point2):
        return 200

    def getpickuplatlng(self, add):
        try:
            r = requests.get("https://www.mapquestapi.com/geocoding/v1/address?key="+self.trulysKey+"&inFormat=kvp&outFormat=json&location= "+add+"&thumbMaps=false")
            data=r.json()
            results=data['results'][0]
            locations=results['locations']
            latlng=locations[0].get('latLng')
            return latlng
        except Exception as identifier:
           print('Network Error')
           return {"lat": -24.90629, "lng": 152.19168}
        

    def getdestinationlatlng(self, add):
        try:
                r = requests.get("https://www.mapquestapi.com/geocoding/v1/address?key="+self.trulysKey+"&inFormat=kvp&outFormat=json&location= "+add+"&thumbMaps=false")
                data=r.json()
                results=data['results'][0]
                locations=results['locations']
                latlng=locations[0].get('latLng')
                return latlng
        except Exception as identifier:
                print('Network Error')
                return {"lat": -27.86015, "lng": 153.35434}
        
    def formatted_pick_address(self,pickupadd):
        '''
        should return a pickup address formatted correctly
        TODO:
        add a billing account to the google maps api and use that
        '''
        return pickupadd
        
    def update_order(self,current_location,status,id):
        '''
        updates the status and or the current location
        '''
        parceltoupdate={}
        for parcel in self.parcels:
            if parcel['id'] == id:
                parceltoupdate = {
                    'id': parcel['id'],
                    'pickup_address': parcel['pickup_address'],
                    'destination_address': parcel['destination_address'],
                    'comment_description': parcel['comment_description'],
                    'status': status,
                    'current_location': current_location,
                    'created': parcel['created'],
                    'updated':datetime.datetime.now(),
                    'user_id': parcel['user_id'],
                    'recipient_address': parcel['recipient_address'],
                    'recipient_phone': parcel['recipient_phone'],
                    'recipient_email': parcel['recipient_email'],
                    'weight': parcel['weight'],
                    'distance': self.get_distance(parcel['pickup_address'], parcel['destination_address']),
                    'pick_up_lat_lng': self.getpickuplatlng(parcel['pickup_address']),
                    'destination_lat_lng': self.getdestinationlatlng(parcel['destination_address']),
                    'price': self.get_charge(parcel['weight'],
                                             self.get_distance(parcel['pickup_address'], parcel['destination_address']))

                }
                parcel.update(parceltoupdate)

        return parceltoupdate


    def changedestination(self,newdest,id):
        '''
        allows user to change destination

        '''
        parceltoupdate={}
        for parcel in self.parcels:
            if parcel['id'] == id:
                parceltoupdate = {
                    'id': parcel['id'],
                    'pickup_address': parcel['pickup_address'],
                    'destination_address':newdest,
                    'comment_description': parcel['comment_description'],
                    'status': parcel['status'],
                    'current_location':parcel['current_location'],
                    'created': parcel['created'],
                    'updated':datetime.datetime.now(),
                    'user_id': parcel['user_id'],
                    'recipient_address': parcel['recipient_address'],
                    'recipient_phone': parcel['recipient_phone'],
                    'recipient_email': parcel['recipient_email'],
                    'weight': parcel['weight'],
                    'distance': self.get_distance(parcel['pickup_address'], newdest),
                    'pick_up_lat_lng': parcel['pick_up_lat_lng'],
                    'destination_lat_lng': self.getdestinationlatlng(newdest),
                    'price': parcel['price']

                }
                parcel.update(parceltoupdate)


        return parceltoupdate

    