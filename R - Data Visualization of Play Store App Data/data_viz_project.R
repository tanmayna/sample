setwd('/Users/tanmay/Desktop/IST 719/Final Project')
library(tidyverse)
library(highcharter) 
library(lubridate)
library(stringr)
library(xts)
library(graphics)
library(RColorBrewer)
library(corrplot)
library(beanplot)
library(ggridges)
library(wordcloud)
library(tm)
library(SnowballC)


opar <- par()

col.play.store <- c("#3BCCFF", "#FF3333", "#FFD400", "#48FF48")

df_src <- read.csv('googleplaystore.csv',
               stringsAsFactors = F)

df <- df_src %>%
  mutate(
    Installs = gsub("\\+", "", as.character(Installs)),
    Installs = as.numeric(gsub(",", "", Installs)),
    Size = gsub("M", "", Size),
    Size = ifelse(grepl("k", Size), 0, as.numeric(Size)),
    Reviews = as.numeric(Reviews),
    Price = as.numeric(gsub("\\$", "", as.character(Price))),
    Last.Updated = mdy(Last.Updated),
    Min.Android.Ver = gsub("Varies with device", NA, Android.Ver),
    Min.Android.Ver = as.numeric(substr(Min.Android.Ver, start = 1, stop = 3)),
    Android.Ver = NULL
  ) %>%
  filter(
    Type %in% c("Free", "Paid")
  )

df <- df %>% 
  mutate(since_update =  difftime(Sys.Date(), df$Last.Updated, units = "days") %>% as.numeric()) %>% 
  mutate(since_update = since_update - min(df$since_update))

# Size v/s number of installs
df_size_vs_installs <- df %>% 
  filter(Installs <=1000000) %>% 
  filter(Installs >=100) %>% 
  # arrange(Installs) %>% 
  # head(7000) %>% 
  group_by(Installs) %>% 
  summarise(avg_size = mean(Size, na.rm = T))

par(bty = 'o', options(scipen = 6))
barplot(df_size_vs_installs$avg_size
     #, type = "l"
     , main = "Size v/s Installs for apps with less than 1,000,000 users"
     , ylab = "Aggregate Installs"
     , xlab = "Average Size of App (MBs)"
     , col = col.play.store
     , names.arg = df_size_vs_installs$Installs
     , horiz = T
     , border = NA
     , cex.lab = 1.5
     , cex.main = 2
     )

#Ratings in paid v/s free apps
df_ratings_vs_installs_free <- df %>% 
  filter(Installs >=1000) %>% 
  filter(Type == 'Free') %>% 
  mutate(Rating = round(Rating, 0)) %>% 
  pull(Rating)

ratings_free <- as.data.frame(table(unlist(df_ratings_vs_installs_free))) %>% 
  rename(Free = Freq) %>% 
  mutate(Free = round(Free/length(df_ratings_vs_installs_free), 3))

df_ratings_vs_installs_paid <- df %>% 
  filter(Installs >=1000) %>% 
  filter(Type == 'Paid') %>% 
  mutate(Rating = round(Rating, 0)) %>% 
  pull(Rating)

ratings_paid <- as.data.frame(table(unlist(df_ratings_vs_installs_paid))) %>% 
  rename(Paid = Freq) %>% 
  mutate(Paid = round(Paid/length(df_ratings_vs_installs_paid), 3))

free_and_paid <- merge(ratings_free, ratings_paid, by="Var1",all = T) %>% 
  mutate(Var1 = NULL) %>% 
  t()

par(bty = 'n')
barplot(free_and_paid
        , main = "Ratings distribution of Free and Paid Apps"
        , legend = c("Free","Paid")
        , beside = T
        , col = col.play.store[1:2]
        , names.arg = c(1,2,3,4,5)
        , border = NA
        , cex.lab = 1.5
        , cex.main = 2
        )

# Piechart Installs
pie_df <- df %>%
  group_by(Installs.Group = cut(Installs, breaks= seq(0, 1000000000, by = 50000))) %>% 
  summarise(n= n()) %>% 
  arrange(n)

pie_df <- df %>%
  group_by(Installs) %>% 
  summarise(n= n()) %>% 
  arrange(n)

pie_cols <- brewer.pal(9, "BuPu")

pie(pie_df$n
    , labels = pie_df$Installs
    , col = col.play.store
    , main = "Number of App Installs")

# Percentage of Paid apps by Category
perc_paid <- df %>% 
  group_by(Category, Type) %>%
  summarize(n = n()) %>%
  mutate(perc = round((n /sum(n))*100)) %>% 
  filter(Type == "Paid") %>% 
  select(Category, perc) %>%
  mutate(perc = as.integer(perc)) %>% 
  arrange(desc(perc)) %>% 
  head(5) %>% 
  as.data.frame()

