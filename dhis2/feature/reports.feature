Feature: Test the reports generation 

  Scenario: Reports
    Report data must have all valid fields 
    Must fetch all submissions made within the specified period
    
  Scenario: Submissions
     Given the required facility UUID exists in mtrack 
     Reporter must be able to use the generated reports data to make posts to dhis2
    