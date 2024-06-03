const notifTemplate = $(`
    <div class="dropdown-item">
        <span class="icon">
            <i class="mdi mdi-heart"></i>
        </span>
        <span id="notif-text"></span>
    </div>
`);

const noNotifTemplate = $(`
    <div class="dropdown-item">
        You have no notifications :D
    </div>
`);

function getNotifs() {
  const notifContainer = $("#notifications");
  notifContainer.empty();

  $.ajax({
    url: "/app/notifications",
    method: "GET",
    dataType: "json",
    success: (response) => {
      if (response.length == 0)
        return notifContainer.append(noNotifTemplate.clone());
      for (let notif of response) {
        let cnotif = notifTemplate.clone();
        cnotif.find("#notif-text").text(notif.message);
        notifContainer.append(cnotif);
        notifContainer.append($('<hr class="dropdown-divider">'))
      }
    },
  });
}
setInterval(5000, getNotifs);
getNotifs();
