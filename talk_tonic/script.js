const observer = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
      }
    });
  },
  { threshold: 0.12 }
);

document.querySelectorAll('.reveal').forEach((el) => observer.observe(el));

const form = document.getElementById('contactForm');
const statusBox = document.getElementById('formStatus');

if (form && statusBox) {
  form.addEventListener('submit', function (event) {
    event.preventDefault();

    const name = document.getElementById('name').value.trim();
    const email = document.getElementById('email').value.trim();
    const message = document.getElementById('message').value.trim();

    if (!name || !email || !message) {
      statusBox.textContent = 'Please fill in all fields before sending.';
      statusBox.style.color = '#b45309';
      return;
    }

    statusBox.textContent = 'Thanks! Your message has been sent successfully.';
    statusBox.style.color = '#166534';
    form.reset();
  });
}
