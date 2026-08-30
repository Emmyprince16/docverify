window.addEventListener('scroll', () => {
    const navbar = document.getElementById('navbar');
    if (window.scrollY > 10) {
        navbar.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.3)';
    } else {
        navbar.style.boxShadow = 'none';
    }
});

document.querySelectorAll('.file-drop input[type="file"]').forEach((input) => {
    input.addEventListener('change', () => {
        if (input.files.length > 0) {
            const label = input.previousElementSibling;
            label.textContent = input.files[0].name;
        }
    });
});