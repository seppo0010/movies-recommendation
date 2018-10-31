var renderedMovie;

function render_movie(movie) {
  renderedMovie = movie;
  document.body.setAttribute('id', 'movie_page')
  document.getElementById('movie-title').innerText = movie.title;
  document.getElementById('movie-year').innerText = movie.release_date.substr(0, 4);
}

function buttonClicked(ev) {
  fetch('rank', {
      method: 'POST',
      headers: {
        "Content-Type": "application/json; charset=utf-8",
      },
      body: JSON.stringify({value: ev.currentTarget.getAttribute('id'), id: renderedMovie.id}),
    })
    .then((response) => response.status < 400 ?
        Promise.resolve() :
        Promise.reject(response.statusText))
    .then(fetchMovie)
    .catch((e) => render_error(e))
}

function render_error(err) {
  alert(err)
}

function fetchMovie() {
  fetch('movie_to_rank')
    .then((response) => response.status < 400 ?
        response.json() :
        Promise.reject(response.statusText))
    .then((data) => render_movie(data))
    .catch((e) => render_error(e))
}

document.addEventListener('DOMContentLoaded', () => {
  Array.prototype.forEach.call(document.getElementsByTagName('button'), (b) => b.addEventListener('click', buttonClicked));
  fetchMovie()
});
