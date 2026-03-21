// ─── Active nav link ───
(function () {
  const path = window.location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.nav-links a').forEach(link => {
    const href = link.getAttribute('href');
    if (href === path || (path === '' && href === 'index.html')) {
      link.classList.add('active');
    }
  });
})();

// ─── Copy helpers ───
function copyText(text, btn) {
  navigator.clipboard.writeText(text).then(() => {
    if (!btn) return;
    const orig = btn.textContent;
    btn.textContent = '✓ copied';
    btn.style.color = '#059669';
    setTimeout(() => { btn.textContent = orig; btn.style.color = ''; }, 1800);
  });
}

// Nav chip: copy install command
const chip = document.querySelector('.install-chip');
if (chip) {
  chip.addEventListener('click', () => {
    navigator.clipboard.writeText('npm install -g @axiomcm/cli').then(() => {
      const orig = chip.innerHTML;
      chip.innerHTML = '✓ Copied!';
      setTimeout(() => chip.innerHTML = orig, 1800);
    });
  });
}

// ─── Agent category filter (agents.html) ───
window.filterCategory = function (btn, cat) {
  document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  document.querySelectorAll('.agent-card').forEach(card => {
    card.style.display = (!cat || card.dataset.category === cat) ? '' : 'none';
  });
  // Update count
  const visible = document.querySelectorAll('.agent-card:not([style*="none"])').length;
  const counter = document.getElementById('agent-count');
  if (counter) counter.textContent = visible;
};

// ─── Docs sidebar: highlight active section on scroll ───
if (document.querySelector('.docs-sidebar')) {
  const sections = document.querySelectorAll('.docs-section');
  const links = document.querySelectorAll('.docs-sidebar a');

  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        links.forEach(l => l.classList.remove('active'));
        const active = document.querySelector(`.docs-sidebar a[href="#${entry.target.id}"]`);
        if (active) active.classList.add('active');
      }
    });
  }, { rootMargin: '-20% 0px -70% 0px' });

  sections.forEach(s => observer.observe(s));
}

// ─── Waitlist form: Formspree + success message ───
const waitlistForm = document.getElementById('waitlist-form');
if (waitlistForm) {
  waitlistForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = waitlistForm.querySelector('button[type="submit"]');
    const success = document.getElementById('form-success');
    btn.disabled = true;
    btn.textContent = 'Sending…';
    try {
      const formData = new FormData(waitlistForm);
      const payload = {};
      formData.forEach((value, key) => { payload[key] = value; });
      const res = await fetch(waitlistForm.action, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
        body: JSON.stringify(payload),
      });
      const data = await res.json().catch(() => ({}));
      if (res.ok && (data.success === 'true' || data.success === true)) {
        waitlistForm.style.display = 'none';
        if (success) success.style.display = 'block';
      } else {
        btn.textContent = 'Try again';
        btn.disabled = false;
      }
    } catch {
      btn.textContent = 'Try again';
      btn.disabled = false;
    }
  });
}
