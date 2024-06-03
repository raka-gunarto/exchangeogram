var offset = 0;
const limit = 20;

const template = $(`
  <div class="card mb-4">
    <header class="card-header" style="border-bottom: 1px solid #dfdfdf">
      <a class="card-header-title"></a>
    </header>
    <div class="card-image" style="border-bottom: 1px solid #dfdfdf">
      <figure class="image is-4by5">
        <img id="post-image"></img>
      </figure>
    </div>
    <div class="card-content px-3 pt-2">
      <div class="level mb-2">
        <div class="level-left">
          <span class="icon mr-2 is-clickable like-btn">
            <i class="mdi mdi-24px mdi-heart-outline"></i>
          </span>
          <span class="icon">
            <i class="mdi mdi-24px mdi-link-variant"></i>
          </span>
        </div>
      </div>
      <div id="likes">
        <p class="subtitle is-6"></p>
      </div>
      <p class="title is-6" id="post-author"></p>
      <p id="post-caption"></p>
    </div>
  </div>
`);

$("body").on("click", "span.like-btn", function () {
  let post = $(this).closest("div.card");
  let postID = post.data("id");
  $.ajax({
    url: `/app/post/${postID}/like`,
    method: "POST",
    success: (resp) => {
      post
        .find("span.like-btn")
        .addClass("has-text-danger")
        .removeClass("is-clickable")
        .removeClass("like-btn")
        .find("i.mdi-heart-outline")
        .removeClass("mdi-heart-outline")
        .addClass("mdi-heart")
    },
  });
});
$(document).ready(() => {
  // run once
  $.ajax({
    url: "/app/feed",
    type: "GET",
    data: {
      limit: limit,
      offset: offset,
    },
    dataType: "json",
    success: (response) => {
      offset += response.length;
      for (let post of response) {
        let cpost = template.clone();
        cpost
          .find("#post-image")
          .attr("src", `/app/posts/${post.user_id}/${post.imgname}`);
        cpost.attr("data-id", post.id);
        cpost.find("#post-caption").text(post.caption);
        cpost.find("#post-author").text(post.user);
        cpost.find(".card-header-title").attr("href", `/u/${post.user_id}`);
        cpost.find(".card-header-title").text(post.user);
        cpost
          .find("#likes")
          .text(`${post.likes ? post.likes.length : 0} likes`);
        for (let like of post.likes) {
          if (like.user_id == current_id)
            cpost
              .find(".like-btn")
              .removeClass("is-clickable")
              .removeClass("like-btn")
              .addClass("has-text-danger")
              .find("i")
              .removeClass("mdi-heart-outline")
              .addClass("mdi-heart");
        }
        $("#feed").append(cpost);
      }
    },
  });
});
$("#load-more-posts").click(() => {
  $.ajax({
    url: "/app/feed",
    type: "GET",
    data: {
      limit: limit,
      offset: offset,
    },
    dataType: "json",
    success: (response) => {
      if (response.length == 0) return $("#load-more-posts").remove();
      offset += response.length;
      for (let post of response) {
        let cpost = template.clone();
        cpost
          .find("#post-image")
          .attr("src", `/app/posts/${post.user_id}/${post.imgname}`);
        cpost.attr("data-id", post.id);
        cpost.find("#post-caption").text(post.caption);
        cpost.find("#post-author").text(post.user);
        cpost.find(".card-header-title").attr("href", `/u/${post.user_id}`);
        cpost.find(".card-header-title").text(post.user);
        cpost
          .find("#likes")
          .text(`${post.likes ? post.likes.length : 0} likes`);
        for (let like of post.likes) {
          if (like.user_id == current_id)
            cpost
              .find(".like-btn")
              .removeClass("is-clickable")
              .removeClass("like-btn")
              .addClass("has-text-danger")
              .find("i")
              .removeClass("mdi-heart-outline")
              .addClass("mdi-heart");
        }
        $("#feed").append(cpost);
      }
    },
  });
});
