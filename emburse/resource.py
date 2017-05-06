import re
from dateutil.parser import parse as date_parser
import datetime
import emburse.util as util
import emburse.errors as error
from emburse.requestor import Requestor


def convert_to_emburse_object(resp, auth_token, klass_name=None):
    """
    Convert to Emburse Object, function to build emburse objects from the given
    response data.
    
    Args:
        resp: Response data
        
        auth_token: our application's auth token from
            https://app.emburse.com/applications
        
        klass_name (str, optional): Name of the resource
    
    Returns:
        An Emburse Object
    
    """
    types = {
        'account': Account,
        'allowance': Allowance,
        'card': Card,
        'category': Category,
        'company': Company,
        'department': Department,
        'label': Label,
        'location': Location,
        'member': Member,
        'shared_link': SharedLink,
        'statement': Statement,
        'transaction': Transaction,
    }

    if isinstance(resp, list):
        return [convert_to_emburse_object(i, auth_token, klass_name=klass_name)
                for i in resp]
    elif isinstance(resp, dict) and not isinstance(resp, APIResource):
        resp = resp.copy()
        if isinstance(klass_name, str):
            klass = types.get(klass_name, APIResource)
        else:
            klass = APIResource
        emburse_obj = klass(auth_token=auth_token)
        return emburse_obj.refresh_from(resp)
    else:
        float_regex = re.compile(r'^\d*\.\d$')
        if isinstance(resp, str) and is_date(resp):
            return date_parser(resp)
        elif isinstance(resp, str) and float_regex.match(resp):
            return float(resp)
        else:
            return resp


def is_date(resp):
    """
    Is Date, method to test if given value is a date string.
    
    Args:
        resp (str): Value to test if it is a date string.
    
    Returns:
        bool: True if value is a date, False otherwise.
     
    """
    date_re = re.compile(r'\d{4}\W\d{2}\W\d{2}')
    if not date_re.match(resp):
        return False
    try:
        date_parser(resp)
        return True
    except Exception:
        return False


class EmburseObject(object):
    """
    Emburse Object
    
    base for all emburse objects forcing the auth_token param
    
    """

    def __init__(self, auth_token, **kwargs):
        """
        Emburse Object
        
        Args:
            auth_token (str): Your application's auth token from
                https://app.emburse.com/applications
            
            **kwargs: if 'id' is given the resources id is set from the value.
            
        """
        self.auth_token = auth_token
        if 'id' in kwargs:
            self.id = kwargs['id']


