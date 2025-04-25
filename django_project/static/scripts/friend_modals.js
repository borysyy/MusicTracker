$(document).on("show.bs.modal", "#friendRequest", event => {
    const username = $(event.relatedTarget).data("username");
    $(".modal-body").data("username", username);
    $(".modal-body .request-username").text("Request to add " + username);
});

$(document).on("show.bs.modal", "#cancelFriendRequest", event => {
    const username = $(event.relatedTarget).data("username");
    $(".modal-body").data("username", username);
    $(".modal-body .request-username").text("Cancel friend request to " + username);
});

$(document).on("show.bs.modal", "#acceptRejectRequest", event => {
    const username = $(event.relatedTarget).data("username");
    $(".modal-body").data("username", username);
    $(".modal-body .request-username").text("Accept or reject friend request from " + username);
});

$(document).on("show.bs.modal", "#removeFriend", event => {
    const username = $(event.relatedTarget).data("username");
    $(".modal-body").data("username", username);
    $(".modal-body .request-username").text("Remove " + username + " as a friend");
});
