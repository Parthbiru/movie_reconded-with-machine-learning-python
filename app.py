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

# TMDb API Key (replace with your own key)
TMDB_API_KEY = 'dab47938bb350c568633125237f89527'  # 🔁 Change this line

def fetch_poster(title):
    """Fetch poster URL from TMDb API using movie title."""
    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={title}"
    response = requests.get(url)
    data = response.json()
    if data['results']:
        poster_path = data['results'][0].get('poster_path')
        if poster_path:
            return "https://image.tmdb.org/t/p/w500" + poster_path
    return "https://via.placeholder.com/300x450?text=No+Image"

def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = similarity[index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
    recommended_movies = []
    for i in movie_list:
        title = movies.iloc[i[0]].title
        poster = fetch_poster(title)
        recommended_movies.append({
            'title': title,
            'poster': poster
        })
    return recommended_movies

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        movie_name = request.form['movie']
        recommendations = recommend(movie_name)
        return render_template('index.html', movies=recommendations, selected=movie_name, all_movies=movies['title'].values)
    return render_template('index.html', movies=[], selected=None, all_movies=movies['title'].values)

if __name__ == '__main__':
    app.run(debug=True)
