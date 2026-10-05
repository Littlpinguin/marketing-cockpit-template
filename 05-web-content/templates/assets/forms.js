/* ==========================================================================
   forms.js · validation and sending of capture forms (optional engine)
   --------------------------------------------------------------------------
   Contract (attributes read in the markup):
     form[data-form]                 a form this engine handles. Without
                                     JavaScript it posts natively to its
                                     action: the page keeps working.
       data-error-required           message for an empty required field
       data-error-email              message for a malformed email
       data-error-consent            message for an unticked consent box
       data-msg-success              confirmation shown after sending
       data-msg-failure              shown when sending fails
       data-msg-unwired              added after the success message when
                                     the action is still a {{PLACEHOLDER}}
                                     or empty (demonstration: nothing sent)
     form[data-demo]                 written on load when the action is
                                     still a {{PLACEHOLDER}} or empty:
                                     submissions are demonstrations, never
                                     sent, counted by tracking.js under
                                     form_demo_submit instead of the lead
     .hp input                       honeypot: filled means a robot; the form
                                     pretends success and sends nothing
     [data-error-for="<name>"]       error message of a field (else the
                                     element whose id is <field id>-error)
     [data-form-fields]              hidden once sent
     [data-form-status]              live region (role="status"), present
                                     from the start, receives the messages
   Behaviour: on submit, every required field is checked; invalid ones get
   aria-invalid="true" and their message, focus goes to the first one, and
   the form carries data-invalid (tracking.js then counts nothing). A valid
   form is sent with fetch (POST, FormData); if fetch fails, the native
   submission takes over. A demonstration form (data-demo) sends nothing
   over the network and shows the success state at once. Never a pre-ticked
   box, never a placeholder used as a label: that is the markup's job.
   ========================================================================== */
(function () {
  'use strict';
  if (window.__landingForms) return;
  window.__landingForms = true;

  var EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;

  function errorBox(form, field) {
    return form.querySelector('[data-error-for="' + field.name + '"]') ||
      (field.id ? document.getElementById(field.id + '-error') : null);
  }

  function setError(form, field, message) {
    var box = errorBox(form, field);
    if (message) {
      field.setAttribute('aria-invalid', 'true');
      if (box) { box.textContent = message; box.hidden = false; }
    } else {
      field.removeAttribute('aria-invalid');
      if (box) { box.textContent = ''; box.hidden = true; }
    }
  }

  function messageFor(form, field) {
    if (field.type === 'checkbox') {
      return field.required && !field.checked
        ? (form.getAttribute('data-error-consent') || form.getAttribute('data-error-required') || '')
        : '';
    }
    var value = (field.value || '').trim();
    if (field.required && !value) return form.getAttribute('data-error-required') || '';
    if (value && field.type === 'email' && !EMAIL.test(value)) return form.getAttribute('data-error-email') || '';
    return '';
  }

  function checkField(form, field) {
    var message = messageFor(form, field);
    setError(form, field, message);
    return message;
  }

  function check(form) {
    var first = null;
    var fields = form.querySelectorAll('input, select, textarea');
    Array.prototype.forEach.call(fields, function (field) {
      if (field.closest('.hp') || field.type === 'hidden' || field.disabled) return;
      if (checkField(form, field) && !first) first = field;
    });
    return first;
  }

  function status(form, text) {
    var box = form.querySelector('[data-form-status]');
    if (box) box.textContent = text || '';
  }

  function done(form, demo) {
    var fields = form.querySelector('[data-form-fields]');
    if (fields) fields.hidden = true;
    var text = form.getAttribute('data-msg-success') || '';
    if (demo && form.getAttribute('data-msg-unwired')) text += (text ? ' ' : '') + form.getAttribute('data-msg-unwired');
    status(form, text);
  }

  // The endpoint is still a {{PLACEHOLDER}} (or missing): a demonstration.
  function unwired(form) {
    var action = form.getAttribute('action') || '';
    return !action || /\{\{/.test(action);
  }

  document.querySelectorAll('form[data-form]').forEach(function (form) {
    form.setAttribute('novalidate', '');
    if (unwired(form)) form.setAttribute('data-demo', '');
    form.addEventListener('submit', function (e) {
      var trap = form.querySelector('.hp input');
      if (trap && trap.value) {
        e.preventDefault();
        form.setAttribute('data-invalid', '');
        done(form);
        return;
      }
      var first = check(form);
      if (first) {
        e.preventDefault();
        form.setAttribute('data-invalid', '');
        first.focus();
        return;
      }
      form.removeAttribute('data-invalid');
      if (unwired(form)) {
        // Nothing leaves the page; tracking.js counts form_demo_submit.
        e.preventDefault();
        form.setAttribute('data-demo', '');
        done(form, true);
        return;
      }
      var action = form.getAttribute('action');
      if (!window.fetch || !window.FormData) return;   // native submission
      e.preventDefault();
      status(form, '');
      window.fetch(action, { method: 'POST', body: new FormData(form) })
        .then(function (r) {
          if (!r.ok && r.type !== 'opaque') throw new Error(String(r.status));
          done(form);
        })
        .catch(function () {
          status(form, form.getAttribute('data-msg-failure'));
          HTMLFormElement.prototype.submit.call(form);
        });
    });
    // Once flagged, a field is re-checked as the visitor corrects it.
    form.addEventListener('input', function (e) {
      if (e.target.getAttribute('aria-invalid') === 'true') checkField(form, e.target);
    });
    form.addEventListener('change', function (e) {
      if (e.target.getAttribute('aria-invalid') === 'true') checkField(form, e.target);
    });
  });
})();
