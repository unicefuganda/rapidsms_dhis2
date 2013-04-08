
class DataError(LookupError):
  def __init__(self, message, xform):
      LookupError.__init__(self, message)
      self.xform = xform
  
class FacilityError(LookupError):
  def __init__(self, message, facility):
      LookupError.__init__(self, message)
      self.facility = facility
