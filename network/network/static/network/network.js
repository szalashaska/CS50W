// Variables to use
let NEXT;
let LAST;
let PREVIOUS;
let FIRST = 1;
let POSTS_VIEW = "all";
let CURRENT_PAGE = 1;
let FOLLOW_BUTTON_ACTION;
let LOGGED_USER;
let VIEWED_USER;

// Get pagination buttons and current page display
const nextButton = document.querySelector("#next-page");
const previousButton = document.querySelector("#previous-page");
const lastButton = document.querySelector("#last-page");
const firstButton = document.querySelector("#first-page");
const currentPageDisplay = document.querySelector("#current-page");
const numberOfPagesDisplay = document.querySelector("#number-of-pages");
const currentViewDisplay = document.querySelector("#current-view-indicator");

// Get following from navigation bar
const followingView = document.querySelector("#following-posts");

// Get follow button
const followButton = document.querySelector("#follow-btn");

// Add event listeners on pagination buttons, depending on current page
nextButton.addEventListener("click", nextPage);
previousButton.addEventListener("click", previousPage);
lastButton.addEventListener("click", lastPage);
firstButton.addEventListener("click", firstPage);

// Add event listner on follow button, depending on action
followButton.addEventListener("click", followButtonAction);

// After entering the page, load all posts, first page
load_posts(POSTS_VIEW, CURRENT_PAGE);
currentViewDisplay.innerHTML = "All Posts";

// When user is logged in
if (document.getElementById("username")) {
  // Update username variable
  loggedUserButton = document.getElementById("username");
  LOGGED_USER = loggedUserButton.innerHTML;

  // Add event listner to following page from navbar
  followingView.addEventListener("click", loadFollowingView);

  // Add event listener on username button
  loggedUserButton.addEventListener("click", () => {
    show_author(LOGGED_USER);
  });

  // When submitting post send it to the server, reload posts
  document.querySelector("#create-form").onsubmit = () => {
    send_post("create-body").then(() => {
      load_posts(POSTS_VIEW, FIRST);
    });
    return false;
  };
}

/*
 *
 ** Called functions **
 *
 */

// Saves or edits post
async function send_post(htmlElementId, postId) {
  // Get the content of the post
  const formField = document.getElementById(`${htmlElementId}`);
  // const formField = document.querySelector("#create-body");
  let content = formField.value;

  // Choose URL depending on action
  let URL;
  // Edit
  if (postId && postId !== "") {
    URL = `/post/${postId}`;
  }
  // Create
  else {
    URL = "/posts";
  }

  // Get CSRF token - Django documentation: "https://docs.djangoproject.com/en/4.0/ref/csrf/"
  const csrftoken = document.querySelector("[name=csrfmiddlewaretoken]").value;
  // Settings for POST method - headers from Django docks
  const settings = {
    method: "POST",
    headers: { "X-CSRFToken": csrftoken },
    mode: "same-origin",
    body: JSON.stringify({ body: content }),
  };

  // Send data to server
  const data = await fetch(URL, settings);
  const response = await data.json();

  // Log the respone and clear the form field
  console.log(response);
  formField.value = "";
  return;
}

async function get_posts(postView, pageNumber, userName) {
  // Gets posts from server
  URL = `/posts/${postView}?page=${pageNumber}&person=${userName}`;

  // Fetch and return data
  try {
    const response = await fetch(URL);
    const data = await response.json();

    return data;
  } catch (error) {
    console.log(error);
  }
}

async function like_or_unlike(postId, isLiked) {
  // Check action
  let action;
  if (isLiked === "true") {
    action = "unlike";
  } else {
    action = "like";
  }

  // URL, token and settings
  URL = `/post/${postId}`;
  const csrftoken = document.querySelector("[name=csrfmiddlewaretoken]").value;
  const settings = {
    method: "PUT",
    headers: { "X-CSRFToken": csrftoken },
    mode: "same-origin",
    body: JSON.stringify({ action: action }),
  };

  // Fetch data
  try {
    const data = await fetch(URL, settings);
    const response = await data.json();

    // Get current likes count from server and html elements
    const currentLikes = response.likes;
    const likeCount = document.getElementById(`like-count-${postId}`);
    const likeButton = document.getElementById(`like-btn-${postId}`);

    // Update count value
    likeCount.innerHTML = `${currentLikes}<i class="bi bi-hand-thumbs-up"></i>`;

    // Update button properties depending on action
    if (action === "like") {
      likeButton.innerHTML = "Unlike";
      likeButton.classList.remove("btn-primary");
      likeButton.classList.add("btn-danger");
      likeButton.dataset.likeaction = "true";
    } else {
      likeButton.innerHTML = "Like";
      likeButton.classList.remove("btn-danger");
      likeButton.classList.add("btn-primary");
      likeButton.dataset.likeaction = "false";
    }

    return;
  } catch (error) {
    // Log errors
    console.log(error);
  }
}

