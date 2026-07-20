document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('[data-email-user]').forEach(function (el) {
    var user = el.getAttribute('data-email-user');
    var domain = el.getAttribute('data-email-domain');
    if (user && domain) {
      el.setAttribute('href', 'mailto:' + user + '@' + domain);
    }
  });
});
