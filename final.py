from flask import Flask, render_template, request
import pickle
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

# Load model and data
movies_dict = pickle.load(open('movies_dict.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)


def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = similarity[index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
    recommended_movies = []

    for i in movie_list:
        recommended_movies.append({
            'title': movies.iloc[i[0]].title,
            # 'poster': movies.iloc[i[0]].poster_url  # you need poster_url in your dataframe
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
