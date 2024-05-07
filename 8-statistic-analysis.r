# First: Run line below in command line (to add R to path) 
# export PATH="/home/wharmsen/R/bin:$PATH"
# echo $PATH (to check whether adding to path went correctly)
# CRAN mirror = 56 (Dronten)

# Rscript /vol/tensusers5/wharmsen/ASTLA/slate-scripts/8-statistic-analysis.r
# It is possible you have to install the packages first (terminal -> R -> install.packages())

# install.packages("languageserver")
# install.packages("irr")
# install.packages("rmarkdown")

library("irr")

teacherData = read.csv('/vol/tensusers5/wharmsen/astla-data/dart-preposttest/slate-data/7-binary-assessments/assessments.csv',sep=',')

# Print head of data
head(teacherData[, 3:53])
# all rows, column 2:4 (index starting at 1 instead of 0, 4 is included)

# Select all raters
mydata <- teacherData[, 3:53]

#Compute Fleiss Kappa
kappam.fleiss(mydata)

