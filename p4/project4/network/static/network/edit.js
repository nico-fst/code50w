document.addEventListener('DOMContentLoaded', function() {
  const buttons = document.querySelectorAll('.edit, .like');

  buttons.forEach((button) => {
    button.addEventListener('click', () => {
      if (button.classList.contains('edit'))
        edit(button);
      else
        toggle_like(button);
    });
  });
});

function edit(button) {
  const post_id = button.getAttribute('data-post_id');

  fetch(`/posts/${post_id}`)
      .then((response) => response.json())
      .then((post) => {
        console.log(post);
        const postContent = document.querySelector(`#post-${post_id}`);

        const textarea = document.createElement('textarea');
        textarea.value = post.content;

        const saveButton = document.createElement('button');
        saveButton.textContent = 'Save';
        saveButton.classList.add('btn', 'btn-primary');
        saveButton.addEventListener(
            'click', () => save(post_id, textarea.value));

        postContent.innerHTML = '';
        postContent.appendChild(textarea);
        postContent.appendChild(saveButton);
      });
}

function save(post_id, text) {
  fetch(`/posts/${post_id}`, {
    method: 'PUT',
    body: JSON.stringify({content: text}),
  }).then((response) => {
    if (response.ok) {
      const postContent = document.querySelector(`#post-${post_id}`);
      postContent.innerHTML = text;
    }
  });
}

function toggle_like(button) {
  const post_id = button.getAttribute('data-post_id');
  const like_span = document.querySelector(`#like-${post_id}`);

  fetch(`/toggle_like/${post_id}`)
    .then((response) => {
      if (response.ok) {
        return response.json();  // Parse the JSON response
      } else {
        throw new Error('Failed to fetch toggle_likes');
      }
    })
    .then(data => {
      console.log(data.message);

      const liked = data.message === 'like added' ? true : false;
      button.innerHTML = liked ? "Unlike" : "Like";
      like_span.innerHTML =
        liked ? parseInt(like_span.innerHTML) + 1 : parseInt(like_span.innerHTML) - 1;
    });
}
