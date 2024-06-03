$("#post-upload-form .file-input").change((e) => {
  if (e.target.files.length == 0) return;
  $("#post-upload-form span.file-label").text(e.target.files[0].name);
});