async function load_posts(postView, pageNumber, userName) {
  // Show or hide user view and create post form
  if (POSTS_VIEW === "userview") {
    document.querySelector("#user-view").style.display = "flex";
    document.querySelector("#create-view").style.display = "none";
  } else {
    document.querySelector("#user-view").style.display = "none";
    try {
      document.querySelector("#create-view").style.display = "block";
    } catch (err) {
      console.log("Create view was hidden by Django.");
    }
  }

  // Clear container before adding posts
  const postsContainer = document.querySelector("#posts-container");
  postsContainer.textContent = "";

  // Get posts from server, store it in variable
  const posts = await get_posts(postView, pageNumber, userName);

  // In followed view, check if user follows anyone
  if (posts.no_followed_users) {
    let container = document.createElement("div");
    container.innerHTML = "You are currently not following any user";
    postsContainer.append(container);
    return;
  }

  // Check if there are any posts to show
  if (posts.no_post_to_show) {
    let container = document.createElement("div");
    container.innerHTML = "No posts to show yet.";
    postsContainer.append(container);

    // Hide pagination
    document.getElementById("pagination").style.display = "none";
    return;
  }

  // Create posts and elements inside of it
  posts.content.forEach((post) => {
    // Html elements
    let container = document.createElement("div");
    let author = document.createElement("div");
    let timestamp = document.createElement("div");
    let content = document.createElement("div");
    let likes = document.createElement("div");
    let likeCount = document.createElement("div");

    // Add classes for CSS purpuses
    container.classList.add("post");
    author.classList.add("author");
    timestamp.classList.add("timestamp");
    content.classList.add("content");
    likes.classList.add("likes");

    // Assign timestamp
    timestamp.innerHTML = post.timestamp;

    // Asign author and load author's view after click event
    author.innerHTML = post.author;
    author.addEventListener("click", (e) => {
      show_author(e.target.innerHTML);
    });

    // Assign post content and post's id
    content.innerHTML = post.content;
    content.id = post.id;

    // Add elements to post container
    container.append(author, timestamp, content);

    // Assign like count for post
    likeCount.innerHTML = `${post.likes}<i class="bi bi-hand-thumbs-up"></i>`;
    likeCount.id = `like-count-${post.id}`;

    // Like Button - only for logged users
    if (LOGGED_USER) {
      // Create html elements
      let likeButton = document.createElement("button");

      // Add css class, dataset and button id
      likeButton.classList.add("btn");
      likeButton.dataset.likeaction = post.liked;
      likeButton.id = `like-btn-${post.id}`;

      // Check if post is liked by the user, assign action to button
      if (post.liked) {
        likeButton.innerHTML = "Unlike";
        likeButton.classList.add("btn-danger");
      } else {
        likeButton.innerHTML = "Like";
        likeButton.classList.add("btn-primary");
      }
      likeButton.addEventListener("click", () => {
        like_or_unlike(post.id, likeButton.dataset.likeaction);
      });

      likes.append(likeButton);
    }

    // Append like elements to post
    likes.append(likeCount);
    container.append(likes);

    // Create edit button, if user is the author of the post
    if (post.author === LOGGED_USER) {
      // Create html element and add class
      let edit = document.createElement("div");
      edit.classList.add("edit");
      edit.innerHTML = "Edit";

      // Add event listener
      edit.addEventListener("click", (e) => {
        // Send post id and edit element, to later replace it with save button.
        edit_post(post.id, e.target);
      });
      container.append(edit);
    }

    // Append post to posts view
    postsContainer.append(container);
  });

  // Pagination
  // Display current page and range
  if (posts.pages.number_of_pages > 1) {
    document.getElementById("pagination").style.display = "flex";
    currentPageDisplay.innerHTML = pageNumber;
    numberOfPagesDisplay.innerHTML = posts.pages.number_of_pages;
  } else {
    // Hide pagination if there are less than one page of posts
    document.getElementById("pagination").style.display = "none";
    return;
  }

  // Update pagination variables
  if (posts.pages.has_next) {
    nextButton.style.visibility = "visible";
    lastButton.style.visibility = "visible";
    NEXT = posts.pages.next;
    LAST = posts.pages.last;
  } else {
    nextButton.style.visibility = "hidden";
    lastButton.style.visibility = "hidden";
  }
  if (posts.pages.has_previous) {
    previousButton.style.visibility = "visible";
    firstButton.style.visibility = "visible";
    PREVIOUS = posts.pages.previous;
  } else {
    previousButton.style.visibility = "hidden";
    firstButton.style.visibility = "hidden";
  }
}

async function get_user(userName) {
  // Get user's info from server
  URL = `/user/${userName}`;

  // Fetch data and log error
  try {
    response = await fetch(URL);
    data = await response.json();

    return data;
  } catch (error) {
    console.log(error);
  }
}