class APIResource(EmburseObject):
    """
    Emburse API Resource Object
    All emburse api endpoint classes are derived from this class and gives some
    of the core functionality such as building api url, retrieving data from
    the api, sending data to the api
    
    """

    def __init__(self, auth_token, **params):
        """
        Emburse API Resource Object
        
        Args:
            auth_token (str): Your application's auth token.
            
            **params: Values to set on the Resource
         
        """
        super(APIResource, self).__init__(auth_token=auth_token, **params)
        self.build_params = params
        self.request_params = None
        self.requestor = Requestor(token=self.auth_token)
        for param_name, param_value in params.items():
            klass_name = param_name
            if klass_name == 'parent':
                klass_name = self.class_name()

            setattr(
                self,
                param_name,
                convert_to_emburse_object(
                    param_value,
                    auth_token=auth_token,
                    klass_name=klass_name
                )
            )

    def __repr__(self):
        obj_params = []
        if self.build_params:
            for key, value in self.build_params.items():
                obj_params.append("{k}='{v}'".format(k=key, v=value))
        if len(obj_params) > 1:
            param_str = ' ,'.join(obj_params)
        elif len(obj_params) == 1:
            param_str = ' '.join(obj_params)
        else:
            param_str = ''
        return '<{cls}{params}>'.format(
            cls=self.__class__,
            params=param_str
        )

    def retrieve(self, identifier):
        """
        Retrieve, gets data from api for the object type by a given identifier,
        object id.
        
        Args:
            identifier (str): UUID of the object.
        
        Returns:
            An instance of the same type of api resource as the calling object
            with data from the api.
        
        :Example:
            >>> card_id = "2316d331-e2d5-43f1-9c9d-8ca3a738df28"
            >>> client = emburse.Client(auth_token='abc123')
            >>> card = client.Card.retrieve(identifier=card_id)
            <Card id='2316d331-e2d5-43f1-9c9d-8ca3a738df28'>
        
        """
        instance = self.__class__(auth_token=self.auth_token)
        instance.id = identifier
        instance.refresh()
        return instance

    def refresh(self):
        """
        Refresh, updates the current instance with data from the api.
        
        Returns:
            self: The current APIResource instance with updated properties
        
        """
        return self.refresh_from(
            util.json.loads(
                self.make_request(method='GET', url_=self.instance_url()))
        )

    def refresh_from(self, resp):
        """
        Refresh From, updates the properties of the current instance with values
        from a dictionary 
        
        Args:
            resp (dict): Data to update teh instance properties with
        
        Returns:
            self: With Updated values
        
        """
        self.build_params = resp
        for k, v in resp.items():
            klass_name = k
            if klass_name == 'parent':
                klass_name = self.class_name()

            setattr(
                self,
                k,
                convert_to_emburse_object(
                    v,
                    self.auth_token,
                    klass_name=klass_name
                )
            )
        return self

    def instance_url(self):
        """
        Instance URL, gets the api end point for the current instance.
        
        Returns:
            str: URL for the current APIResource instance.
            
        Raises:
            error.InvalidRequestError: if the current instance does not have
            the id set.
        
        """
        if not self.id:
            raise error.EmburseInvalidRequestError(
                ('Could not determine which URL to request: {0} instance has' 
                 ' invalid ID: {1}').format(
                    type(self).__name__,
                    'id'
                )
            )
        id_ = util.utf8(self.id)
        base = self.class_url()
        extn = util.quote_plus(id_)
        return "{0}/{1}".format(base, extn)

    def make_request(self, method, url_, **params):
        """
        Make Request, method to send requests to the given api end point with
        given parameters. 
        
        Args:
            method (str): HTTP Method to use when making a request to the API.
            
            url_ (str): API endpoint URL for request.
            
            **params: The data to send to the API endpoint
        
        Returns:
            str: Raw response from the API
        
        """

        response, api_key = self.requestor.request(method=method.lower(),
                                                   url_=url_, params=params)
        return response

    def as_dict(self):
        """
        As Dict, converts a resource to a dictionary
        
        Returns:
            dict: A dictionary representation fo the current resource instance.
        
        """
        resource_as_dict = {}
        for property_name, property_value in self.build_params.items():
            if property_name == 'auth_token':
                continue
            prop = getattr(self, property_name)
            if isinstance(prop, APIResource):
                resource_as_dict[property_name] = prop.as_dict()
            else:
                resource_as_dict[property_name] = prop
        return resource_as_dict

    @classmethod
    def construct_from(cls, values, auth_token):
        """
        Construct From, builds an APIResource instance from the given data
        
        Args:
            values (dict): the data to build the instance from.
            
            auth_token (str): Your application's auth token.
            
        Returns:
            An APIResource instance of the same type with data from the given
            values.
        
        """
        instance = cls(auth_token=auth_token, **values)
        return instance

    @classmethod
    def class_name(cls):
        """
        Class Name, gets the name of the APIResource
        
        Returns:
            str: The lowercase name of the class
        
        Raises:
            emburse.errors.EmburseNotImplementedError: if cls is APIResource
        
        """
        if cls == APIResource:
            raise error.EmburseNotImplementedError(
                ('APIResource is an abstract class.  You should perform actions'
                 ' on its subclasses (e.g. Transaction, Card)')
            )
        return str(util.quote_plus(cls.__name__.lower()))

    @classmethod
    def class_name_plural(cls):
        """
        Class Name Plural, the plural form of the current class. In most cases
        just adding an 's' at the end of the class name will work. With a few
        exceptions this method needs to be over loaded to make the url building 
        methods work correctly.
        
        Returns:
            str: Plural form of the class name
        
        """
        return '{0}s'.format(cls.class_name())

    @classmethod
    def class_url(cls):
        """
        Class Url, builds the url for the current class.
        
        Returns:
            str: The endpoint url for the current class
            
        """
        cls_name = cls.class_name_plural()
        return "/{0}".format(cls_name)


class ListableAPIResource(APIResource):
    """
    Emburse Listable API Resource, any resource that can retrieve a list of
    objects will derive from this class.
    
    """

    def list(self, **params):
        """
        List, method to get a list of objects of the current resource type from
        the emburse api.
        
        Args:
            **params: Query parameters to filter list objects.
        
        Returns:
            A list of resource objects.
        
        """
        resp = util.json.loads(
            self.make_request(method='GET', url_=self.class_url(), **params))
        return [convert_to_emburse_object(v, self.auth_token,
                                          klass_name=self.class_name()) for v in
                resp.get(self.class_name_plural(), [])]


