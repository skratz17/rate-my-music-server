# Rate My Music API

## What Is This?

Welcome to the repo that houses the server-side API that powers [Rate My Music](https://ratemymusic.jacobweckert.com) - an exciting and amazing new application that is described in greater detail in the [repo for the client-side application](https://github.com/skratz17/rate-my-music-client).

## Nifty Features

* Pagination and sorting of all lists of resources. For instance - do you want the second page of songs (with ten results per page), between the years 1989 and 1994, sorted by average user rating descending? Sweet! `/songs?page=2&pageSize=10&startYear=1989&endYear=1994&orderBy=avgRating&direction=desc` will do the trick!
* Meaningful HTTP response codes on both success and failures, in addition to descriptive error messages if a response with status code >= 400 is being returned.
* Strong validation checks to ensure users cannot edit or remove any resources added by other users, as well as to generally ensure that data sent in requests is properly formatted and valid.

## Technologies Used

This application was created using [Django](https://www.djangoproject.com/), and the [Django REST Framework](https://www.django-rest-framework.org/). These technologies allowed me to rapidly build out an extensive REST API with many different resources, 

I wrote a full test suite for the API code in this repo, all of which can be found in the top-level [tests directory](https://github.com/skratz17/rate-my-music-server/tree/main/tests). These tests allowed me to confidently make any changes or additions to any code in my app while being sure that my changes would not negatively impact the health of my app as a whole. It was a great experience!

## Planning Resources

Below are links to the ERD for this project, as well as the Figma mockups I made and used as a guideline for how the UI should be implemented. 

* [ERD](https://dbdiagram.io/d/5fce88eb9a6c525a03ba26fc)
* [Figma Wireframe](https://www.figma.com/file/UAXwF0vzyIztgS9m5CSjfw/Full-Stack-Capstone?node-id=0%3A1)

## Author

Jacob Eckert - [GitHub](https://github.com/skratz17), [LinkedIn](https://www.linkedin.com/in/jacob-w-eckert/) 