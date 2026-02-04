/**
 * Pydo-IT landing helpers:
 * - Smooth scroll for anchor links
 * - Build a better CRM lead title before submit
 */

(function () {
  function ready(fn) {
    if (document.readyState !== 'loading') {
      fn();
    } else {
      document.addEventListener('DOMContentLoaded', fn);
    }
  }

  ready(function () {
    // Smooth scroll
    document.addEventListener('click', function (e) {
      var a = e.target.closest('a[href^="#"]');
      if (!a) return;
      var id = a.getAttribute('href');
      if (!id || id === '#') return;
      var target = document.querySelector(id);
      if (!target) return;
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      history.replaceState(null, '', id);
    });

    // Lead title from inputs
    var form = document.querySelector('form.pydoit-form[data-model_name="crm.lead"]');
    if (!form) return;

    form.addEventListener('submit', function () {
      var contact = (form.querySelector('input[name="contact_name"]') || {}).value || '';
      var company = (form.querySelector('input[name="partner_name"]') || {}).value || '';
      var email = (form.querySelector('input[name="email_from"]') || {}).value || '';

      var pieces = [];
      if (company.trim()) pieces.push(company.trim());
      if (contact.trim()) pieces.push(contact.trim());
      var title = pieces.length ? ('Landing Pydo-IT - ' + pieces.join(' / ')) : 'Lead desde Landing Pydo-IT';

      // If CRM requires name (opportunity title), set it
      var nameInput = form.querySelector('input[name="name"]');
      if (nameInput) {
        nameInput.value = title;
      } else {
        nameInput = document.createElement('input');
        nameInput.type = 'hidden';
        nameInput.name = 'name';
        nameInput.value = title;
        form.appendChild(nameInput);
      }

      // Add a bit of info to description (optional)
      var desc = form.querySelector('textarea[name="description"]');
      if (desc && email.trim()) {
        var marker = '\n\n---\nOrigen: Landing Pydo-IT\nEmail: ' + email.trim();
        if (desc.value.indexOf('Origen: Landing Pydo-IT') === -1) {
          desc.value += marker;
        }
      }
    });
  });
})();
