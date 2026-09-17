library(tidyverse)
library(dbplyr)

#Connect to database
db <- DBI::dbConnect(RSQLite::SQLite(),"outputs/KAPy_database.sqlite")
dat <- tbl(db,"View_EnsembleArealStatistics")

#Extract temperature data
temp <-
  dat %>% 
  filter(IndicatorCode=="101",
         SeasonCode=="ann",
         StatisticTypeCode=="mean",
         Percentile==50,
         Delta==0)  %>% 
  collect()

#Prepare data for plotting and plot
temp %>% 
  ggplot(aes(x=TimeBinCode,y=Value,colour=ScenarioCode,shape=ScenarioCode,group=ScenarioCode))+
  geom_point()+
  geom_line()+
  theme_bw(base_size=14)+
  labs(x="Period",
       y="Mean annual temperature")
  
  
  