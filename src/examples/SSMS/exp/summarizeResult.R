library(tidyverse)

tb = read_csv("Desktop/So Simple Mobility Simulation/src/examples/SSMS/exp/results_fog_offloading/Results_one_0.csv")
not_sink <- tb %>% filter(type != "SINK_M") %>% select(id, type, time_emit)
sink <- tb %>% filter(type == "SINK_M") %>% select(id, type, time_out)

sink %>% left_join(not_sink, by = "id") %>%
  group_by(id) %>%
  mutate(response_time = max(time_out) - min(time_emit)) %>% 
  ungroup() %>%
  select(id, response_time) %>%
  distinct() %>% 
  summarize(mean_response_time = mean(response_time), 
            max_response_time = max(response_time),
            sd = sd(response_time),
            count = n())

sink %>% left_join(not_sink, by = "id") %>%
  group_by(id) %>%
  mutate(response_time = max(time_out) - min(time_emit)) %>% 
  ungroup() %>%
  select(id, response_time) %>%
  distinct() %>% 
  group_by(latency=cut(response_time, breaks= seq(0, 1000, by = 100)) ) %>% 
  summarise(num_of_task= n()) %>%
  arrange(as.numeric(latency)) %>%
  ggplot() + geom_col(aes(x = latency, y = num_of_task)) +
  ggtitle("Fog Without Offloading")
  
