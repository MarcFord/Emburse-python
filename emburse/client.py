from emburse.resource import (
    EmburseObject,
    Account,
    Allowance,
    Card,
    Category,
    Company,
    Department,
    Label,
    Location,
    Member,
    SharedLink,
    Statement,
    Transaction
)


class Client(EmburseObject):
    """
    Emburse API Client
    
    API enables for the creation of expense cards at scale for custom business solutions as well as for 
    third-party app integrations. Cards can be created with set spending limits and assigned with just an email. 
    Some use cases include vendor payments, employee expense control, and fleet card management.
    
    API Version: 
        v1
    API Docs: 
        https://www.emburse.com/api/v1/docs#getting-started
    Authors:
        Marc Ford <marc.ford@gmail.com>
        
    """

    @property
    def Account(self):
        """
        Emburse Account Object,
        configured with the auth token from the client
        :return: A configured emburse.resource.Account
        :rtype: Account
        """
        return Account(auth_token=self.auth_token)

    @property
    def Allowance(self):
        """
        Emburse Allowance Object,
        configured with the auth token from the client
        :return: A configured emburse.resource.Allowance
        :rtype: Allowance
        """
        return Allowance(auth_token=self.auth_token)

    @property
    def Card(self):
        """
        Emburse Card Object,
        configured with the auth token from the client
        :return: A configured emburse.resource.Card
        :rtype: Card
        """
        return Card(auth_token=self.auth_token)

    @property
    def Category(self):
        """
        Emburse Category Object,
        configured with the auth token from the client
        :return: A configured emburse.resource.Category
        :rtype: Category
        """
        return Category(auth_token=self.auth_token)

    @property
    def Company(self):
        """
        Emburse Company Object,
        configured with the auth token from the client
        :return: A configured emburse.resource.Company
        :rtype: Company
        """
        return Company(auth_token=self.auth_token)

    @property
    def Department(self):
        """
        Emburse Department Object,
        configured with the auth token from the client
        :return: A configured emburse.resource.Department
        :rtype: Department
        """
        return Department(auth_token=self.auth_token)

    @property
    def Label(self):
        """
        Emburse Label Object,
        configured with the auth token from the client
        :return: A configured emburse.resource.Label
        :rtype: Label
        """
        return Label(auth_token=self.auth_token)

    @property
    def Location(self):
        """
        Emburse Location Object,
        configured with the auth token from the client
        :return: A configured emburse.resource.Location
        :rtype: Location
        """
        return Location(auth_token=self.auth_token)

    @property
    def Member(self):
        """
        Emburse Member Object,
        configured with the auth token from the client
        :return: A configured emburse.resource.Member
        :rtype: Member
        """
        return Member(auth_token=self.auth_token)

    @property
    def SharedLink(self):
        """
        Emburse SharedLink Object,
        configured with the auth token from the client
        :return: A configured emburse.resource.SharedLink
        :rtype: SharedLink
        """
        return SharedLink(auth_token=self.auth_token)

    @property
    def Statement(self):
        """
        Emburse Statement Object,
        configured with the auth token from the client
        :return: A configured emburse.resource.Statement
        :rtype: Statement
        """
        return Statement(auth_token=self.auth_token)

    @property
    def Transaction(self):
        """
        Emburse Transaction Object,
        configured with the auth token from the client
        :return: A configured emburse.resource.Transaction
        :rtype: Transaction
        """
        return Transaction(auth_token=self.auth_token)