class CreateableAPIResource(APIResource):
    """
    Emburse Createable API Resource
    any resource that can be created will derive from this class.
    
    """

    @property
    def required_create_params(self):
        """
        Required Create Params, params required by the api to create a new
        resource.
        
        Returns:
            A list of dictionaries in the format of 
                {'name': param_name, 'type': param_type} 
        
        Example:
            >>> card.required_create_params
            [{'name': 'name', 'type': str}, {'name': 'code', 'type': int}]
                
        """
        return []

    def create(self, **params):
        """
        Create, creates a new resource with the given values.
        
        Args:
            **params: Values to create a new resource
        
        Returns:
            APIResource: New resource instance
        
        Raises:
            emburse.errors.EmburseResourceError: if the required_create_params
                list is empty.
            
            emburse.errors.EmburseAttributeError: if a required param is missing
                or of the wrong type.
            
        """
        if len(self.required_create_params) <= 0:
            raise error.EmburseResourceError(
                '{resource}: required create params left are empty!'.format(
                    resource=self.class_name()
                )
            )
        for required in self.required_create_params:
            if required.get('name') not in params or not isinstance(
                    params.get(required.get('name')),
                    required.get('type')
            ):
                raise error.EmburseAttributeError(
                    ('{name}: is a required property and must be of type' 
                     ' {type}!').format(
                        name=required.get('name'),
                        type=type(required.get('type'))
                    )
                )
            if isinstance(params.get(required.get('name')), APIResource):
                params[required.get('name')] = params[
                    required.get('name')].as_dict()
        return self.construct_from(
            values=util.json.loads(
                self.make_request(method='post', url_=self.class_url(),
                                  **params)),
            auth_token=self.auth_token
        )


class UpdateableAPIResource(APIResource):
    """
    Emburse Updateable API Resource, any resource that can be updated/edited
    will derive from this class.
    
    """

    def update(self, **params):
        """
        Update, updates the given values for the resource instance.
        
        Args:
            **params: Values to be updated
        
        Returns:
            self: Updated resource instance
        
        Raises:
            emburse.errors.EmburseAttributeError: if instance does not have an
            id set and the id was not in the params.
        
        Example:
            >>> card.update(state='suspended')
            <Card id='ce93d83a-8a43-439d-9f5b-cc6ed89ecf89', state='suspended'>
        
        """
        param_copy = params
        if not self.id:
            self.id = params.get('id', None)
        if not self.id:
            raise error.EmburseAttributeError(
                ('ID: is a required property and must be set to update/edit' 
                 ' this resource!')
            )
        param_copy['id'] = self.id
        for param_name, param_value in params.items():
            if isinstance(param_value, APIResource):
                param_copy[param_name] = param_value.as_dict()
        self.refresh_from(
            resp=util.json.loads(
                self.make_request(method='put', url_=self.instance_url(),
                                  **param_copy)),
        )
        return self


class DeletableAPIResource(APIResource):
    """
    Emburse Deletable API Resource, any resource that can be deleted will derive
    from this class.
    
    """

    def delete(self, identifier=None):
        """
        Delete, deletes a resource from the api
        
        Args:
            identifier (str, optional): The id of the resource to delete.
        
        Returns:
            self: Current resource instance
        
        Raises:
            emburse.errors.EmburseAttributeError: if id is not set on the
            instance and it was not passed in.
        
        """
        if not self.id:
            self.id = identifier
        if not self.id:
            raise error.EmburseAttributeError(
                ('ID: is a required property and must be set to delete this ' 
                 'resource!')
            )
        self.make_request(method='delete', url_=self.instance_url())
        return self


class Account(ListableAPIResource):
    """
    Emburse Account Resource
    
    API DOC: https://www.emburse.com/api/v1/docs#account
    
    """
    pass


