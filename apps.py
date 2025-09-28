from flask import Flask, render_template, request
import pickle
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import requests

app = Flask(__name__)

# Load model and data
movies_dict = pickle.load(open('movies_dict.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)

TMDB_API_KEY = 'fb7bb23f03b6994dafc674c074d01761'
# TMDb API

def fetch_poster(title):
    search_url = f'https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={title}'
    response = requests.get(search_url)
    data = response.json()
    if data['results']:
        poster_path = data['results'][0].get('poster_path')
        if poster_path:
            return "https://image.tmdb.org/t/p/w500" + poster_path
    return "https://via.placeholder.com/500x750?text=No+Image"

def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = similarity[index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
    
    recommended_movies = []
    for i in movie_list:
        title = movies.iloc[i[0]].title
        poster_url = fetch_poster(title)
        recommended_movies.append({
            'title': title,
            'poster': poster_url
        })
    return recommended_movies



# def recommend(movie):
#     index = movies[movies['title'] == movie].index[0]
#     distances = similarity[index]
#     movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
#     recommended_movies = []

#     # Fetch poster URLs using TMDb API
#     url = f'https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}&language=en-US&page=1'
#     response = requests.get(url)
#     data = response.json()
#     image_base_url = "https://image.tmdb.org/t/p/w500"

#     for i in movie_list:
#         recommended_movies.append({
#             'title': movies.iloc[i[0]].title,
#             'poster': image_base_url + movie_list['poster_path']
#             # 'poster': movies.iloc[i[0]].poster_url  # you need poster_url in your dataframe
#         })
#     return recommended_movies

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        movie_name = request.form['movie']
        recommendations = recommend(movie_name)
        return render_template('index.html', movies=recommendations, selected=movie_name, all_movies=movies['title'].values)
    return render_template('index.html', movies=[], selected=None, all_movies=movies['title'].values)

if __name__ == '__main__':
    app.run(debug=True)