async function follow_or_unfollow(userName, action) {
  // Make action
  URL = `user/${userName}`;

  // Prepare settings, headers, csrf token
  const csrftoken = document.querySelector("[name=csrfmiddlewaretoken]").value;
  const settings = {
    method: "PUT",
    headers: { "X-CSRFToken": csrftoken },
    mode: "same-origin",
    body: JSON.stringify({ action: action }),
  };

  // Fetch data and wait for response
  try {
    const data = await fetch(URL, settings);
    const response = await data.json();

    // From response get followed count
    const followedCount = response.followed;

    // Update value
    const followed = document.querySelector("#user-followers");
    followed.innerHTML = followedCount;

    // Assign action for follow button
    if (action === "follow") {
      followButton.innerHTML = "Unfollow";
      FOLLOW_BUTTON_ACTION = "unfollow";
    } else {
      followButton.innerHTML = "Follow";
      FOLLOW_BUTTON_ACTION = "follow";
    }
    return;
  } catch (error) {
    console.log(error);
  }
}

// Shows author page
async function show_author(userName) {
  // Set current view as userview and load users posts
  POSTS_VIEW = "userview";
  load_posts(POSTS_VIEW, FIRST, userName);

  // Update current view display
  currentViewDisplay.innerHTML = `${userName}'s Page`;

  // Get html elements
  const follows = document.querySelector("#user-follows");
  const followed = document.querySelector("#user-followers");
  const viewedUser = document.querySelector("#user-viewed");

  // Update viewed user variable, in order to pagination works corectly
  VIEWED_USER = userName;
  viewedUser.innerHTML = `<i class="bi bi-person"></i>${userName}`;

  // Fetch users data
  const userData = await get_user(userName);

  // Show follows statistics
  follows.innerHTML = userData.follows;
  followed.innerHTML = userData.followed;

  // Hide follow button for unlogged user and when user is visiting himself
  if (userData.is_the_same || LOGGED_USER === undefined) {
    followButton.style.display = "none";
    return;
  }

  // Set buttons dataset to username
  followButton.dataset.username = userName;

  // Assign action for follow button
  if (userData.is_followed) {
    followButton.innerHTML = "Unfollow";
    FOLLOW_BUTTON_ACTION = "unfollow";
  } else {
    followButton.innerHTML = "Follow";
    FOLLOW_BUTTON_ACTION = "follow";
  }
}

function edit_post(id, button) {
  // Get html elements
  let contentContainer = document.getElementById(`${id}`);
  let textArea = document.createElement("textarea");
  let savePost = document.createElement("button");
  let parentContainer = contentContainer.parentElement;

  // Add class
  textArea.classList.add("text-area");
  savePost.classList.add("save-changes", "btn", "btn-success");

  // Prepopulate text field
  textArea.value = contentContainer.innerHTML;
  textArea.id = `edit-${id}`;

  // Replace elements
  savePost.innerHTML = "Save";
  parentContainer.replaceChild(textArea, contentContainer);
  parentContainer.replaceChild(savePost, button);

  // To save post
  savePost.addEventListener("click", () => {
    // Get edited post content
    contentContainer.innerHTML = textArea.value;
    // Send edited post to server, replace it on website
    send_post(textArea.id, id).then(() => {
      parentContainer.replaceChild(contentContainer, textArea);
      parentContainer.replaceChild(button, savePost);
    });
  });
}

// Loads next and previous page after clicking a button
function nextPage() {
  if (POSTS_VIEW === "userview") {
    load_posts(POSTS_VIEW, NEXT, VIEWED_USER);
  } else {
    load_posts(POSTS_VIEW, NEXT);
  }
}

function previousPage() {
  if (POSTS_VIEW === "userview") {
    load_posts(POSTS_VIEW, PREVIOUS, VIEWED_USER);
  } else {
    load_posts(POSTS_VIEW, PREVIOUS);
  }
}

// Loads last and first page after clicking a button
function lastPage() {
  if (POSTS_VIEW === "userview") {
    load_posts(POSTS_VIEW, LAST, VIEWED_USER);
  } else {
    load_posts(POSTS_VIEW, LAST);
  }
}

function firstPage() {
  if (POSTS_VIEW === "userview") {
    load_posts(POSTS_VIEW, FIRST, VIEWED_USER);
  } else {
    load_posts(POSTS_VIEW, FIRST);
  }
}

// Follows or unfollows user
function followButtonAction() {
  const userName = followButton.dataset.username;
  follow_or_unfollow(userName, FOLLOW_BUTTON_ACTION);
}

// Loads following view
function loadFollowingView() {
  POSTS_VIEW = "following";
  load_posts(POSTS_VIEW, FIRST);
  currentViewDisplay.innerHTML = "Following Posts";
}
