document.addEventListener("DOMContentLoaded", function () {
  // Use buttons to toggle between views
  document
    .querySelectorAll(".edit").forEach((btn) => {
      // get post key id and edit corresponding post
      let id = btn.id.slice(4)
      btn.addEventListener("click", () => edit(btn, id))
    })

  document
    .querySelectorAll(".like").forEach((btn) => {
      // get post key id and edit corresponding post
      let id = btn.id.slice(4)
      btn.addEventListener("click", () => like(btn, id))
    })

  document.querySelector("#follow").onclick = () => {
    let username = document.querySelector("h2").id
    follow(username)
  }
});

function edit(editbtn, postid) {
  // show textarea instead of previous content to edit
  let post = document.querySelector(`#content${postid}`)
  let postBefore = post.textContent
  // create textarea prefilled with previous post and add a submit button
  post.innerHTML = `<form id="editform${postid}"><textarea id="editarea${postid}">${postBefore}</textarea><button type="submit" class="btn btn-light btn-sm edit" id="post${postid}">Post</button></form>`
  editbtn.style.display = "none"
  let postbtn = document.querySelector(`#editform${postid}`)
  postbtn.onsubmit = (event) => {
    event.preventDefault()
    const postAfter = document.querySelector(`#editarea${postid}`).value;
    // update post body through api
    fetch(`edit/${postid}`, {
      method: "PUT",
      body: JSON.stringify({
        body: postAfter
      })
    })
    // live update post body
    post.innerHTML = postAfter;
    editbtn.style.display = "inline-block";
  }
}

function like(likebtn, postid) {
  let likeFlag
  let hearts = document.querySelector(`#likecount${postid}`)
  likecount = parseInt(hearts.textContent.slice(2))
  // when user likes a post
  if (likebtn.innerText === "Like") {
    likebtn.innerHTML = "Unlike"
    likeFlag = true
    likecount += 1
  }
  // when user unlikes a post
  else {
    likebtn.innerHTML = "Like"
    likeFlag = false
    likecount -= 1
  }
  // live update likecount
  hearts.innerText = "❤️ " + likecount
  // update likecount through api
  fetch(`like/${postid}`, {
    method: "PUT",
    body: JSON.stringify({
      flag: likeFlag
    })
  })
}

function follow(username) {
  let followFlag
  let followbtn = document.querySelector("#follow")
  if (followbtn.innerText === "Follow") {
    followbtn.innerText = "Unfollow"
    followFlag = true
  }
  else {
    followbtn.innerText = "Follow"
    followFlag = false
  }
  fetch(`follow/${username}`, {
    method: "PUT",
    body: JSON.stringify({
      flag: followFlag
    })
  })
}