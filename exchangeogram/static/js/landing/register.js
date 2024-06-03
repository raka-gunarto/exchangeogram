$('input[name="email"]').focusout((e) => {
  const elem = $(e.target);

  // check if email is already being used
  $.ajax({
    url: "/app/profile/check",
    type: "GET",
    data: {
      type: "email",
      val: `${elem.val()}`,
    },
    dataType: "json",
    success: (response) => {
      if (response.data == true) {
        // email already exists
        $("#email-help").text("Email already exists!").show();
        elem.addClass("is-danger");
        elem.removeClass("is-success");
      } else {
        // email does not exist, all is well
        $("#email-help").hide();
        elem.addClass("is-success");
        elem.removeClass("is-danger");
      }
    },
  });
});

$('input[name="username"]').focusout((e) => {
  const elem = $(e.target);

  // check if email is already being used
  $.ajax({
    url: "/app/profile/check",
    type: "GET",
    data: {
      type: "username",
      val: `${elem.val()}`,
    },
    dataType: "json",
    success: (response) => {
      if (response.data == true) {
        // username already exists
        $("#username-help").text("Email already exists!").show();
        elem.addClass("is-danger").removeClass("is-success");
      } else {
        // username does not exist, all is well
        $("#username-help").hide();
        elem.addClass("is-success").removeClass("is-danger");
      }
    },
  });
});

$('input[name="password"]').focusout((e) => {
  const elem = $(e.target);
  const val = elem.val();
  if (val.length < 8) {
    elem.addClass("is-danger").removeClass("is-success");
    $("#password-help")
      .text("Password must be at least 8 characters long!")
      .show();
  } else {
    elem.removeClass("is-danger").addClass("is-success");
    $("#password-help").hide();
  }

  // trigger confirm password check after password is changed
  $('input[name="passwordconfirm"]').focusout();
});

$('input[name="passwordconfirm"]').focusout((e) => {
  const passval = $('input[name="password"]').val();
  const val = $(e.target).val();
  const elem = $(e.target);

  if (val !== passval) {
    elem.addClass("is-danger").removeClass("is-success");
    $("#passwordconfirm-help").text("Passwords do not match!").show();
  } else {
    elem.addClass("is-success").removeClass("is-danger");
    $("#passwordconfirm-help").hide();
  }
});

function checkFormValidity() {
  const inputs = $("#register-form input");
  for (let input of inputs) if ($(input).hasClass("is-danger")) return false;
  return true;
}

$("#register-form input").focusout(() => {
  if (!checkFormValidity())
    return $("#register-form > button").attr("disabled", true);
  $("#register-form > button").removeAttr("disabled");
});

$("#register-form > button").click((e) => {
  if (!checkFormValidity())
    return $("#register-form > button").attr("disabled", true);

  const form = $("#register-form");
  if (form[0].checkValidity()) {
    $(e.target).addClass("is-loading").attr("disabled", true);
    form.submit();
  } else form.find("input").each((idx, input) => input.reportValidity());
});
