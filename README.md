# Shelfsounds

This is a music tracking website, where users create an account and collections that store music. Example of collections include:

- Favorite Artists of all time
- Favorite Albums of all time
- Favorite Albums of 2025
- My Vinyl Collection

The idea that sparked this project was I originally wanted to show off all of the records that I own. I realized that getting the album covers for every album I own will be tedious to retrieve and save onto the page. That's when I got the idea of looking into api's that can get music data. I looked into the Spotify API and found that it returns data that I need.

Spotify API: https://developer.spotify.com/documentation/web-api

That's also when I realized that I can create a website that isn't just for me, but for anyone else that would like to easily showcase music they enjoy.

# Stack

- Django Backend
- Spotify API
- Spotipy, Python Library that works directly with the Spotify API
- MySQL DB
- Nginx
- Docker Compose for web server setup

# API Integration

I used the /search endpoint because it simulates a typical Spotify search where you can get a mix of results based off your input.

Spotify Search Endpoint: https://developer.spotify.com/documentation/web-api/reference/search

I send the user input to this endpoint and search albums and artists. I wanted to be able to replicate Spotify search where you get top results based on your input. If you type in the first three letters of a popular musicians name, you want to expect that artist to be the top result. However, the Spotify doesn't filter this by default. It does include a `popularity` key that gives each result a integer value. Spotify states, "Artist and album popularity is derived mathematically from track popularity." Using this, I sort the popularity of album and artists results and these sorted dictionaries get displayed on screen.

When I was working on this project, I noticed one interesting thing regarding Spotify search. The top result is usually what Spotify thinks you're trying to find and then it gives you other results based on your top result.

For example, if I look up the album `Innerspeaker` by Tame Impala, I should expect that album to be the top result. However, under the artist results the top result should be `Tame Impala` himself. Another interesting thing I noticed, is that the artist of the top resulting album, their other albums are also part of the album results. Same thing if an artist is the top results, the album results are usually that artists albums before results of albums with your search input.

Here are demo videos representing both cases:

Searching an album:

[album-top.webm](https://github.com/user-attachments/assets/18db9ef0-67ef-4701-86e3-08a8b325a47f)

Searching an artist:

[artist-top.webm](https://github.com/user-attachments/assets/7ed4d490-efb2-4b6e-b8a2-e924175a0f39)

The user is then able to click on an artist or album and choose a collection for them to save it to.

# Database Integration

As stated before, my original intent for this project was to not manually acquire album covers. The way I do this is through the API and the database. 

## Models

- Artist
    - user (FK)
    - uri
    - name
    - image
    - genre

- Album
    - user (FK)
    - title
    - release_year
    - cover_art
    - artist
    - genre

You may notice that the user that is saving the artist or album is the Foreign Key for both models. This is so that each album and artist is associated with that user. I had this for future ideas of custom album art and artist images. 

The album art and artist images are saved as URLFields. I save the url provided from the API and store this url. Then when a user goes to a collection, the src in the HTML for the img is this url when the page is rendered.

# Other Features

- Friends list
- Editing a Collection

# Demo

Here is a demo video showcasing how searching and saving works:

[demo.webm](https://github.com/user-attachments/assets/1b761209-2535-452d-ab99-cbc1e3f1916a)