barplot(perc_paid$perc
        , names.arg = perc_paid$Category
        , main = "Categories with the highest percentage of Paid apps"
        , col = "Orange"
        , ylab = "Percent of Paid Apps")

# Most famous app genres
genres <- df %>% 
  group_by(App) %>%
  top_n(n=1, wt=Reviews) %>% 
  ungroup() %>% 
  group_by(Category) %>%
  summarize(n = n()) %>% 
  arrange(desc(n)) %>% 
  as.data.frame() %>% 
  head(7)

genres[6, 1] <- ""

par(bty="n")
plot(genres$n
    , type = "p"
    , names.arg = genres$Category
    , col = "White"
    , ylab = "Number of Apps"
    , xlab = "Genres"
    , xlim = c(1,8)
    , ylim = c(200,2200)
    , xaxt = 'n'
    , yaxt = 'n'
    , cex.lab = 1.5
    , cex.main = 2)

text(genres$n, genres$Category,labels=genres$Category,col = col.play.store
     ,cex = 2.5)

apps_by_genre <- df %>% 
  group_by(Genres) %>% 
  top_n(n = 20, wt = Reviews)


#Top paid games by Genre
games.genres <- df %>% 
  filter(Category == 'GAME') %>% 
  filter(Price>0) %>% 
  select(Genres, Price) %>% 
  group_by(Genres) %>% 
  summarise(n = n()) %>% 
  slice(1:7) %>% 
  pull(Genres)
  
games.df <- df %>% 
  filter(Category == 'GAME') %>% 
  filter(Genres %in% games.genres) %>% 
  filter(Price>0) %>% 
  select(Genres, Price)

par(bty="n")
beanplot(Price~Genres
         , data=games.df
         , log=""
         , bw="nrd0"
         , col = col.play.store
         , main="Paid Games By Genre"
         , cex.lab = 1.5
         , xlab = ""
         , cex.main = 2)

axis(1,cex.axis=2, labels = games.df$Genres)


#Correlation matrix
COR <- cor(df %>% 
             na.omit() %>% 
             filter(Installs <=1000000) %>% 
             select(Rating, Reviews, Size, Installs))


par(bty="o", xpd=NA)
image(x=seq(nrow(COR)), y=seq(ncol(COR)), z=cor(M), axes=F, xlab="", ylab="",
      col = colorRampPalette(c("Yellow","Green","Red","Blue"))(12)
      , xaxt='n')

text(expand.grid(x=seq(dim(COR)[1]), y=seq(dim(COR)[2])), labels=round(c(COR),2)
     ,cex = 2)
box()
axis(1, at=seq(nrow(COR)), labels = rownames(COR), las=2, cex.axis = 1)
axis(2, at=seq(ncol(COR)), labels = colnames(COR), las=1, cex.axis = 1)

dev.off()

corrplot(M, method = "circle", type="upper"
         , col = colorRampPalette(c("Yellow","Green","Red","Blue"))(12)
         , cex.lab = 2) #plot matrix

text(expand.grid(x=seq(dim(M)[1]), y=seq(dim(M)[2])), labels=round(c(M),2)
     ,cex = 2)
box()
axis(1, at=seq(nrow(M)), labels = rownames(M), las=2, cex.axis = 1.5)
axis(2, at=seq(ncol(M)), labels = colnames(M), las=1, cex.axis = 1.5)

### REVIEWS --- 
df_reviews <- read.csv('googleplaystore_user_reviews.csv', stringsAsFactors = F)

positive.reviews <- df_reviews %>% 
  filter(Sentiment == 'Positive') %>% 
  pull(Translated_Review)

negative.reviews <- df_reviews %>% 
  filter(Sentiment == 'Negative') %>% 
  pull(Translated_Review)

# Load the text as a corpus
clean_word_cloud <- function(text){
  docs <- Corpus(VectorSource(text))
  docs<-tm_map(docs,stripWhitespace)
  docs<-tm_map(docs,tolower)
  docs<-tm_map(docs,removeNumbers)
  docs<-tm_map(docs,removePunctuation)
  docs<-tm_map(docs,removeWords, stopwords("english"))
  
  docs<-tm_map(docs, 
               removeWords, 
               c("and","the","our","that","for","are","also","more","has","must"
                 ,"have","should","this","with","game","get"))
  return(docs)
  
}

docs <- clean_word_cloud(positive.reviews)

wordcloud(docs, scale=c(5,0.5), max.words=50, 
          random.order=FALSE, rot.per=0.35, 
          use.r.layout=FALSE, colors=col.play.store
          , main = "Positive Reviews")

docs <- clean_word_cloud(negative.reviews)

wordcloud(docs, scale=c(5,0.5), max.words=50, 
          random.order=FALSE, rot.per=0.35, 
          use.r.layout=FALSE, colors=col.play.store
          , main = "Negative Reviews")
