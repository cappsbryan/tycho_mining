-- $ head -n 2 "cumulative all conditions weekly US.csv"
-- ConditionName,ConditionSNOMED,PathogenName,PathogenTaxonID,Fatalities,CountryName,CountryISO,Admin1Name,Admin1ISO,Admin2Name,CityName,PeriodStartDate,PeriodEndDate,PartOfCumulativeCountSeries,AgeRange,Subpopulation,PlaceOfAquisition,DiagnosisCertainty,SourceName,CountValue,DOI
-- Acquired immune deficiency syndrome,62479008,Human immunodeficiency virus,12721,0,UNITED STATES OF AMERICA,US,WISCONSIN,US-WI,NA,NA,1984-01-01,1984-03-24,1,0-130,None specified,NA,NA,US Nationally Notifiable Disease Surveillance System,2.0,10.25337/T7/ptycho.v2.0/US.62479008

CREATE TABLE cumulative_all_conditions (
  ConditionName varchar(300) not null,
  ConditionSNOMED bigint not null,
  PathogenName varchar(300),
  PathogenTaxonID int,
  Fatalities int not null,
  CountryName varchar(300) not null,
  CountryISO varchar(10) not null,
  Admin1Name varchar(300) not null,
  Admin1ISO varchar(10) not null,
  Admin2Name varchar(300),
  CityName varchar(300),
  PeriodStartDate date not null,
  PeriodEndDate date not null,
  PartOfCumulativeCountSeries bool not null,
  AgeRangeStart int not null,
  AgeRangeEnd int not null,
  Subpopulation varchar(300),
  PlaceOfAquisition varchar(300),
  DiagnosisCertainty varchar(300),
  SourceName varchar(300) not null,
  CountValue varchar(300) not null,
  DOI varchar(300) not null
);

CREATE TABLE noncumulative_all_conditions (
  ConditionName varchar(300) not null,
  ConditionSNOMED bigint not null,
  PathogenName varchar(300),
  PathogenTaxonID int,
  Fatalities int not null,
  CountryName varchar(300) not null,
  CountryISO varchar(10) not null,
  Admin1Name varchar(300) not null,
  Admin1ISO varchar(10) not null,
  Admin2Name varchar(300),
  CityName varchar(300),
  PeriodStartDate date not null,
  PeriodEndDate date not null,
  PartOfCumulativeCountSeries bool not null,
  AgeRangeStart int not null,
  AgeRangeEnd int not null,
  Subpopulation varchar(300),
  PlaceOfAquisition varchar(300),
  DiagnosisCertainty varchar(300),
  SourceName varchar(300) not null,
  CountValue varchar(300) not null,
  DOI varchar(300) not null
);
