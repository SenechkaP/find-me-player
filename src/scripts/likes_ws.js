const ws = new WebSocket("ws://" + window.location.host + "/ws/likes");

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    const postDiv = document.querySelector(`[data-post-id='${data.post_id}']`);
    if (!postDiv) return;

    const likeCount = postDiv.querySelector(".like-count");
    if (!likeCount) return;

    likeCount.textContent = `❤️ ${data.likes}`;
};
