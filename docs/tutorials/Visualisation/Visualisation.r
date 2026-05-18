library(tidyverse)
library(dbplyr)

#Connect to database
db <- DBI::dbConnect(RSQLite::SQLite(),"outputs/KAPy_outputs.sqlite")
dat <- tbl(db,"View_Ensemble_Statistics")

#Extract temperature data
temp <-
  dat %>% 
  filter(IndicatorCode=="101",
         SeasonCode=="ann",
         ArealStatisticCode=="mean",
         Percentile==50,
         Delta==0)  %>% 
  collect()

#Prepare data for plotting and plot
temp %>% 
  mutate(PeriodCode=factor(PeriodCode,
                           levels = unique(PeriodCode),
                           labels = unique(PeriodDescription),
                           ordered = TRUE)) %>% 
  ggplot(aes(x=PeriodCode,y=Value,colour=ScenarioCode,shape=ScenarioCode,group=ScenarioCode))+
  geom_point()+
  geom_line()+
  theme_bw(base_size=14)+
  labs(x="Period",
       y="Mean annual temperature")
  
  
  