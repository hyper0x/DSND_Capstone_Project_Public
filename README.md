# DSND_Capstone_Project
The Capstone Project for DSND.

## Starbucks Capstone Challenge

## Table of Contents

1. [Installation](#installation)
2. [Project Motivation](#motivation)
3. [File Description](#files)
4. [Folder Description](#folders)
5. [Instructions](#instructions)
6. [Results](#results)
7. [Blog](#blog)
8. [Licensing](#licensing)

### Installation <a name="installation"></a>

The code in this project is written in Python, and the specific version is `3.7.1`.

The libraries required to run all the code in this project have been documented in the file named requirements.txt.

### Project Motivation <a name="motivation"></a>

I'm interested in Starbucks data, although the data isn't entirely real. I want to know how their customers are doing in the Starbucks promotion process. These customers should respond to the offer according to their needs. But what are the potential reasons for their response or non-response to an offer? It may not be easy to find out the reason, I need to mine the data layer by layer. After that, I will also try to divide these customers to help Starbucks adopt different promotional strategies for them.

I will study these data to clarify the following questions:

1. What are the characteristics of every offer?
2. What are the customer's gender, age and income?
3. How many of the various types of events are recorded in the transcript data? 
4. When did all those events happen? Are there some potential links between them?
5. What is a valid response to an offer?
6. What is the valid customer response rate for each type of offer?
7. How will different customers respond differently to different kinds of offer?
8. How many clustering do we need to divide our customers into? 

These questions will be answered in the process of my study. I have two primary targets. One is figuring out which customers are more sensitive to which offers. Another is to divide customers into different clustering.

### File Description <a name="files"></a>

A brief description of  the important files in this project is as follows:

- Starbucks_Capstone_notebook.ipynb: This file contains all the records of the process from getting the original data to the conclusion. It includes codes, images, and descriptions. The general steps of this process are: exploring the original data, cleaning up the data, transforming the data, building a clustering model based on the data, explaining the results of the clustering, and finally the conclusion.
- *.py: It refers to several Python source files. These files contain all the codes that implement essential functionality. Among them, cleaner.py, combiner.py and model.py can be executed in the command line. They are executed in sequence to produce a trained and evaluated cluster model.

### Folder Description <a name="folders"></a>

- data: This folder contains all the original files in JSON format.
- processed_data: This folder contains all intermediate results. These results are stored separately as pickle files. This folder will be created by the command line program of this project during execution.
- model: This folder contains the final model and the labeled data. They are also stored as pickle files. This folder will be created by the command line program of this project during execution.
- images: This folder is used to hold great graphics that I drew during my study.

### Instructions <a name="instructions"></a>

You can use the Python command to execute cleaner.py, combiner.py, and model.py in turn to get a pickle file that can represent the clustering model. Some of the files that are generated in this process that serve intermediate results will be stored in the "processed_data" folder. The file representing the model and a file representing labeled data will be saved in the "model" folder.

### Results <a name="results"></a>

Overall, the ratio of customers responding to BOGO offer to discount offer is not the same. The rate of customers responding to discount offer is significantly larger. Besides, some customers will respond to the same offer multiple times. The discount offer is still better in this respect. However, judging by the ranking of these offer for customer response ratios, I have not found a law that is directly related to the characteristics of the offer. 

The average consumption amount for female customers is the highest. Surprisingly, the number of customers of other genders, although small, has performed well in this area and is in second place. And for the average of responses, the average number of responses per offer and the average of rewards, this part of the customer's performance even ranked first. The worst performers are customers of unknown gender. 

There is a positive correlation between the customer's income and the number of times they respond to the offer. This relationship is particularly pronounced among male customers. And there is a relationship between customers' income and the amount they pay when they respond to an offer. As for the difficulty, duration, and reward of the offer, there is little relationship between them and the number of times customers respond to an offer.

However, if we only look at the discount offer, we will find that there is a more apparent negative correlation relationship between the various counts about customer response and the difficulty of the offer. That is, the higher the consumption threshold for discount offer, the fewer customers respond.

On the whole, female customers have a similar attitude towards both types of offer, but they spend significantly more on responding to BOGO offer, and they get more rewards as a result. Male customers have a clear preference for discount offer, but they spend a little more on their response to BOGO offer, as well as on the rewards they receive. Customers of other genders are slightly more motivated to respond to discount offer, and they spend significantly more on responding to such offer, but receive fewer rewards.

As a result, Starbucks customers are more fond of discount offer. This is also amply illustrated by the various data and diagrams that I have shown in the course of my analysis. Starbucks can use the results of this analysis to send more discount offer to male customers and customers of other genders, and to send more BOGO offer to female customers. Given that male customers are spending a higher amount of money when they respond to BOGO offer, I think it's OK for Starbucks to send them more BOGO offers.


---------
I divided Starbucks customers into 6 clustering through a clustering model.

The characteristics of these customers are still relatively obvious. First of all, I think Starbucks should focus on the customers that cluster 0 and cluster 4 contain. Second, they can focus on developing the customers included in cluster 1.

![Figure - Average numbers of times customers responded to each offer in different clusters](images/response_clusters-resp_number_mean.png)

For cluster 2 contains customers and clustering 3 of customers, because their preference for different kinds of the offer is pronounced, so I think Starbucks should adapt to their favorites. Further, we can look at the reasons why they have such a preference. For example, the reason some customers have a clear choice for BOGO offer is that they often enjoy coffee with their friends. If that's the case, then Starbucks can usually send them an offer for a variety of combination packages. On the contrary, if customers prefer discount offers, Starbucks can offer them a discount strategy in the form of a ladder.

Also, for cluster 5 customers, I think Starbucks can put them in the lowest position. They're not supposed to be Starbucks regular customers. Most of them are of medium age and income but do not seem interested in any form of promotion.

Finally, if we want to get more value out of the data, we should make the information in profile richer. And, for the informational offer, I didn't get valuable information in this study. I think this part of the data is still essential, unfortunately in the transcript does not contain records related to them.

### Blog

For a general description of the project and the analysis process involved, see [my blog](#)

### Licensing <a name="licensing"></a>

See [LICENSE](LICENSE) for details.