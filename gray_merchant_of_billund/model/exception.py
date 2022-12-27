class GMoBException(Exception):
    pass


class GMoBResourceException(GMoBException):
    pass


class PersonalCollectionException(GMoBResourceException):
    pass


class BricklinkException(GMoBResourceException):
    pass


class ParseException(Exception):
    pass


class PersonalCollectionParseException(
    PersonalCollectionException, ParseException
):
    pass


class BricklinkParseException(BricklinkException, ParseException):
    pass


class BricklinkQuotaError(BricklinkException):
    pass


class BricklinkLoginException(BricklinkException, ParseException):
    pass