class Allowance(ListableAPIResource):
    """
    Emburse Allowance Resource
    
    API DOC: https://www.emburse.com/api/v1/docs#allowance
    
    """

    @property
    def required_create_params(self):
        """
        Required Create Params, params required by the api to create a new
        resource.

        Returns:
            A list of dictionaries in the format of 
            {'name': param_name, 'type': param_type} 

        """
        return [
            {'name': 'interval', 'type': str},
            {'name': 'amount', 'type': float},
            {'name': 'transaction_limit', 'type': float}
        ]

    def create(self, **params):
        """
        Create, creates a new allowance resource with the given values, but does
        not send them to the api. This is used for creating a Card resource
        correctly.
        
        Args:
            **params: Values to create a new resource
        
        Returns:
            emburse.resource.Allowance instance
        
        Raises:
            emburse.errors.EmburseAttributeError: if a required param is missing
            or of the wrong type.
        
        :Example:
        
            >>> new_card = emburse_client.Card.create(
            >>>     'allowance': emburse_client.Allowance.create(
            >>>         interval='null',
            >>>         amount=100.00,
            >>>         transaction_limit=100.00
            >>>     ),  # This does not get sent to the api until card is created!
            >>>     'description': "Vendor #125",
            >>>     'is_virtual': True
            >>> )
            <Card allowance='<Allowance interval='null', amount=100,
            transaction_limit=100>', description='Vendor #125', is_virtual=True>
            
        """
        if len(self.required_create_params) <= 0:
            raise error.EmburseResourceError(
                '{resource}: required create params left are empty!'.format(
                    resource=self.class_name()
                )
            )
        for required in self.required_create_params:
            if required.get('name') not in params or not isinstance(
                    params.get(required.get('name')),
                    required.get('type')
            ):
                err_msg = ('{name}: is a required property and must be of type'
                           '{type}!')
                raise error.EmburseAttributeError(
                    err_msg.format(
                        name=required.get('name'),
                        type=type(required.get('type'))
                    )
                )
            if isinstance(params.get(required.get('name')), APIResource):
                params[required.get('name')] = params[
                    required.get('name')].as_dict()
        return self.construct_from(
            values=params,
            auth_token=self.auth_token
        )


class Card(ListableAPIResource, CreateableAPIResource, UpdateableAPIResource,
           DeletableAPIResource):
    """
    Emburse Card Resource
    
    API DOC: https://www.emburse.com/api/v1/docs#card
    
    """

    @property
    def required_create_params(self):
        """
        Required Create Params, params required by the api to create a new
        resource.

        Returns:
            A list of dictionaries in the format of 
            {'name': param_name, 'type': param_type} 

        """
        return [
            {'name': 'allowance', 'type': Allowance},
            {'name': 'description', 'type': str},
            {'name': 'is_virtual', 'type': bool}
        ]


class Category(ListableAPIResource, CreateableAPIResource,
               UpdateableAPIResource, DeletableAPIResource):
    """
    Emburse Category Resource
    
    API DOC: https://www.emburse.com/api/v1/docs#category
    """

    @property
    def required_create_params(self):
        """
        Required Create Params, params required by the api to create a new
        resource.

        Returns:
            A list of dictionaries in the format of 
            {'name': param_name, 'type': param_type} 

        """
        return [
            {'name': 'name', 'type': str}
        ]

    @classmethod
    def class_name_plural(cls):
        return 'categories'


class Company(APIResource):
    """
    Emburse Company Resource
    
    API DOC: https://www.emburse.com/api/v1/docs#company
    """

    @classmethod
    def class_name_plural(cls):
        return 'company'


class Department(ListableAPIResource, CreateableAPIResource,
                 UpdateableAPIResource, DeletableAPIResource):
    """
    Emburse Department Resource
    
    API DOC: https://www.emburse.com/api/v1/docs#department
    
    """

    @property
    def required_create_params(self):
        """
        Required Create Params, params required by the api to create a new
        resource.

        Returns:
            A list of dictionaries in the format of 
            {'name': param_name, 'type': param_type} 

        """
        return [
            {'name': 'name', 'type': str}
        ]


class Label(ListableAPIResource, CreateableAPIResource, UpdateableAPIResource,
            DeletableAPIResource):
    """
    Emburse Label Resource
    
    API DOC: https://www.emburse.com/api/v1/docs#label
    
    """

    @property
    def required_create_params(self):
        """
        Required Create Params, params required by the api to create a new
        resource.

        Returns:
            A list of dictionaries in the format of 
            {'name': param_name, 'type': param_type} 

        """
        return [
            {'name': 'name', 'type': str}
        ]


class Location(ListableAPIResource, CreateableAPIResource,
               UpdateableAPIResource, DeletableAPIResource):
    """
    Emburse Location Resource
    
    API DOC: https://www.emburse.com/api/v1/docs#location
    
    """

    @property
    def required_create_params(self):
        """
        Required Create Params, params required by the api to create a new
        resource.

        Returns:
            A list of dictionaries in the format of 
            {'name': param_name, 'type': param_type} 

        """
        return [
            {'name': 'name', 'type': str}
        ]


class Member(ListableAPIResource, CreateableAPIResource, UpdateableAPIResource,
             DeletableAPIResource):
    """
    Emburse Member Resource
    
    API DOC: https://www.emburse.com/api/v1/docs#member
    
    """
    pass


class SharedLink(ListableAPIResource, CreateableAPIResource,
                 UpdateableAPIResource, DeletableAPIResource):
    """
    Emburse SharedLink Resource
    
    API DOC: https://www.emburse.com/api/v1/docs#shared-link
    
    """

    @property
    def required_create_params(self):
        """
        Required Create Params, params required by the api to create a new
        resource.

        Returns:
            A list of dictionaries in the format of 
            {'name': param_name, 'type': param_type} 

        """
        return [
            {'name': 'card', 'type': str}
        ]

    @classmethod
    def class_name(cls):
        return 'shared-link'


class Statement(ListableAPIResource):
    """
    Emburse Statement Resource
    
    API DOC: https://www.emburse.com/api/v1/docs#statement
    
    """

    #: Constant for comma separated value format file
    CSV_FORMAT = 'csv'

    #: Constant for portable document format file
    PDF_FORMAT = 'pdf'

    #: Constant for open financial exchange format file
    OXF_FORMAT = 'oxf'

    def export(self, start_date=None, end_date=None, file_format=None):
        """
        Export, method to export the bank statement for the account in a
        optional date range. If no file format is given, will default to csv
        format. If no start date given will default to first of the month. If
        end date is not given will default to today.

        Args:
            start_date (datetime): Optional start of date range for statement

            end_date (datetime): Optional end of date range for bank statement

            file_format (str): Optional file format for the bank statement 

        Returns:
            The file contents in the requested format.

        Raises:
            error.EmburseValueError if account_id is not set.

            error.EmburseTypeError if start_date or end_date are not of type
            datetime.

        """
        valid_formats = [
            Statement.CSV_FORMAT,
            Statement.PDF_FORMAT,
            Statement.OXF_FORMAT
        ]
        account_id = getattr(self, 'account_id', None)
        params = {}
        if not account_id:
            raise error.EmburseValueError(
                'Account id must be set before calling method!'
            )
        if file_format not in valid_formats:
            file_format = Statement.CSV_FORMAT
        if start_date and not isinstance(start_date, datetime.datetime):
            raise error.EmburseTypeError(
                'Start date must be of type  datetime, {0} was given!'.format(
                    type(end_date)
                )
            )
        if end_date and not isinstance(end_date, datetime.datetime):
            raise error.EmburseTypeError(
                'End date must be of type datetime, {0} was given!'.format(
                    type(end_date)
                )
            )
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        url = '/accounts/{acc_id}/statement.{fmt}'.format(
            acc_id=account_id,
            fmt=file_format
        )
        resp = self.make_request(method='GET', url_=url, params=params)
        return resp

    def as_dict(self):
        """
        As Dict, is not implemented by this resource

        Returns:
            Never returns anything

        Raises:
            error.EmburseNotImplementedError

        """
        raise error.EmburseNotImplementedError(
            'Method not supported by this resource!'
        )

    def refresh(self):
        """
        Refresh, is not implemented by this resource

        Returns:
            Never returns anything

        Raises:
            error.EmburseNotImplementedError

        """
        raise error.EmburseNotImplementedError(
            'Method not supported by this resource!'
        )

    def retrieve(self, identifier):
        """
        Retrieve,, is not implemented by this resource

        Args:
            identifier (str): ID of the resource. 

        Returns:
            Never returns anything

        Raises:
            error.EmburseNotImplementedError

        """
        raise error.EmburseNotImplementedError(
            'Method not supported by this resource!'
        )


class Transaction(ListableAPIResource, UpdateableAPIResource):
    """
    Emburse Transaction Resource
    
    API DOC: https://www.emburse.com/api/v1/docs#transaction
    
    """
    pass